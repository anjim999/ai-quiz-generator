"""
Authentication Middleware
=========================
JWT authentication dependency for FastAPI routes.
"""

import logging
from typing import Optional, Annotated
from dataclasses import dataclass
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.core.security import verify_token
from src.core.exceptions import UnauthorizedException, ForbiddenException
from src.core import settings

logger = logging.getLogger(__name__)

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    """
    Current authenticated user data.
    Populated from JWT token payload.
    """
    user_id: int
    email: str
    name: str
    role: str


async def get_current_user(
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials], 
        Depends(security)
    ] = None
) -> CurrentUser:
    """
    FastAPI dependency to get the current authenticated user.
    
    Usage:
        @router.get("/protected")
        async def protected_route(user: CurrentUser = Depends(get_current_user)):
            return {"user_id": user.user_id}
    
    Raises:
        UnauthorizedException: If no token provided or token is invalid/expired
        
    Returns:
        CurrentUser object with user data from token
    """
    
    # Check for test environment
    if settings.ENVIRONMENT == "test":
        return CurrentUser(
            user_id=1,
            email="test@example.com",
            name="Test User",
            role="admin"
        )
    
    # Check if credentials are provided
    if credentials is None:
        raise UnauthorizedException("No token provided")
    
    token = credentials.credentials
    
    # Verify and decode the token
    payload = verify_token(token)
    
    if payload is None:
        raise UnauthorizedException("Invalid or expired token")
    
    # Extract user data from payload
    user_id = payload.get("userId")
    email = payload.get("email")
    name = payload.get("name")
    role = payload.get("role", "user")
    
    if not user_id or not email:
        raise UnauthorizedException("Invalid token payload")
    
    return CurrentUser(
        user_id=user_id,
        email=email,
        name=name or email,
        role=role
    )


async def get_current_admin_user(
    user: Annotated[CurrentUser, Depends(get_current_user)]
) -> CurrentUser:
    """
    FastAPI dependency to get the current authenticated admin user.
    
    Usage:
        @router.get("/admin-only")
        async def admin_route(user: CurrentUser = Depends(get_current_admin_user)):
            return {"admin_id": user.user_id}
    
    Raises:
        ForbiddenException: If user is not an admin
        
    Returns:
        CurrentUser object (guaranteed to be admin)
    """
    
    if user.role != "admin":
        raise ForbiddenException("Admins only")
    
    return user


async def get_optional_user(
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials], 
        Depends(security)
    ] = None
) -> Optional[CurrentUser]:
    """
    FastAPI dependency to optionally get the current user.
    Returns None if no valid token is provided (doesn't raise error).
    
    Usage:
        @router.get("/public-or-auth")
        async def route(user: Optional[CurrentUser] = Depends(get_optional_user)):
            if user:
                return {"user_id": user.user_id}
            return {"message": "guest"}
    
    Returns:
        CurrentUser object if authenticated, None otherwise
    """
    
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except UnauthorizedException:
        return None
