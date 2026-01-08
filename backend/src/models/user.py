"""
User Models
===========
Pydantic models for user-related data.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class UserWithQuizCount(BaseModel):
    """User with quiz count for admin panel."""
    id: int
    name: str
    email: str
    role: str
    created_at: datetime
    quiz_count: int


class UserAttempt(BaseModel):
    """User's quiz attempt details."""
    id: int
    quiz_id: int
    title: str
    url: str
    score: Optional[int]
    full_quiz_data: Optional[str]
    submitted_at: Optional[datetime]
    time_taken_seconds: Optional[int]
    total_time: Optional[int]
    total_questions: Optional[int]


class AdminUsersResponse(BaseModel):
    """Admin users list response."""
    users: List[UserWithQuizCount]


class UserAttemptsResponse(BaseModel):
    """User attempts response for admin."""
    attempts: List[UserAttempt]
