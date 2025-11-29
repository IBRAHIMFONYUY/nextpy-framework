"""
NextPy Email Utilities
Send emails via SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from nextpy.config import settings


async def send_email(
    to: List[str],
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
) -> bool:
    """Send email via SMTP"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.mail_username
        msg["To"] = ", ".join(to)
        
        if text_content:
            msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))
        
        with smtplib.SMTP(settings.mail_server, settings.mail_port) as server:
            server.starttls()
            server.login(settings.mail_username, settings.mail_password)
            server.sendmail(settings.mail_username, to, msg.as_string())
        
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False


async def send_welcome_email(email: str, name: str) -> bool:
    """Send welcome email"""
    html = f"""
    <h2>Welcome {name}!</h2>
    <p>Thanks for joining NextPy.</p>
    <p>Start building amazing apps today.</p>
    """
    return await send_email([email], "Welcome to NextPy", html)


async def send_reset_password_email(email: str, reset_link: str) -> bool:
    """Send password reset email"""
    html = f"""
    <h2>Reset Your Password</h2>
    <p>Click the link below to reset your password:</p>
    <a href="{reset_link}">Reset Password</a>
    <p>This link expires in 24 hours.</p>
    """
    return await send_email([email], "Reset Your Password", html)
