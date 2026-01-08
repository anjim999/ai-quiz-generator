"""
Email Mailer Module
===================
Send emails using Brevo API.
"""

import logging
import httpx
from typing import Dict, Any, Optional
from src.core import settings

logger = logging.getLogger(__name__)


async def send_otp_email(
    to: str,
    otp: str,
    purpose: str
) -> Dict[str, Any]:
    """
    Send an OTP email using Brevo API.
    
    Args:
        to: Recipient email address
        otp: OTP code
        purpose: 'REGISTER' or 'RESET'
        
    Returns:
        Dict with 'success' boolean and optional 'error'
    """
    
    if not settings.BREVO_API_KEY:
        logger.warning("Brevo API key not configured, skipping email send")
        return {"success": False, "error": "Email service not configured"}
    
    try:
        # Determine email subject based on purpose
        if purpose == "REGISTER":
            subject = "Your Registration OTP - AI Quiz Generator"
        else:
            subject = "Your Password Reset OTP - AI Quiz Generator"
        
        # Create HTML content
        html_content = f"""
        <div style="font-family: Arial, sans-serif; font-size: 14px; color: #333; max-width: 500px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4F46E5;">AI Quiz Generator</h2>
            <p><strong>Your OTP Code:</strong></p>
            <h1 style="letter-spacing: 8px; font-size: 36px; color: #1F2937; background: #F3F4F6; padding: 20px; text-align: center; border-radius: 8px;">{otp}</h1>
            <p style="color: #6B7280;">This OTP is valid for <strong>10 minutes</strong>.</p>
            <p style="color: #6B7280;">If you didn't request this code, please ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
            <p style="font-size: 12px; color: #9CA3AF;">This is an automated message from AI Quiz Generator.</p>
        </div>
        """
        
        # Parse sender from EMAIL_FROM
        email_from = settings.EMAIL_FROM
        if "<" in email_from:
            sender_name, sender_email_raw = email_from.split("<")
            sender_email = sender_email_raw.replace(">", "").strip()
            sender_name = sender_name.strip().strip('"')
        else:
            sender_email = email_from
            sender_name = "AI Quiz Generator"
        
        # Prepare request body
        body = {
            "sender": {
                "email": sender_email,
                "name": sender_name
            },
            "to": [{"email": to}],
            "subject": subject,
            "htmlContent": html_content
        }
        
        # Send request to Brevo API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                json=body,
                headers={
                    "Content-Type": "application/json",
                    "api-key": settings.BREVO_API_KEY
                },
                timeout=30.0
            )
            
            if response.status_code >= 400:
                logger.error(f"Brevo API error: {response.status_code} - {response.text}")
                return {"success": False, "error": f"Brevo API error: {response.status_code}"}
            
            data = response.json()
            logger.info(f"OTP email sent via Brevo API: {data.get('messageId', data)}")
            return {"success": True}
            
    except Exception as e:
        logger.error(f"Error sending Brevo email: {e}")
        return {"success": False, "error": str(e)}
