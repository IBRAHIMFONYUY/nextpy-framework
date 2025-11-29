"""
NextPy Error Handling
Custom exceptions and error utilities
"""

from typing import Optional, Dict, Any


class NextPyException(Exception):
    """Base NextPy exception"""
    pass


class RouteNotFound(NextPyException):
    """Route not found"""
    pass


class TemplateNotFound(NextPyException):
    """Template not found"""
    pass


class DatabaseError(NextPyException):
    """Database connection error"""
    pass


class AuthenticationError(NextPyException):
    """Authentication failed"""
    pass


class ValidationError(NextPyException):
    """Validation failed"""
    
    def __init__(self, message: str, errors: Optional[Dict[str, str]] = None):
        self.message = message
        self.errors = errors or {}
        super().__init__(message)


class RateLimitError(NextPyException):
    """Rate limit exceeded"""
    pass


def handle_error(error: Exception) -> Dict[str, Any]:
    """Convert error to response dict"""
    if isinstance(error, ValidationError):
        return {
            "error": error.message,
            "details": error.errors,
            "status": 400
        }
    elif isinstance(error, AuthenticationError):
        return {
            "error": str(error),
            "status": 401
        }
    elif isinstance(error, RateLimitError):
        return {
            "error": str(error),
            "status": 429
        }
    else:
        return {
            "error": str(error),
            "status": 500
        }
