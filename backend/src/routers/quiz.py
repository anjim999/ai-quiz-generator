"""
Quiz Router
===========
Handles quiz generation, history, attempts, and PDF export.

Endpoints:
- GET /api/quiz/health - Health check
- POST /api/quiz/generate_quiz - Generate quiz from Wikipedia URL
- GET /api/quiz/history - Get user's quiz history
- GET /api/quiz/quiz/{quiz_id} - Get a specific quiz
- POST /api/quiz/submit_attempt/{quiz_id} - Submit quiz attempt
- POST /api/quiz/export_pdf/{quiz_id} - Export quiz as PDF
"""

import json
import logging
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse

from src.core import settings
from src.core.exceptions import BadRequestException, NotFoundException, UnprocessableEntityException
from src.middleware import get_current_user, CurrentUser
from src.models.quiz import (
    GenerateQuizRequest, SubmitAttemptRequest, ExportPdfRequest,
    QuizData, HistoryResponse, HistoryItem, SubmitAttemptResponse, HealthResponse
)
from src.db.queries.quizzes import (
    get_quiz_by_url_and_user, get_quiz_by_id, get_quiz_by_id_and_user,
    create_quiz, update_quiz, get_user_quiz_history, create_quiz_attempt
)
from src.services import scrape_wikipedia, generate_quiz_payload, build_exam_pdf
from src.utils import is_wikipedia_url

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quiz", tags=["Quiz"])


# ===========================================
# Health Check (Public)
# ===========================================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check if the quiz service is running."
)
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


# ===========================================
# Generate Quiz (Protected)
# ===========================================

@router.post(
    "/generate_quiz",
    response_model=QuizData,
    summary="Generate Quiz",
    description="Generate a quiz from a Wikipedia article URL."
)
async def generate_quiz(
    request: GenerateQuizRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    count: int = Query(default=10, ge=1, le=50, description="Number of questions")
):
    """
    Generate a quiz from a Wikipedia article.
    
    This endpoint:
    1. Validates the Wikipedia URL
    2. Checks cache for existing quiz (optional)
    3. Scrapes the Wikipedia article using BeautifulSoup
    4. Generates quiz using LangChain + Gemini
    5. Stores the quiz in the database
    6. Returns the complete quiz data
    """
    try:
        url = request.url
        force_refresh = request.force_refresh
        user_id = user.user_id
        
        # Validate Wikipedia URL
        if not is_wikipedia_url(url):
            raise BadRequestException("Only Wikipedia article URLs are accepted.")
        
        # Check cache
        use_cache = settings.ENABLE_URL_CACHE
        
        if use_cache and not force_refresh:
            existing = await get_quiz_by_url_and_user(url, user_id)
            
            if existing:
                stored = json.loads(existing["full_quiz_data"])
                if len(stored.get("quiz", [])) >= count:
                    # Trim to requested count
                    stored["quiz"] = stored["quiz"][:count]
                    stored["id"] = existing["id"]
                    logger.info(f"Returning cached quiz for {url}")
                    return stored
        
        # Scrape Wikipedia article
        logger.info(f"Scraping article: {url}")
        title, cleaned_text, sections, raw_html = await scrape_wikipedia(url)
        
        if not cleaned_text or len(cleaned_text) < 200:
            raise UnprocessableEntityException("Article content too short or could not be parsed.")
        
        # Generate quiz using LangChain + Gemini
        logger.info(f"Generating quiz with {count} questions...")
        payload = await generate_quiz_payload(
            url=url,
            title=title,
            article_text=cleaned_text,
            sections=sections,
            count=count
        )
        
        # Trim quiz to requested count
        payload["quiz"] = payload.get("quiz", [])[:count]
        
        # Use scraped sections if LLM didn't provide any
        if not payload.get("sections"):
            payload["sections"] = sections
        
        # Store in database
        existing = await get_quiz_by_url_and_user(url, user_id)
        
        if not existing:
            try:
                result = await create_quiz(
                    url=url,
                    title=title,
                    user_id=user_id,
                    scraped_html=raw_html,
                    scraped_text=cleaned_text,
                    full_quiz_data=payload
                )
                record_id = result["id"]
            except Exception as insert_err:
                # Might be a race condition, try to get existing
                logger.warning(f"Insert failed, checking for existing: {insert_err}")
                existing = await get_quiz_by_url_and_user(url, user_id)
                if existing:
                    record_id = existing["id"]
                    await update_quiz(record_id, title, raw_html, cleaned_text, payload)
                else:
                    raise
        else:
            record_id = existing["id"]
            await update_quiz(record_id, title, raw_html, cleaned_text, payload)
        
        payload["id"] = record_id
        
        logger.info(f"Quiz generated successfully: {title} ({len(payload['quiz'])} questions)")
        
        return payload
        
    except (BadRequestException, UnprocessableEntityException):
        raise
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===========================================
# Quiz History (Protected)
# ===========================================

