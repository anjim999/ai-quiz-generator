"""
OTP Utilities
=============
One-Time Password generation and management.
"""

import random
import string
from datetime import datetime, timedelta, timezone


def generate_otp(length: int = 6) -> str:
    """
    Generate a random numeric OTP.
    
    Args:
        length: Length of the OTP (default: 6)
        
    Returns:
        Random numeric string of specified length
    """
    return ''.join(random.choices(string.digits, k=length))


def get_expiry(minutes: int = 10) -> datetime:
    """
    Get an expiry timestamp for OTP.
    
    Args:
        minutes: Minutes until expiry (default: 10)
        
    Returns:
        datetime object with UTC timezone
    """
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def is_expired(expires_at: str) -> bool:
    """
    Check if an expiry timestamp has passed.
    
    Args:
        expires_at: ISO format timestamp string
        
    Returns:
        True if expired, False otherwise
    """
    try:
        # Handle both datetime objects and strings
        if isinstance(expires_at, datetime):
            expiry = expires_at
        else:
            expiry = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        
        # Make sure both are timezone-aware for comparison
        now = datetime.now(timezone.utc)
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
            
        return expiry < now
    except Exception:
        return True  # If we can't parse, assume expired
