"""
Users API with Database
Example API routes using SQLAlchemy database
"""

from fastapi import HTTPException
from nextpy.db import get_session, User
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    is_active: bool


async def get(request):
    """GET /api/users - List all users"""
    session = get_session()
    try:
        users = session.query(User).all()
        return {
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "username": u.username,
                    "full_name": u.full_name,
                    "is_active": u.is_active
                }
                for u in users
            ]
        }
    finally:
        session.close()


async def post(request):
    """POST /api/users - Create user"""
    session = get_session()
    try:
        data = await request.json()
        user_data = UserCreate(**data)
        
        # Check if user exists
        existing = session.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password="hashed_password_here"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()
