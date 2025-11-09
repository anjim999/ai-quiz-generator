
from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    date_generated = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    scraped_html = Column(Text, nullable=True)
    scraped_text = Column(Text, nullable=True)
    full_quiz_data = Column(Text, nullable=False)
    __table_args__ = (UniqueConstraint('url', name='uq_quizzes_url'),)

class Attempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), index=True, nullable=False)
    # started_at: default to NOW() on insert (both client-side and server-side) and never NULL
    started_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    )
    # submitted_at: remains nullable until the attempt is submitted
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    total_time = Column(Integer, nullable=True)
    total_questions = Column(Integer, nullable=True)
    time_taken_seconds = Column(Integer, nullable=True)
    score = Column(Integer, nullable=True)  # out of number_of_questions
    answers_json = Column(Text, nullable=True)  # {"0":"A", "1":"C", ...}


# # --- NEW ---
# from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
# from sqlalchemy.sql import func
# from database import Base

# class ExamSession(Base):
#     __tablename__ = "exam_sessions"
#     id = Column(Integer, primary_key=True)
#     quiz_id = Column(Integer, ForeignKey("quizzes.id"), index=True, nullable=False)
#     started_at = Column(DateTime(timezone=True), server_default=func.now())
#     finished_at = Column(DateTime(timezone=True), nullable=True)
#     total_questions = Column(Integer, nullable=False, default=0)
#     user_name = Column(String(200), nullable=True)
#     auto_submitted = Column(Boolean, default=False)
#     score = Column(Integer, nullable=True)
#     time_taken_seconds = Column(Integer, nullable=True)

# class ProctorEvent(Base):
#     __tablename__ = "proctor_events"
#     id = Column(Integer, primary_key=True)
#     session_id = Column(Integer, ForeignKey("exam_sessions.id"), index=True, nullable=False)
#     at = Column(DateTime(timezone=True), server_default=func.now())
#     type = Column(String(64), nullable=False)   # 'tab-blur' | 'visibility-hidden' | 'fs-exit' | 'fs-enter' | 'submit'
#     meta = Column(Text, nullable=True)
