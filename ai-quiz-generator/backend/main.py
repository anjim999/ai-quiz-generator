# main.py
import json, os, io
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime, timezone
import tempfile

# --- NEW (top) ---
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
import json

class WSManager:
    def __init__(self):
        self.active: Dict[int, List[WebSocket]] = {}

    async def connect(self, session_id: int, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(session_id, []).append(ws)

    def disconnect(self, session_id: int, ws: WebSocket):
        if session_id in self.active and ws in self.active[session_id]:
            self.active[session_id].remove(ws)

    async def broadcast(self, session_id: int, event: dict):
        for ws in self.active.get(session_id, []):
            try:
                await ws.send_text(json.dumps(event))
            except Exception:
                pass

ws_manager = WSManager()


from database import Base, engine, SessionLocal
from orm_models import Quiz, Attempt
from schemas import GenerateRequest, HistoryItem, HistoryResponse
from scraper import scrape_wikipedia
from llm_quiz_generator import generate_quiz_payload
from utils import is_wikipedia_url
from pdf_generator import build_exam_pdf

load_dotenv()

app = FastAPI(title="AI Wiki Quiz Generator", version="1.1.0")

# Open CORS (frontend localhost/Vercel, etc.)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://ai-quiz-generator-jade.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ✅ use allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate_quiz")
def generate_quiz(
    req: GenerateRequest,
    db: Session = Depends(get_db),
    count: int = Query(10, ge=5, le=50)   # ✅ reads ?count= from frontend URL
):
    url = str(req.url)

    print("Generating quiz for URL:", url, "with count:", count)

    if not is_wikipedia_url(url):
        raise HTTPException(status_code=400, detail="Only Wikipedia article URLs are accepted.")

    use_cache = os.getenv("ENABLE_URL_CACHE", "true").lower() == "true"
    existing = db.query(Quiz).filter(Quiz.url == url).one_or_none()

    # ✅ Return cached quiz if exists & not forcing refresh
    if use_cache and existing and not req.force_refresh:
        stored = json.loads(existing.full_quiz_data)
        stored_count = len(stored.get("quiz", []))

        # ✅ Enough questions stored → slice and return
        if stored_count >= count:
            stored["quiz"] = stored["quiz"][:count]
            stored["id"] = existing.id
            return stored
        # ❌ Not enough → regenerate

    # ✅ Fresh scrape and LLM call
    title, cleaned_text, sections, raw_html = scrape_wikipedia(url)
    if not cleaned_text or len(cleaned_text) < 200:
        raise HTTPException(status_code=422, detail="Article content too short or could not be parsed.")

    payload = generate_quiz_payload(
    url=url,
    title=title,
    article_text=cleaned_text,
    sections=sections,
    count=count   # ✅ pass count from frontend
)


    # ✅ Trim to requested question count
    payload["quiz"] = (payload.get("quiz") or [])[:count]
    payload["sections"] = payload.get("sections") or sections

    # ✅ Insert or update DB
    if not existing:
        record = Quiz(
            url=url, title=title,
            scraped_html=raw_html, scraped_text=cleaned_text,
            full_quiz_data=json.dumps(payload, ensure_ascii=False)
        )
        db.add(record)
        db.commit()
        db.refresh(record)
    else:
        existing.title = title
        existing.scraped_html = raw_html
        existing.scraped_text = cleaned_text
        existing.full_quiz_data = json.dumps(payload, ensure_ascii=False)
        db.commit()
        db.refresh(existing)
        record = existing

    payload["id"] = record.id
    return payload

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

@app.post("/submit_attempt/{quiz_id}")
def submit_attempt(quiz_id: int, payload: dict, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    answers = payload.get("answers", {})
    score = int(payload.get("score", 0))

    # ✅ use time_taken_seconds coming from frontend
    time_taken = int(payload.get("time_taken_seconds", 0))

    # ✅ also capture total allotted time if sent
    total_time = int(payload.get("total_time", 0))

    attempt = Attempt(
        quiz_id=quiz_id,
        time_taken_seconds=time_taken,  # ✅ store actual time taken
        total_time=total_time,
        score=score,
        answers_json=json.dumps(answers),
        # total_questions=len(quiz.quiz) if quiz.quiz else 0,
        # set submission timestamp so submitted_at is not NULL
        submitted_at=datetime.now(timezone.utc),
    )

    print(attempt)

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return {"saved": True, "attempt_id": attempt.id}

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

    # ✅ Cross-platform temp directory
    import tempfile, os
    tmp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, filename)

    # ✅ Build PDF
    build_exam_pdf(tmp_path, "DeepKlarity AI Exam", user, q.get("title","Quiz"), q, duration_str)

    with open(tmp_path, "rb") as f:
        pdf_bytes = f.read()

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

from fastapi import WebSocket

# Start a session (called when user enters QuizMode)
@app.post("/session/start/{quiz_id}")
def start_session(
    quiz_id: int,
    payload: dict,
    db: Session = Depends(get_db)
):
    q = db.query(Quiz).filter(Quiz.id == quiz_id).one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Quiz not found")
    total_questions = int(payload.get("total_questions", 0)) or len(json.loads(q.full_quiz_data).get("quiz", []))
    user_name = payload.get("user_name", "Candidate")

    s = ExamSession(quiz_id=quiz_id, total_questions=total_questions, user_name=user_name)
    db.add(s); db.commit(); db.refresh(s)
    return {"session_id": s.id}

# Log proctor events (tab/visibility/fs) and broadcast to dashboard
@app.post("/session/{session_id}/event")
async def add_event(session_id: int, payload: dict, db: Session = Depends(get_db)):
    etype = payload.get("type") or "unknown"
    meta = json.dumps(payload.get("meta") or {})
    ev = ProctorEvent(session_id=session_id, type=etype, meta=meta)
    db.add(ev); db.commit()
    await ws_manager.broadcast(session_id, {"type": "event", "event": {"type": etype, "meta": payload.get("meta"), "at": ev.at.isoformat()}})
    return {"saved": True}

# Finish session (submit answers) — replaces /submit_attempt
@app.post("/session/{session_id}/submit")
def finish_session(session_id: int, payload: dict, db: Session = Depends(get_db)):
    s = db.query(ExamSession).filter(ExamSession.id == session_id).one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    quiz = db.query(Quiz).filter(Quiz.id == s.quiz_id).one()
    data = json.loads(quiz.full_quiz_data)

    answers_map = payload.get("answers", {})            # { "0": 2, "1": 1 ... }
    total_time = int(payload.get("time_taken_seconds", 0))
    requested_total = int(payload.get("total_time", 0))
    # score
    score = 0
    for i, q in enumerate(data.get("quiz", [])):
        ans_idx = answers_map.get(str(i)) if isinstance(answers_map, dict) else answers_map.get(i)
        if ans_idx is not None and q["options"][int(ans_idx)] == q["answer"]:
            score += 1

    s.finished_at = func.now()
    s.time_taken_seconds = total_time or None
    s.score = score
    s.auto_submitted = bool(payload.get("auto", False))
    db.commit()

    # also keep previous Attempt table in sync (optional)
    a = Attempt(
        quiz_id=s.quiz_id,
        submitted_at=None,
        time_taken_seconds=total_time or requested_total,
        score=score,
        answers_json=json.dumps(answers_map)
    )
    db.add(a); db.commit()

    return {"ok": True, "score": score, "total": len(data.get("quiz", []))}

# WebSocket for proctors to watch live events for a session
@app.websocket("/ws/proctor/{session_id}")
async def proctor_ws(websocket: WebSocket, session_id: int):
    await ws_manager.connect(session_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # keep alive, ignore client messages
    except WebSocketDisconnect:
        ws_manager.disconnect(session_id, websocket)