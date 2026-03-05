"""
API Route: /api/posts
Demonstrates API routes with FastAPI and Pydantic
"""

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class Post(BaseModel):
    """Post model with Pydantic validation"""
    id: Optional[int] = None
    title: str
    content: str
    author: str = "Anonymous"
    created_at: Optional[str] = None


POSTS_DB = [
    Post(id=1, title="Getting Started", content="Welcome to NextPy!", author="Admin", created_at="2024-11-28"),
    Post(id=2, title="File-based Routing", content="Learn about routing.", author="Admin", created_at="2024-11-25"),
    Post(id=3, title="Data Fetching", content="SSR and SSG patterns.", author="Admin", created_at="2024-11-20"),
]


async def get(request, params):
    """
    GET /api/posts
    Returns all posts
    """
    return {
        "posts": [post.model_dump() for post in POSTS_DB],
        "total": len(POSTS_DB)
    }


async def post(request, params):
    """
    POST /api/posts
    Create a new post
    """
    try:
        data = await request.json()
        new_post = Post(
            id=len(POSTS_DB) + 1,
            title=data.get("title", ""),
            content=data.get("content", ""),
            author=data.get("author", "Anonymous"),
            created_at=datetime.now().isoformat()
        )
        POSTS_DB.append(new_post)
        return {
            "success": True,
            "post": new_post.model_dump()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
