"""
API Routers Module
==================
FastAPI route definitions.
"""

from .auth import router as auth_router
from .quiz import router as quiz_router
from .admin import router as admin_router

__all__ = ["auth_router", "quiz_router", "admin_router"]
