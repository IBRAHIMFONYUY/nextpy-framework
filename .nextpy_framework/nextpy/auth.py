"""
NextPy Authentication - JWT, Session, and Password support
"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from fastapi import HTTPException, Request, Response
from nextpy.config import settings


# ---------------------------------------------------------------------------
# Password hashing (HMAC-SHA256 with random salt — no bcrypt dependency)
# ---------------------------------------------------------------------------
_HASH_ITERATIONS = 260_000


def hash_password(password: str) -> str:
    """Hash a password with a random salt.  Returns ``salt$hash``."""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _HASH_ITERATIONS)
    return f"{salt}${dk.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a ``salt$hash`` string."""
    try:
        salt, expected_hex = hashed.split("$", 1)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _HASH_ITERATIONS)
        return secrets.compare_digest(dk.hex(), expected_hex)
    except Exception:
        return False


class AuthManager:
    """Handle JWT and session authentication"""
    
    @staticmethod
    def create_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT token"""
        if expires_delta is None:
            expires_delta = timedelta(hours=settings.jwt_expiration_hours)
        
        expire = datetime.utcnow() + expires_delta
        payload = {"user_id": user_id, "exp": expire}
        
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    
    @staticmethod
    def verify_token(token: str) -> Optional[int]:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            user_id = payload.get("user_id")
            if user_id is None:
                return None
            return user_id
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    @staticmethod
    def get_token_from_request(request: Request) -> Optional[str]:
        """Extract token from Authorization header"""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        return None


def require_auth(func):
    """Decorator to require authentication"""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        token = AuthManager.get_token_from_request(request)
        if not token:
            raise HTTPException(status_code=401, detail="Missing token")
        
        user_id = AuthManager.verify_token(token)
        request.state.user_id = user_id
        return await func(request, *args, **kwargs)
    
    return wrapper


# Session storage (in-memory, use Redis for production)
_sessions: Dict[str, Dict[str, Any]] = {}


def create_session(user_id: int) -> str:
    """Create session"""
    import uuid
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=24)
    }
    return session_id


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session"""
    session = _sessions.get(session_id)
    if session and session["expires_at"] > datetime.utcnow():
        return session
    return None


def delete_session(session_id: str) -> bool:
    """Delete session"""
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False


# ---------------------------------------------------------------------------
# Cookie-based session helpers (for server actions / API routes)
# ---------------------------------------------------------------------------

COOKIE_NAME = "nextpy_session"
COOKIE_MAX_AGE = 86400  # 24 hours


def set_session_cookie(response: Response, user_id: int) -> str:
    """Create a session and set it as an HTTP cookie on *response*."""
    session_id = create_session(user_id)
    response.set_cookie(
        COOKIE_NAME,
        session_id,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    return session_id


def get_user_id_from_request(request: Request) -> Optional[int]:
    """Extract the authenticated user-id from the session cookie.

    Returns ``None`` when not authenticated.
    """
    session_id = request.cookies.get(COOKIE_NAME)
    if not session_id:
        return None
    sess = get_session(session_id)
    if sess is None:
        return None
    return sess.get("user_id")


def clear_session_cookie(response: Response, session_id: str) -> None:
    """Delete the session cookie and the server-side session."""
    delete_session(session_id)
    response.delete_cookie(COOKIE_NAME)
