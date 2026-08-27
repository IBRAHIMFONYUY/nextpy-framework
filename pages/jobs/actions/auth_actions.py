"""
Authentication server actions — register, login, logout, get_me.
All use cookie-based sessions. Response object is used to set/clear cookies.
"""

from fastapi import Request, Response
from nextpy.db import get_session, User
from nextpy.auth import (
    hash_password, verify_password,
    set_session_cookie, get_user_id_from_request, clear_session_cookie,
)
from nextpy.server_actions import server_action


@server_action()
async def register(
    request: Request,
    response: Response,
    email: str = "",
    username: str = "",
    full_name: str = "",
    password: str = "",
    role: str = "job_seeker",
):
    """Register a new user account."""
    email = (email or "").strip().lower()
    username = (username or "").strip()
    full_name = (full_name or "").strip()
    password = password or ""

    if not email or not username or not password:
        return {"success": False, "error": "All fields are required"}
    if len(password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters"}
    if role not in ("job_seeker", "employer"):
        role = "job_seeker"

    db = get_session()
    try:
        if db.query(User).filter(User.email == email).first():
            return {"success": False, "error": "Email already registered"}
        if db.query(User).filter(User.username == username).first():
            return {"success": False, "error": "Username already taken"}

        user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        set_session_cookie(response, user.id)
        return {
            "success": True,
            "user": {"id": user.id, "email": user.email, "username": user.username, "role": user.role},
            "message": "Account created successfully",
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@server_action()
async def login(
    request: Request,
    response: Response,
    email: str = "",
    password: str = "",
):
    """Log in an existing user."""
    email = (email or "").strip().lower()
    password = password or ""

    if not email or not password:
        return {"success": False, "error": "Email and password are required"}

    db = get_session()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None or not verify_password(password, user.hashed_password):
            return {"success": False, "error": "Invalid email or password"}

        set_session_cookie(response, user.id)
        return {
            "success": True,
            "user": {"id": user.id, "email": user.email, "username": user.username, "role": user.role},
            "message": "Logged in successfully",
        }
    finally:
        db.close()


@server_action()
async def logout(request: Request, response: Response):
    """Log out the current user by clearing the session cookie."""
    session_id = request.cookies.get("nextpy_session", "")
    if session_id:
        clear_session_cookie(response, session_id)
    else:
        response.delete_cookie("nextpy_session")
    return {"success": True, "message": "Logged out"}


@server_action()
async def get_me(request: Request):
    """Get the currently authenticated user, or null."""
    user_id = get_user_id_from_request(request)
    if user_id is None:
        return {"user": None}

    db = get_session()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return {"user": None}
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name or "",
                "role": user.role or "job_seeker",
            }
        }
    finally:
        db.close()
