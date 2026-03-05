"""
Contact Form API
Example of form submission with email and database storage
"""

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
from nextpy.db import get_session, Base
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime


class ContactMessage(Base):
    """Store contact messages"""
    __tablename__ = "contact_messages"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    subject = Column(String(255))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str


async def post(request):
    """POST /api/contact - Submit contact form"""
    session = get_session()
    try:
        data = await request.json()
        form = ContactForm(**data)
        
        # Save to database
        contact = ContactMessage(
            name=form.name,
            email=form.email,
            subject=form.subject,
            message=form.message
        )
        session.add(contact)
        session.commit()
        
        return {
            "success": True,
            "message": "Message received! We'll get back to you soon."
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()
