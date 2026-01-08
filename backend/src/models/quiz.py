"""
Quiz Models
===========
Pydantic models for quiz endpoints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


# ===========================================
# Quiz Data Models
# ===========================================

class QuizQuestion(BaseModel):
    """A single quiz question."""
    question: str = Field(..., description="Question text")
    options: List[str] = Field(..., min_length=4, max_length=4, description="Four answer options")
    answer: str = Field(..., description="Correct answer")
    difficulty: str = Field(..., pattern="^(easy|medium|hard)$", description="Difficulty level")
    explanation: str = Field(..., description="Explanation for the answer")


class KeyEntities(BaseModel):
    """Key entities extracted from the article."""
    people: List[str] = Field(default_factory=list)
    organizations: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)


class QuizData(BaseModel):
    """Complete quiz data structure matching assignment requirements."""
    id: Optional[int] = None
    url: str
    title: str
    summary: str = Field(..., description="Article summary")
    key_entities: KeyEntities = Field(default_factory=KeyEntities)
    sections: List[str] = Field(default_factory=list, description="Article sections")
    quiz: List[QuizQuestion] = Field(..., description="Quiz questions")
    related_topics: List[str] = Field(default_factory=list, description="Related Wikipedia topics")


# ===========================================
# Request Models
# ===========================================

class GenerateQuizRequest(BaseModel):
    """Request to generate a quiz from a URL."""
    url: str = Field(..., description="Wikipedia article URL")
    force_refresh: bool = Field(default=False, description="Force regeneration even if cached")


class SubmitAttemptRequest(BaseModel):
    """Request to submit a quiz attempt."""
    answers: Dict[str, str] = Field(default_factory=dict, description="User's answers (question index -> answer)")
    score: int = Field(default=0, ge=0, description="User's score")
    time_taken_seconds: int = Field(default=0, ge=0, description="Time taken in seconds")
    total_time: Optional[int] = Field(None, description="Total allowed time")
    total_questions: Optional[int] = Field(None, description="Total number of questions")


class ExportPdfRequest(BaseModel):
    """Request to export quiz as PDF."""
    count: Optional[int] = Field(None, description="Number of questions to include")
    user: Optional[str] = Field(default="Anonymous", description="User name for PDF")
    duration_str: Optional[str] = Field(default="—", description="Duration string for PDF")
    user_answers: Optional[Dict[str, str]] = Field(default_factory=dict, description="User's submitted answers")
    score: Optional[int] = Field(default=0, description="User's score")
    total: Optional[int] = Field(None, description="Total questions")


# ===========================================
# Response Models
# ===========================================

class HistoryItem(BaseModel):
    """A quiz history item."""
    id: int
    url: str
    title: str
    date_generated: str


class HistoryResponse(BaseModel):
    """Quiz history response."""
    items: List[HistoryItem]


class SubmitAttemptResponse(BaseModel):
    """Quiz attempt submission response."""
    saved: bool
    attempt_id: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
