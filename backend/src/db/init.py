"""
Database Initialization Module
==============================
Creates database schema and tables on application startup.
"""

import logging
from src.db.database import get_db_pool

logger = logging.getLogger(__name__)


async def init_database() -> None:
    """
    Initialize database schema.
    Creates all required tables if they don't exist.
    """
    logger.info("Initializing database schema...")
    
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        # ===========================================
        # Users Table
        # ===========================================
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'user',
                is_verified BOOLEAN NOT NULL DEFAULT TRUE,
                google_id VARCHAR(255),
                avatar TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        logger.info("✓ Users table ready")
        
        # ===========================================
        # OTPs Table
        # ===========================================
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS otps (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                code VARCHAR(10) NOT NULL,
                purpose VARCHAR(20) NOT NULL,
                expires_at TIMESTAMPTZ NOT NULL,
                used BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        logger.info("✓ OTPs table ready")
        
        # ===========================================
        # Quizzes Table
        # ===========================================
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id SERIAL PRIMARY KEY,
                url VARCHAR(2048) NOT NULL,
                title VARCHAR(512) NOT NULL,
                user_id INT,
                date_generated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                scraped_html TEXT,
                scraped_text TEXT,
                full_quiz_data TEXT NOT NULL
            )
        """)
        
        # Create unique index on URL (handle if exists)
        try:
            await conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS uq_quizzes_url 
                ON quizzes (url, user_id)
            """)
        except Exception:
            # Index might exist with different definition
            pass
        
        logger.info("✓ Quizzes table ready")
        
        # ===========================================
        # Quiz Attempts Table
        # ===========================================
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id SERIAL PRIMARY KEY,
                quiz_id INT NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
                user_id INT NOT NULL,
                started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                submitted_at TIMESTAMPTZ,
                total_time INT,
                total_questions INT,
                time_taken_seconds INT,
                score INT,
                answers_json TEXT
            )
        """)
        
        # Create index for faster lookups
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_quiz_attempts_quiz_id 
            ON quiz_attempts (quiz_id)
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_quiz_attempts_user_id 
            ON quiz_attempts (user_id)
        """)
        
        logger.info("✓ Quiz attempts table ready")
        
        # ===========================================
        # Add user_id column to existing tables (migration)
        # ===========================================
        try:
            await conn.execute("""
                ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS user_id INT
            """)
        except Exception:
            pass
        
        try:
            await conn.execute("""
                ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS user_id INT
            """)
        except Exception:
            pass
        
        logger.info("✓ Database schema initialization complete")