@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="Get Quiz History",
    description="Get list of previously generated quizzes."
)
async def get_history(
    user: Annotated[CurrentUser, Depends(get_current_user)]
):
    """Get the user's quiz history."""
    try:
        rows = await get_user_quiz_history(user.user_id)
        
        items = []
        for r in rows:
            items.append({
                "id": r["id"],
                "url": r["url"],
                "title": r["title"],
                "date_generated": r["date_generated"].isoformat() if r["date_generated"] else ""
            })
        
        return {"items": items}
        
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get quiz history"
        )


# ===========================================
# Get Single Quiz (Protected)
# ===========================================

@router.get(
    "/quiz/{quiz_id}",
    response_model=QuizData,
    summary="Get Quiz",
    description="Get a specific quiz by ID."
)
async def get_quiz(
    quiz_id: int,
    user: Annotated[CurrentUser, Depends(get_current_user)]
):
    """Get a specific quiz by ID."""
    try:
        row = await get_quiz_by_id_and_user(quiz_id, user.user_id)
        
        if not row:
            raise NotFoundException("Quiz not found")
        
        data = json.loads(row["full_quiz_data"])
        data["id"] = row["id"]
        
        return data
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting quiz {quiz_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get quiz"
        )


# ===========================================
# Submit Quiz Attempt (Protected)
# ===========================================

@router.post(
    "/submit_attempt/{quiz_id}",
    response_model=SubmitAttemptResponse,
    summary="Submit Quiz Attempt",
    description="Submit answers for a quiz attempt."
)
async def submit_attempt(
    quiz_id: int,
    request: SubmitAttemptRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)]
):
    """Submit a quiz attempt."""
    try:
        # Verify quiz exists
        quiz = await get_quiz_by_id(quiz_id)
        
        if not quiz:
            raise NotFoundException("Quiz not found")
        
        # Create attempt record
        result = await create_quiz_attempt(
            quiz_id=quiz_id,
            user_id=user.user_id,
            total_time=request.total_time,
            total_questions=request.total_questions,
            time_taken_seconds=request.time_taken_seconds,
            score=request.score,
            answers_json=request.answers
        )
        
        return {
            "saved": True,
            "attempt_id": result["id"]
        }
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error submitting attempt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit attempt"
        )


# ===========================================
# Export Quiz as PDF (Protected)
# ===========================================

@router.post(
    "/export_pdf/{quiz_id}",
    summary="Export Quiz as PDF",
    description="Export a quiz as a PDF document."
)
async def export_pdf(
    quiz_id: int,
    request: ExportPdfRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)]
):
    """Export a quiz as PDF."""
    try:
        # Get quiz
        row = await get_quiz_by_id(quiz_id)
        
        if not row:
            raise NotFoundException("Quiz not found")
        
        quiz_data = json.loads(row["full_quiz_data"])
        quiz_data["id"] = row["id"]
        
        # Add user's answers and score from request
        quiz_data["user_answers"] = request.user_answers or {}
        quiz_data["score"] = request.score or 0
        quiz_data["total"] = request.total or len(quiz_data.get("quiz", []))
        
        # Limit questions if count specified
        count = request.count
        if count is not None and count > 0:
            quiz_data["quiz"] = quiz_data.get("quiz", [])[:count]
        
        # Build PDF
        pdf_buffer = build_exam_pdf(
            org_title="DeepKlarity AI Exam",
            user=request.user or "Anonymous",
            quiz_title=quiz_data.get("title", "Quiz"),
            quiz=quiz_data,
            duration_str=request.duration_str or "—"
        )
        
        filename = f"quiz_{quiz_id}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export PDF"
        )
