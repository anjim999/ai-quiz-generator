"""
Quiz Database Queries
=====================
All database queries related to quizzes and quiz attempts.
"""

from typing import Optional, List
import json
import asyncpg
from src.db.database import execute_query, execute_query_one, get_db_pool


async def get_quiz_by_url_and_user(
    url: str, 
    user_id: int
) -> Optional[asyncpg.Record]:
    """Get a quiz by URL and user ID."""
    return await execute_query_one(
        "SELECT * FROM quizzes WHERE url = $1 AND user_id = $2 LIMIT 1",
        url,
        user_id
    )


async def get_quiz_by_id(quiz_id: int) -> Optional[asyncpg.Record]:
    """Get a quiz by its ID."""
    return await execute_query_one(
        "SELECT * FROM quizzes WHERE id = $1 LIMIT 1",
        quiz_id
    )


async def get_quiz_by_id_and_user(
    quiz_id: int, 
    user_id: int
) -> Optional[asyncpg.Record]:
    """Get a quiz by ID and user ID (ownership check)."""
    return await execute_query_one(
        "SELECT * FROM quizzes WHERE id = $1 AND user_id = $2 LIMIT 1",
        quiz_id,
        user_id
    )


async def create_quiz(
    url: str,
    title: str,
    user_id: int,
    scraped_html: str,
    scraped_text: str,
    full_quiz_data: dict
) -> asyncpg.Record:
    """
    Create a new quiz.
    
    Returns:
        Created quiz record with id
    """
    return await execute_query_one(
        """
        INSERT INTO quizzes (url, title, scraped_html, scraped_text, full_quiz_data, user_id)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id
        """,
        url,
        title,
        scraped_html,
        scraped_text,
        json.dumps(full_quiz_data),
        user_id
    )


async def update_quiz(
    quiz_id: int,
    title: str,
    scraped_html: str,
    scraped_text: str,
    full_quiz_data: dict
) -> None:
    """Update an existing quiz."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE quizzes
            SET title = $1, scraped_html = $2, scraped_text = $3, full_quiz_data = $4
            WHERE id = $5
            """,
            title,
            scraped_html,
            scraped_text,
            json.dumps(full_quiz_data),
            quiz_id
        )


async def get_user_quiz_history(user_id: int) -> List[asyncpg.Record]:
    """
    Get quiz history for a user.
    
    Returns:
        List of quiz records (id, url, title, date_generated)
    """
    return await execute_query(
        """
        SELECT id, url, title, date_generated 
        FROM quizzes 
        WHERE user_id = $1 
        ORDER BY date_generated DESC
        """,
        user_id
    )


async def create_quiz_attempt(
    quiz_id: int,
    user_id: int,
    total_time: Optional[int],
    total_questions: Optional[int],
    time_taken_seconds: int,
    score: int,
    answers_json: dict
) -> asyncpg.Record:
    """
    Create a quiz attempt record.
    
    Returns:
        Created attempt record with id
    """
    return await execute_query_one(
        """
        INSERT INTO quiz_attempts
            (quiz_id, user_id, submitted_at, total_time, total_questions, 
             time_taken_seconds, score, answers_json)
        VALUES ($1, $2, NOW(), $3, $4, $5, $6, $7)
        RETURNING id
        """,
        quiz_id,
        user_id,
        total_time,
        total_questions,
        time_taken_seconds,
        score,
        json.dumps(answers_json)
    )


async def get_user_attempts(user_id: int) -> List[asyncpg.Record]:
    """
    Get all quiz attempts for a user with quiz details.
    Used for admin panel.
    """
    return await execute_query(
        """
        SELECT
            qa.id,
            qa.quiz_id,
            q.title,
            q.url,
            qa.score,
            q.full_quiz_data,
            qa.submitted_at,
            qa.time_taken_seconds,
            qa.total_time,
            qa.total_questions
        FROM quiz_attempts qa
        JOIN quizzes q ON qa.quiz_id = q.id
        WHERE qa.user_id = $1
        ORDER BY qa.submitted_at DESC
        """,
        user_id
    )
