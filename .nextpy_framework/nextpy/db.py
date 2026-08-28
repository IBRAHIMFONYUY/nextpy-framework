"""
NextPy Database Layer
Support for SQLite, PostgreSQL, MySQL with SQLAlchemy ORM
"""

import os
from typing import Optional, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import declarative_base

Base = declarative_base()
Model = Base


class DatabaseConfig:
    """Database configuration manager"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./nextpy.db")
        self.echo = os.getenv("DB_ECHO", "false").lower() == "true"
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "5"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        
    def get_engine(self):
        """Get SQLAlchemy engine"""
        if self.database_url.startswith("sqlite"):
            return create_engine(
                self.database_url,
                echo=self.echo,
                connect_args={"check_same_thread": False}
            )
        else:
            return create_engine(
                self.database_url,
                echo=self.echo,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_pre_ping=True
            )


class Database:
    """Database manager with connection pooling"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.config = DatabaseConfig(database_url)
        self.engine = self.config.get_engine()
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
    
    def drop_tables(self):
        """Drop all tables (development only)"""
        Base.metadata.drop_all(self.engine)
    
    def close(self):
        """Close connection pool"""
        self.engine.dispose() 


# Global database instance
_db: Optional[Database] = None


def init_db(database_url: Optional[str] = None) -> Database:
    """Initialize global database instance"""
    global _db
    _db = Database(database_url)
    _db.create_tables()
    return _db


def get_db() -> Database:
    """Get global database instance"""
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db


def get_session() -> Session:
    """Get database session"""
    return get_db().get_session()


def session() -> Session:
    """Return a database session using the native NextPy API name."""
    return get_session()


# Models example
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(255), unique=True, index=True)
    full_name = Column(String(255))
    hashed_password = Column(String(255))
    role = Column(String(50), default="job_seeker")  # job_seeker | employer
    bio = Column(Text, default="")
    company_name = Column(String(255), default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Post(Base):
    """Blog post model"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), index=True)
    slug = Column(String(255), unique=True, index=True)
    content = Column(Text)
    excerpt = Column(String(500))
    author_id = Column(Integer, index=True)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Todo(Base):
    """Persistent todo item shared by the API, PSX pages, and admin."""
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, index=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)




class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(200))
    description = Column(Text, nullable=False)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    job_type = Column(String(50), default="full_time")  # full_time | part_time | contract | internship
    experience_level = Column(String(50), default="mid")  # entry | mid | senior | lead
    employer_id = Column(Integer, index=True)  # FK to users.id
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, index=True)
    applicant_id = Column(Integer, index=True)  # FK to users.id
    cover_letter = Column(Text, default="")
    resume_url = Column(String(500), default="")
    status = Column(String(50), default="pending")  # pending | accepted | rejected
    created_at = Column(DateTime, default=datetime.utcnow)