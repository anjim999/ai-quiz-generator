"""
Admin Router
============
Admin-only endpoints for user and quiz management.

Endpoints:
- GET /api/admin/users - Get all users with quiz counts
- GET /api/admin/user/{userId}/attempts - Get user's quiz attempts
"""

import logging
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status

from src.middleware import get_current_admin_user, CurrentUser
from src.db.queries.users import get_all_users_with_quiz_count
from src.db.queries.quizzes import get_user_attempts

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ===========================================
# Get All Users (Admin Only)
# ===========================================

@router.get(
    "/users",
    summary="Get All Users",
    description="Get list of all users with their quiz counts. Admin only."
)
async def get_users(
    user: Annotated[CurrentUser, Depends(get_current_admin_user)]
):
    """Get all users with quiz counts."""
    try:
        rows = await get_all_users_with_quiz_count()
        
        users = []
        for r in rows:
            users.append({
                "id": r["id"],
                "name": r["name"],
                "email": r["email"],
                "role": r["role"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "quiz_count": r["quiz_count"] or 0
            })
        
        return users
        
    except Exception as e:
        logger.error(f"Admin users query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DB error"
        )


# ===========================================
# Get User Attempts (Admin Only)
# ===========================================

@router.get(
    "/user/{user_id}/attempts",
    summary="Get User Attempts",
    description="Get all quiz attempts for a specific user. Admin only."
)
async def get_user_quiz_attempts(
    user_id: int,
    admin: Annotated[CurrentUser, Depends(get_current_admin_user)]
):
    """Get all quiz attempts for a user."""
    try:
        rows = await get_user_attempts(user_id)
        
        attempts = []
        for r in rows:
            attempts.append({
                "id": r["id"],
                "quiz_id": r["quiz_id"],
                "title": r["title"],
                "url": r["url"],
                "score": r["score"],
                "full_quiz_data": r["full_quiz_data"],
                "submitted_at": r["submitted_at"].isoformat() if r["submitted_at"] else None,
                "time_taken_seconds": r["time_taken_seconds"],
                "total_time": r["total_time"],
                "total_questions": r["total_questions"]
            })
        
        return attempts
        
    except Exception as e:
        logger.error(f"Failed to fetch user attempts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DB error"
        )
