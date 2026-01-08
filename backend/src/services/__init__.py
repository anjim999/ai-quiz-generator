"""
Services Module
===============
Business logic layer.
"""

from .scraper import scrape_wikipedia, clean_wikipedia_html
from .llm_quiz_generator import generate_quiz_payload
from .pdf_generator import build_exam_pdf
from .fallback import fallback_quiz

__all__ = [
    "scrape_wikipedia",
    "clean_wikipedia_html",
    "generate_quiz_payload",
    "build_exam_pdf",
    "fallback_quiz"
]
