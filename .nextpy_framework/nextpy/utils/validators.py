"""
NextPy Validation Utilities
Type-safe validation helpers using Pydantic
"""

from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List, Dict, Any


class ContactForm(BaseModel):
    """Contact form validation"""
    name: str
    email: EmailStr
    message: str
    subject: Optional[str] = None


class BlogPost(BaseModel):
    """Blog post validation"""
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = None
    featured_image: Optional[HttpUrl] = None
    author: str
    tags: List[str] = []
    published: bool = False


class User(BaseModel):
    """User profile validation"""
    email: EmailStr
    username: str
    full_name: str
    bio: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None


class LoginForm(BaseModel):
    """Login form validation"""
    email: EmailStr
    password: str
    remember_me: bool = False


class SignupForm(BaseModel):
    """Signup form validation"""
    email: EmailStr
    username: str
    password: str
    confirm_password: str
    agree_to_terms: bool = False


def validate_slug(slug: str) -> bool:
    """Validate URL-safe slug format"""
    import re
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))
