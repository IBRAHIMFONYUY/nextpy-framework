"""
Login API with JWT authentication
"""

from pydantic import BaseModel, EmailStr
from nextpy.auth import AuthManager
from fastapi import HTTPException


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


async def post(request):
    """POST /api/login - Authenticate user and return JWT token"""
    data = await request.json()
    form = LoginRequest(**data)
    
    # TODO: Verify against database
    # For demo, accept any email with password "password"
    if form.password != "password":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    user_id = hash(form.email) % 1000  # Simple demo user_id
    token = AuthManager.create_token(user_id)
    
    return {
        "token": token,
        "user_id": user_id,
        "type": "bearer"
    }
