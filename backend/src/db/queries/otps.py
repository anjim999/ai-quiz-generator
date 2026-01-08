"""
OTP Database Queries
====================
All database queries related to OTPs (One-Time Passwords).
"""

from typing import Optional
from datetime import datetime
import asyncpg
from src.db.database import execute_query, execute_query_one, get_db_pool


async def create_otp(
    email: str,
    code: str,
    purpose: str,
    expires_at: str
) -> asyncpg.Record:
    """
    Create a new OTP record.
    
    Args:
        email: User's email address
        code: OTP code
        purpose: 'REGISTER' or 'RESET'
        expires_at: ISO format expiry timestamp
        
    Returns:
        Created OTP record
    """
    return await execute_query_one(
        """
        INSERT INTO otps (email, code, purpose, expires_at)
        VALUES ($1, $2, $3, $4)
        RETURNING id
        """,
        email.lower().strip(),
        code,
        purpose,
        expires_at
    )


async def get_valid_otp(
    email: str,
    code: str,
    purpose: str
) -> Optional[asyncpg.Record]:
    """
    Get a valid (unused) OTP.
    
    Args:
        email: User's email address
        code: OTP code to verify
        purpose: 'REGISTER' or 'RESET'
        
    Returns:
        OTP record if found and valid, None otherwise
    """
    return await execute_query_one(
        """
        SELECT * FROM otps
        WHERE email = $1 AND code = $2 AND purpose = $3 AND used = FALSE
        ORDER BY created_at DESC
        LIMIT 1
        """,
        email.lower().strip(),
        code,
        purpose
    )


async def mark_otp_used(otp_id: int) -> None:
    """Mark an OTP as used."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE otps SET used = TRUE WHERE id = $1",
            otp_id
        )


async def cleanup_expired_otps() -> int:
    """
    Delete expired OTPs.
    
    Returns:
        Number of deleted records
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM otps WHERE expires_at < NOW() OR used = TRUE"
        )
        # Result is like "DELETE 5"
        return int(result.split()[-1]) if result else 0
