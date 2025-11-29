"""
NextPy Configuration Manager
Environment variables, settings, and configuration
"""

import os
from typing import Optional, Any
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App
    app_name: str = "NextPy App"
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    domain: str = os.getenv("DOMAIN", "localhost:5000")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./nextpy.db")
    db_echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    
    # Auth
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    session_secret: str = os.getenv("SESSION_SECRET", "change-me")
    
    # Email
    mail_server: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    mail_port: int = int(os.getenv("MAIL_PORT", "587"))
    mail_username: str = os.getenv("MAIL_USERNAME", "")
    mail_password: str = os.getenv("MAIL_PASSWORD", "")
    
    # API Keys
    api_key: Optional[str] = os.getenv("API_KEY")
    stripe_key: Optional[str] = os.getenv("STRIPE_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # URLs
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5000")
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:5000")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_setting(key: str, default: Any = None) -> Any:
    """Get setting by key"""
    return getattr(settings, key, default)


def get_env(key: str, default: Any = None) -> Any:
    """Get environment variable"""
    return os.getenv(key, default)


def is_production() -> bool:
    """Check if running in production"""
    return not settings.debug


def is_development() -> bool:
    """Check if running in development"""
    return settings.debug
