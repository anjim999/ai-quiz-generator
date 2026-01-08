"""
Authentication Models
=====================
Pydantic models for authentication endpoints.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ===========================================
# Request Models
# ===========================================

class RegisterRequestOTPRequest(BaseModel):
    """Request to send registration OTP."""
    email: EmailStr = Field(..., description="User's email address")


class RegisterVerifyRequest(BaseModel):
    """Request to verify OTP and complete registration."""
    name: str = Field(..., min_length=1, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    otp: str = Field(..., min_length=4, description="OTP code")
    password: str = Field(..., min_length=6, description="User's password")


class LoginRequest(BaseModel):
    """Request to login with email and password."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")


class ForgotPasswordRequest(BaseModel):
    """Request to send password reset OTP."""
    email: EmailStr = Field(..., description="User's email address")


class ForgotPasswordVerifyRequest(BaseModel):
    """Request to verify OTP and reset password."""
    email: EmailStr = Field(..., description="User's email address")
    otp: str = Field(..., min_length=4, description="OTP code")
    newPassword: str = Field(..., min_length=6, alias="newPassword", description="New password")
    
    class Config:
        populate_by_name = True


class GoogleAuthRequest(BaseModel):
    """Request for Google OAuth login."""
    idToken: Optional[str] = Field(None, description="Google ID token")
    credential: Optional[str] = Field(None, description="Google credential token")


# ===========================================
# Response Models
# ===========================================

class UserResponse(BaseModel):
    """User information in responses."""
    id: int
    name: str
    email: str
    role: str
    avatar: Optional[str] = None
    google_id: Optional[str] = None


class AuthResponse(BaseModel):
    """Authentication response with token and user."""
    message: str
    token: str
    user: UserResponse


class OTPResponse(BaseModel):
    """OTP generation response."""
    message: str
    devOtp: Optional[str] = None  # Only in development


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
