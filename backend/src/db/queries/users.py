"""
User Database Queries
=====================
All database queries related to users.
"""

from typing import Optional, Dict, Any
import asyncpg
from src.db.database import execute_query, execute_query_one, get_db_pool


async def get_user_by_email(email: str) -> Optional[asyncpg.Record]:
    """Get a user by their email address."""
    return await execute_query_one(
        "SELECT * FROM users WHERE email = $1",
        email.lower().strip()
    )


async def get_user_by_id(user_id: int) -> Optional[asyncpg.Record]:
    """Get a user by their ID."""
    return await execute_query_one(
        "SELECT * FROM users WHERE id = $1",
        user_id
    )


async def get_user_by_google_id(google_id: str) -> Optional[asyncpg.Record]:
    """Get a user by their Google ID."""
    return await execute_query_one(
        "SELECT * FROM users WHERE google_id = $1",
        google_id
    )


async def get_user_by_email_or_google_id(
    email: str, 
    google_id: str
) -> Optional[asyncpg.Record]:
    """Get a user by email or Google ID."""
    return await execute_query_one(
        "SELECT * FROM users WHERE email = $1 OR google_id = $2",
        email.lower().strip(),
        google_id
    )


async def create_user(
    name: str,
    email: str,
    password: str,
    role: str = "user",
    is_verified: bool = True,
    google_id: Optional[str] = None,
    avatar: Optional[str] = None
) -> asyncpg.Record:
    """
    Create a new user.
    
    Returns:
        Created user record
    """
    return await execute_query_one(
        """
        INSERT INTO users (name, email, password, role, is_verified, google_id, avatar)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id, name, email, role, avatar, google_id
        """,
        name,
        email.lower().strip(),
        password,
        role,
        is_verified,
        google_id,
        avatar
    )


async def upsert_user(
    name: str,
    email: str,
    password: str,
    is_verified: bool = True
) -> asyncpg.Record:
    """
    Insert or update a user (for registration verification).
    
    Returns:
        User record
    """
    return await execute_query_one(
        """
        INSERT INTO users (name, email, password, is_verified)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (email) DO UPDATE SET
            name = EXCLUDED.name,
            password = EXCLUDED.password,
            is_verified = EXCLUDED.is_verified
        RETURNING id, name, email, role
        """,
        name,
        email.lower().strip(),
        password,
        is_verified
    )


async def update_user_password(email: str, hashed_password: str) -> int:
    """
    Update a user's password.
    
    Returns:
        Number of rows affected
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE users SET password = $1 WHERE email = $2",
            hashed_password,
            email.lower().strip()
        )
        # Result is like "UPDATE 1"
        return int(result.split()[-1]) if result else 0


async def update_user_google_info(
    user_id: int,
    google_id: str,
    avatar: Optional[str] = None
) -> None:
    """Update user's Google ID and avatar."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE users
            SET google_id = $1, avatar = $2
            WHERE id = $3
            """,
            google_id,
            avatar,
            user_id
        )


async def get_all_users_with_quiz_count():
    """
    Get all users with their quiz count.
    Used for admin panel.
    """
    return await execute_query(
        """
        SELECT
            u.id,
            u.name,
            u.email,
            u.role,
            u.created_at,
            COUNT(q.id) AS quiz_count
        FROM users u
        LEFT JOIN quizzes q ON q.user_id = u.id
        GROUP BY u.id
        ORDER BY u.created_at DESC
        """
    )
