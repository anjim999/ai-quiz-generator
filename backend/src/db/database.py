"""
Database Connection Module
==========================
Async PostgreSQL connection pool management using asyncpg.
Provides connection pooling, query execution, and error handling.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple
from contextlib import asynccontextmanager
import asyncpg
from asyncpg import Pool, Connection

from src.core import settings

# Configure logger
logger = logging.getLogger(__name__)

# Global connection pool
_pool: Optional[Pool] = None


async def get_db_pool() -> Pool:
    """
    Get or create the database connection pool.
    
    Returns:
        asyncpg Pool instance
    """
    global _pool
    
    if _pool is None:
        logger.info("Creating database connection pool...")
        
        # Parse SSL settings from DATABASE_URL
        dsn = settings.DATABASE_URL
        ssl_required = (
            "sslmode=require" in dsn.lower() or 
            "neon" in dsn.lower() or
            "sslmode" in dsn.lower()
        )
        
        # For asyncpg, we need to use ssl=True or ssl="require"
        # and create_pool doesn't accept sslmode in the DSN the same way
        # So we need to handle it properly
        import ssl as ssl_module
        
        ssl_context = None
        if ssl_required:
            ssl_context = ssl_module.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl_module.CERT_NONE
        
        try:
            _pool = await asyncpg.create_pool(
                dsn=dsn,
                min_size=1,
                max_size=settings.DB_POOL_SIZE,
                max_inactive_connection_lifetime=300,
                command_timeout=60,
                timeout=60,  # Connection timeout
                ssl=ssl_context if ssl_required else None
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise
    
    return _pool


async def close_db_pool() -> None:
    """
    Close the database connection pool.
    Should be called on application shutdown.
    """
    global _pool
    
    if _pool is not None:
        logger.info("Closing database connection pool...")
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


@asynccontextmanager
async def get_connection():
    """
    Get a database connection from the pool.
    
    Usage:
        async with get_connection() as conn:
            result = await conn.fetch("SELECT * FROM users")
    
    Yields:
        asyncpg Connection instance
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as connection:
        yield connection


async def execute_query(
    query: str,
    *args,
    timeout: float = 30.0
) -> List[asyncpg.Record]:
    """
    Execute a query and return all results.
    
    Args:
        query: SQL query string with $1, $2, etc. placeholders
        *args: Query parameters
        timeout: Query timeout in seconds
        
    Returns:
        List of asyncpg.Record objects
    """
    pool = await get_db_pool()
    
    try:
        async with pool.acquire() as conn:
            result = await conn.fetch(query, *args, timeout=timeout)
            logger.debug(f"Query OK: rows={len(result)}")
            return result
    except asyncpg.PostgresError as e:
        logger.error(f"Database query error: {e}")
        raise


async def execute_query_one(
    query: str,
    *args,
    timeout: float = 30.0
) -> Optional[asyncpg.Record]:
    """
    Execute a query and return a single result.
    
    Args:
        query: SQL query string with $1, $2, etc. placeholders
        *args: Query parameters
        timeout: Query timeout in seconds
        
    Returns:
        Single asyncpg.Record or None if no results
    """
    pool = await get_db_pool()
    
    try:
        async with pool.acquire() as conn:
            result = await conn.fetchrow(query, *args, timeout=timeout)
            logger.debug(f"Query OK: found={'yes' if result else 'no'}")
            return result
    except asyncpg.PostgresError as e:
        logger.error(f"Database query error: {e}")
        raise


async def execute_many(
    query: str,
    args_list: List[Tuple],
    timeout: float = 60.0
) -> None:
    """
    Execute the same query with multiple sets of parameters.
    
    Args:
        query: SQL query string with $1, $2, etc. placeholders
        args_list: List of parameter tuples
        timeout: Query timeout in seconds
    """
    pool = await get_db_pool()
    
    try:
        async with pool.acquire() as conn:
            await conn.executemany(query, args_list, timeout=timeout)
            logger.debug(f"Batch query OK: count={len(args_list)}")
    except asyncpg.PostgresError as e:
        logger.error(f"Database batch query error: {e}")
        raise


async def execute_transaction(queries: List[Tuple[str, Tuple]]) -> None:
    """
    Execute multiple queries in a transaction.
    
    Args:
        queries: List of (query_string, params_tuple) tuples
    """
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        async with conn.transaction():
            for query, params in queries:
                await conn.execute(query, *params)
            logger.debug(f"Transaction OK: queries={len(queries)}")
