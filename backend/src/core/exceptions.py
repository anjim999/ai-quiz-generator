"""
Custom Exceptions Module
========================
Centralized exception handling for the application.
Provides custom HTTP exceptions with proper error responses.
"""

from typing import Any, Optional, Dict
from fastapi import HTTPException, status


class AppException(HTTPException):
    """
    Base application exception.
    All custom exceptions should inherit from this class.
    """
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class BadRequestException(AppException):
    """Exception for 400 Bad Request errors."""
    
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(AppException):
    """Exception for 401 Unauthorized errors."""
    
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(AppException):
    """Exception for 403 Forbidden errors."""
    
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(AppException):
    """Exception for 404 Not Found errors."""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictException(AppException):
    """Exception for 409 Conflict errors."""
    
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UnprocessableEntityException(AppException):
    """Exception for 422 Unprocessable Entity errors."""
    
    def __init__(self, detail: str = "Unprocessable entity"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class TooManyRequestsException(AppException):
    """Exception for 429 Too Many Requests errors."""
    
    def __init__(self, detail: str = "Too many requests"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        )


class InternalServerException(AppException):
    """Exception for 500 Internal Server errors."""
    
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class DatabaseException(InternalServerException):
    """Exception for database-related errors."""
    
    def __init__(self, detail: str = "Database error"):
        super().__init__(detail=f"Database error: {detail}")


class ExternalServiceException(AppException):
    """Exception for external service errors (Gemini, Email, etc.)."""
    
    def __init__(self, service: str, detail: str = "Service unavailable"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service} service error: {detail}"
        )
