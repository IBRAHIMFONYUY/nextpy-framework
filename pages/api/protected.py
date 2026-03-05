"""Protected API endpoint - requires authentication"""

from fastapi import HTTPException, Request


async def get(request: Request):
    """Protected endpoint requiring Authorization header"""
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = auth_header[7:]
    
    # Verify token
    from nextpy.auth import AuthManager
    try:
        user_id = AuthManager.verify_token(token)
        return {
            "message": "Access granted",
            "user_id": user_id,
            "protected_data": "This is protected"
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
