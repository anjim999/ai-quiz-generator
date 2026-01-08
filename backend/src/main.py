"""
AI Quiz Generator - FastAPI Backend
====================================
Main application entry point.

This is a production-grade FastAPI application that:
- Generates quizzes from Wikipedia articles using LangChain + Gemini
- Provides user authentication with JWT and Google OAuth
- Stores data in PostgreSQL
- Exports quizzes as PDF

Technical Stack:
- Framework: FastAPI
- Database: PostgreSQL (async with asyncpg)
- LLM: Google Gemini via LangChain
- Scraping: BeautifulSoup
- Authentication: JWT + Google OAuth

Author: DeepKlarity Technologies Assignment
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import settings
from src.core.exceptions import AppException
from src.db import init_database, close_db_pool
from src.routers import auth_router, quiz_router, admin_router

# ===========================================
# Logging Configuration
# ===========================================
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# ===========================================
# Application Lifespan
# ===========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("=" * 50)
    logger.info("AI Quiz Generator - FastAPI Backend")
    logger.info("=" * 50)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    
    try:
        await init_database()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {e}")
        raise
    
    logger.info("✓ Application started successfully")
    logger.info("=" * 50)
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_db_pool()
    logger.info("✓ Database connections closed")
    logger.info("Goodbye!")


# ===========================================
# Create FastAPI Application
# ===========================================
app = FastAPI(
    title="AI Quiz Generator API",
    description="""
    A FastAPI backend for generating quizzes from Wikipedia articles.
    
    ## Features
    
    * **Quiz Generation** - Generate quizzes from Wikipedia URLs using AI
    * **Take Quiz Mode** - Submit answers and get scored
    * **History** - View past quizzes
    * **PDF Export** - Export quizzes as PDF documents
    * **Authentication** - JWT and Google OAuth support
    
    ## Technical Stack
    
    * FastAPI + PostgreSQL
    * LangChain + Google Gemini
    * BeautifulSoup for scraping
    
    Built for DeepKlarity Technologies Assignment.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ===========================================
# CORS Middleware
# ===========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================================
# Exception Handlers
# ===========================================
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}")
    logger.exception("Full traceback:")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# ===========================================
# Include Routers
# ===========================================
app.include_router(auth_router)
app.include_router(quiz_router)
app.include_router(admin_router)


# ===========================================
# Root Endpoint
# ===========================================
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API health check."""
    return {
        "status": "ok",
        "message": "AI Quiz Generator Backend",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok"}


# ===========================================
# Run with Uvicorn (for development)
# ===========================================
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
