# main.py
import os, io, json, tempfile, datetime, asyncio
from typing import Dict, List
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dotenv import load_dotenv

from database import Base, engine, SessionLocal
from orm_models import Quiz, Attempt
from schemas import GenerateRequest, HistoryItem, HistoryResponse
from scraper import scrape_wikipedia
from llm_quiz_generator import generate_quiz_payload  # <- ensure it accepts count=
from utils import is_wikipedia_url
from pdf_generator import build_exam_pdf

load_dotenv()

app = FastAPI(title="AI Wiki Quiz Generator", version="1.1.0")

# --- CORS ------------------------------------------------------------
# Use explicit origins if you need credentials; don't use "*" with allow_credentials=True
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # add your deployed frontend:
    "https://ai-quiz-generator-jade.vercel.app",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# --- DB bootstrap ----------------------------------------------------
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Simple in-memory proctor hub (no DB) ----------------------------
# session_id (int/str) -> set[WebSocket]
proctor_rooms: Dict[str, set] = defaultdict(set)
room_lock = asyncio.Lock()

async def ws_broadcast(session_id: str, message: dict):
    data = json.dumps({"type": "event", "event": message})
    async with room_lock:
        dead = []
        for ws in list(proctor_rooms[session_id]):
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            proctor_rooms[session_id].discard(ws)

# --- Health ----------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# --- Quiz generation -------------------------------------------------
@app.post("/generate_quiz")
def generate_quiz(
    req: GenerateRequest,
    db: Session = Depends(get_db),
    count: int = Query(10, ge=5, le=50)  # reads ?count= from frontend
):
    url = str(req.url)
    if not is_wikipedia_url(url):
        raise HTTPException(status_code=400, detail="Only Wikipedia article URLs are accepted.")

    use_cache = os.getenv("ENABLE_URL_CACHE", "true").lower() == "true"
    existing = db.query(Quiz).filter(Quiz.url == url).one_or_none()

    # serve cached if enough questions and not forcing refresh
    if use_cache and existing and not req.force_refresh:
        stored = json.loads(existing.full_quiz_data)
        if len(stored.get("quiz") or []) >= count:
            stored["quiz"] = stored["quiz"][:count]
            stored["id"] = existing.id
            return stored

    title, cleaned_text, sections, raw_html = scrape_wikipedia(url)
    if not cleaned_text or len(cleaned_text) < 200:
        raise HTTPException(status_code=422, detail="Article content too short or could not be parsed.")

    # IMPORTANT: your llm_quiz_generator.generate_quiz_payload must accept count and try to produce up to that many.
    payload = generate_quiz_payload(
        url=url,
        title=title,
        article_text=cleaned_text,
        sections=sections,
        count=count,  # pass through
    )

    payload["quiz"] = (payload.get("quiz") or [])[:count]
    payload["sections"] = payload.get("sections") or sections

    if not existing:
        record = Quiz(
            url=url, title=title,
            scraped_html=raw_html, scraped_text=cleaned_text,
            full_quiz_data=json.dumps(payload, ensure_ascii=False),
        )
        db.add(record)
        try:
            db.commit(); db.refresh(record)
        except IntegrityError:
            db.rollback()
            record = db.query(Quiz).filter(Quiz.url == url).one()
    else:
        existing.title = title
        existing.scraped_html = raw_html
        existing.scraped_text = cleaned_text
        existing.full_quiz_data = json.dumps(payload, ensure_ascii=False)
        db.commit(); db.refresh(existing)
        record = existing

    payload["id"] = record.id
    return payload

# --- History / fetch -------------------------------------------------
@app.get("/history", response_model=HistoryResponse)
def history(db: Session = Depends(get_db)):
    rows = db.query(Quiz).order_by(Quiz.date_generated.desc()).all()
    return HistoryResponse(items=[
        HistoryItem(
            id=r.id, url=r.url, title=r.title,
            date_generated=r.date_generated.isoformat() if r.date_generated else ""
        ) for r in rows
    ])

@app.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    r = db.query(Quiz).filter(Quiz.id == quiz_id).one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Quiz not found")
    data = json.loads(r.full_quiz_data); data["id"] = r.id
    return data

# --- Submit attempt --------------------------------------------------
@app.post("/submit_attempt/{quiz_id}")
def submit_attempt(quiz_id: int, payload: dict, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    answers = payload.get("answers", {})
    score = int(payload.get("score", 0))
    time_taken = int(payload.get("time_taken_seconds", 0))
    total_time = int(payload.get("total_time", 0))

    attempt = Attempt(
        quiz_id=quiz_id,
        submitted_at=datetime.datetime.utcnow(),
        time_taken_seconds=time_taken,
        score=score,
        answers_json=json.dumps(answers),
    )
    # If your Attempt model has total_time / total_questions columns, set them here:
    # attempt.total_time = total_time
    # attempt.total_questions = int(payload.get("total_questions", 0))

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return {"saved": True, "attempt_id": attempt.id}

# --- Export PDF ------------------------------------------------------
@app.post("/export_pdf/{quiz_id}")
def export_pdf(quiz_id: int, payload: dict, db: Session = Depends(get_db)):
    r = db.query(Quiz).filter(Quiz.id == quiz_id).one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Quiz not found")
    q = json.loads(r.full_quiz_data); q["id"] = r.id

    count = int(payload.get("count", len(q["quiz"])))
    q["quiz"] = q["quiz"][:count]
    user = payload.get("user", "Anonymous")
    duration_str = payload.get("duration_str", "—")

    filename = f"quiz_{quiz_id}.pdf"
    tmp_path = os.path.join(tempfile.gettempdir(), filename)
    build_exam_pdf(tmp_path, "DeepKlarity AI Exam", user, q.get("title","Quiz"), q, duration_str)

    with open(tmp_path, "rb") as f:
        pdf_bytes = f.read()

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

# # --- Proctor events (no DB) -----------------------------------------
# @app.post("/session/{session_id}/event")
# async def session_event(session_id: str, payload: dict):
#     """
#     Called from frontend on tab-blur/fs-exit/etc.
#     payload: {"type": "...", "meta": {...}}
#     """
#     event = {
#         "at": datetime.datetime.utcnow().isoformat(),
#         "type": payload.get("type", "info"),
#         "meta": payload.get("meta", {}),
#     }
#     asyncio.create_task(ws_broadcast(str(session_id), event))
#     return {"ok": True}

# @app.websocket("/ws/proctor/{session_id}")
# async def ws_proctor(session_id: str, ws: WebSocket):
#     # Accept from any origin (Render/localhost)
#     await ws.accept()
#     async with room_lock:
#         proctor_rooms[str(session_id)].add(ws)
#     try:
#         # keepalive loop; ignore messages from client
#         while True:
#             await ws.receive_text()
#     except WebSocketDisconnect:
#         async with room_lock:
#             proctor_rooms[str(session_id)].discard(ws)
#     except Exception:
#         async with room_lock:
#             proctor_rooms[str(session_id)].discard(ws)
