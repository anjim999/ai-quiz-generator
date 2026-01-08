"""
Authentication Router
=====================
Handles user registration, login, password reset, and Google OAuth.

Endpoints:
- POST /api/auth/register-request-otp - Request registration OTP
- POST /api/auth/register-verify - Verify OTP and complete registration
- POST /api/auth/login - Login with email/password
- POST /api/auth/forgot-password-request - Request password reset OTP
- POST /api/auth/forgot-password-verify - Verify OTP and reset password
- POST /api/auth/google - Google OAuth login
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status

from src.core import settings
from src.core.security import hash_password, verify_password, create_access_token
from src.core.exceptions import BadRequestException, UnauthorizedException
from src.models.auth import (
    RegisterRequestOTPRequest, RegisterVerifyRequest, LoginRequest,
    ForgotPasswordRequest, ForgotPasswordVerifyRequest, GoogleAuthRequest,
    AuthResponse, UserResponse, OTPResponse, MessageResponse
)
from src.db.queries.users import (
    get_user_by_email, create_user, upsert_user, update_user_password,
    get_user_by_email_or_google_id, update_user_google_info
)
from src.db.queries.otps import create_otp, get_valid_otp, mark_otp_used
from src.utils import generate_otp, get_expiry, normalize_email, send_otp_email
from src.utils.otp import is_expired

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ===========================================
# Registration Endpoints
# ===========================================

@router.post(
    "/register-request-otp",
    response_model=OTPResponse,
    summary="Request Registration OTP",
    description="Send a registration OTP to the user's email address."
)
async def register_request_otp(request: RegisterRequestOTPRequest):
    """Request an OTP for registration."""
    try:
        email = normalize_email(request.email)
        
        # Generate OTP
        code = generate_otp()
        expires_at = get_expiry(10)  # 10 minutes
        
        # Store OTP in database
        await create_otp(email, code, "REGISTER", expires_at)
        
        # Send email
        mail_result = await send_otp_email(email, code, "REGISTER")
        
        if not mail_result.get("success"):
            logger.warning("OTP email not delivered. OTP logged on server only.")
        
        # Return response (include OTP in dev mode)
        response = {"message": "OTP generated. If email doesn't arrive, use the OTP from server logs."}
        
        if not settings.is_production:
            response["devOtp"] = code
        
        return response
        
    except Exception as e:
        logger.error(f"Error in register-request-otp: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate OTP"
        )


@router.post(
    "/register-verify",
    response_model=AuthResponse,
    summary="Verify OTP and Register",
    description="Verify the OTP and complete user registration."
)
async def register_verify(request: RegisterVerifyRequest):
    """Verify OTP and complete registration."""
    try:
        email = normalize_email(request.email)
        
        # Get valid OTP
        otp_row = await get_valid_otp(email, request.otp, "REGISTER")
        
        if not otp_row:
            raise BadRequestException("Invalid OTP")
        
        # Check expiration
        if is_expired(otp_row["expires_at"]):
            raise BadRequestException("OTP expired")
        
        # Hash password
        hashed_password = hash_password(request.password)
        
        # Create or update user
        user = await upsert_user(request.name, email, hashed_password, is_verified=True)
        
        # Mark OTP as used
        await mark_otp_used(otp_row["id"])
        
        # Generate JWT token
        role = user["role"] if user["role"] else "user"
        token = create_access_token({
            "userId": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": role
        })
        
        return {
            "message": "Registration successful",
            "token": token,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": role
            }
        }
        
    except BadRequestException:
        raise
    except Exception as e:
        logger.error(f"Error in register-verify: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DB error / registration failed"
        )


# ===========================================
# Login Endpoint
# ===========================================

@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login",
    description="Login with email and password."
)
async def login(request: LoginRequest):
    """Login with email and password."""
    try:
        email = normalize_email(request.email)
        
        # Get user
        user = await get_user_by_email(email)
        
        if not user:
            logger.warning(f"Login failed: user not found for {email}")
            raise BadRequestException("Invalid credentials")
        
        # Verify password
        if not verify_password(request.password, user["password"]):
            logger.warning(f"Login failed: wrong password for {email}")
            raise BadRequestException("Invalid credentials")
        
        # Generate JWT token
        role = user["role"] if user["role"] else "user"
        token = create_access_token({
            "userId": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": role
        })
        
        logger.info(f"Login successful for {email}")
        
        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": role,
                "avatar": user.get("avatar")
            }
        }
        
    except BadRequestException:
        raise
    except Exception as e:
        logger.error(f"DB error on login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DB error"
        )


# ===========================================
# Password Reset Endpoints
# ===========================================

@router.post(
    "/forgot-password-request",
    response_model=MessageResponse,
    summary="Request Password Reset OTP",
    description="Send a password reset OTP to the user's email."
)
async def forgot_password_request(request: ForgotPasswordRequest):
    """Request a password reset OTP."""
    try:
        email = normalize_email(request.email)
        
        # Check if user exists
        user = await get_user_by_email(email)
        
        if not user:
            logger.warning(f"Forgot password for non-existing email: {email}")
            # Return success message anyway (security best practice)
            return {"message": "If the email exists, an OTP has been sent to reset the password"}
        
        # Generate OTP
        code = generate_otp()
        expires_at = get_expiry(10)
        
        # Store OTP
        await create_otp(email, code, "RESET", expires_at)
        
        # Send email
        try:
            await send_otp_email(email, code, "RESET")
            logger.info(f"Reset OTP for {email} => {code}")
        except Exception as mail_err:
            logger.error(f"Error sending reset OTP email: {mail_err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP email. Try again."
            )
        
        return {"message": "If the email exists, an OTP has been sent to reset the password"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DB error on forgot-password-request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DB error"
        )


@router.post(
    "/forgot-password-verify",
    response_model=MessageResponse,
    summary="Verify OTP and Reset Password",
    description="Verify the OTP and reset the user's password."
)
async def forgot_password_verify(request: ForgotPasswordVerifyRequest):
    """Verify OTP and reset password."""
    try:
        email = normalize_email(request.email)
        
        # Get valid OTP
        otp_row = await get_valid_otp(email, request.otp, "RESET")
        
        if not otp_row:
            raise BadRequestException("Invalid OTP")
        
        # Check expiration
        if is_expired(otp_row["expires_at"]):
            raise BadRequestException("OTP expired")
        
        # Hash new password
        hashed_password = hash_password(request.newPassword)
        
        # Update password
        rows_updated = await update_user_password(email, hashed_password)
        
        if rows_updated == 0:
            logger.warning(f"Password reset for non-existing email: {email}")
            raise BadRequestException("User not found for this email")
        
        # Mark OTP as used
        await mark_otp_used(otp_row["id"])
        
        logger.info(f"Password reset successful for {email}")
        return {"message": "Password reset successful"}
        
    except BadRequestException:
        raise
    except Exception as e:
        logger.error(f"DB error on reset verify: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DB error"
        )


# ===========================================
# Google OAuth Endpoint
# ===========================================

@router.post(
    "/google",
    response_model=AuthResponse,
    summary="Google OAuth Login",
    description="Login or register using Google OAuth."
)
async def google_auth(request: GoogleAuthRequest):
    """Login or register with Google OAuth."""
    try:
        token = request.idToken or request.credential
        
        if not token:
            raise BadRequestException("idToken (or credential) is required")
        
        if not settings.GOOGLE_CLIENT_ID:
            logger.error("Google auth not configured on server.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google login is not configured on server."
            )
        
        # Verify Google token
        try:
            from google.oauth2 import id_token
            from google.auth.transport import requests as google_requests
            
            id_info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
        except Exception as verify_err:
            logger.error(f"Google token verification failed: {verify_err}")
            raise UnauthorizedException("Invalid Google token")
        
        # Extract user info
        google_id = id_info.get("sub")
        raw_email = id_info.get("email", "")
        email = normalize_email(raw_email)
        name = id_info.get("name") or email
        avatar = id_info.get("picture")
        
        if not email:
            raise BadRequestException("Google account does not have a valid email.")
        
        # Check if user exists
        user = await get_user_by_email_or_google_id(email, google_id)
        
        if not user:
            # Create new user
            dummy_password = hash_password(google_id + settings.JWT_SECRET)
            user = await create_user(
                name=name,
                email=email,
                password=dummy_password,
                role="user",
                is_verified=True,
                google_id=google_id,
                avatar=avatar
            )
            logger.info(f"Google login created new user: {email}")
        else:
            # Update existing user's Google info
            new_google_id = user.get("google_id") or google_id
            new_avatar = avatar or user.get("avatar")
            
            await update_user_google_info(user["id"], new_google_id, new_avatar)
            
            # Update local user dict
            user = dict(user)
            user["google_id"] = new_google_id
            user["avatar"] = new_avatar
            
            logger.info(f"Google login successful for existing user: {email}")
        
        # Generate JWT token
        role = user.get("role") or "user"
        jwt_token = create_access_token({
            "userId": user["id"],
            "email": user["email"] if hasattr(user, "__getitem__") else user.email,
            "name": user.get("name", name),
            "role": role
        })
        
        return {
            "message": "Login successful",
            "token": jwt_token,
            "user": {
                "id": user["id"],
                "name": user.get("name", name),
                "email": email,
                "role": role,
                "avatar": user.get("avatar") or avatar,
                "google_id": user.get("google_id") or google_id
            }
        }
        
    except (BadRequestException, UnauthorizedException):
        raise
    except Exception as e:
        logger.error(f"Error in /api/auth/google: {e}")
        raise UnauthorizedException("Invalid Google token")
