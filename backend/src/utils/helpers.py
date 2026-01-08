"""
Helper Functions
================
General utility functions used across the application.
"""

from urllib.parse import urlparse
from typing import List


def is_wikipedia_url(url: str) -> bool:
    """
    Check if a URL is a valid Wikipedia article URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid Wikipedia URL, False otherwise
    """
    try:
        parsed = urlparse(url)
        return (
            parsed.hostname is not None and
            parsed.hostname.endswith("wikipedia.org") and
            "/wiki/" in parsed.path
        )
    except Exception:
        return False


def normalize_email(email: str) -> str:
    """
    Normalize an email address.
    
    Args:
        email: Email address to normalize
        
    Returns:
        Lowercase, trimmed email address
    """
    if not email:
        return ""
    return email.strip().lower()


def parse_origins(origins_str: str) -> List[str]:
    """
    Parse a comma-separated string of origins into a list.
    
    Args:
        origins_str: Comma-separated origins string
        
    Returns:
        List of origin strings
    """
    if not origins_str:
        return ["*"]
    return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
