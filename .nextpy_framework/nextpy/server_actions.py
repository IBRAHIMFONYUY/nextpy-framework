"""
NextPy Server Actions - Enhanced Client-Server Communication
Provides seamless server-side function execution from client components
"""

import asyncio
import inspect
import json
from typing import Any, Callable, Dict, Optional, TypeVar, get_type_hints
from functools import wraps
from datetime import datetime

from fastapi import Request, HTTPException
from nextpy.db import get_session
from nextpy.auth import AuthManager

T = TypeVar('T')


class ServerActionError(Exception):
    """Custom exception for server action errors"""
    def __init__(self, message: str, code: str = "SERVER_ACTION_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationError(Exception):
    """Validation error for server actions"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation failed for {field}: {message}")


class ServerAction:
    """
    Decorator and manager for server actions that can be called from client components
    Provides automatic serialization, validation, and error handling
    """
    
    _actions: Dict[str, Callable] = {}
    _validators: Dict[str, Callable] = {}
    
    @classmethod
    def register(cls, name: Optional[str] = None, validate: Optional[Callable] = None):
        """
        Decorator to register a server action
        
        Args:
            name: Custom action name (defaults to function name)
            validate: Optional validation function
        """
        def decorator(func: Callable) -> Callable:
            action_name = name or func.__name__
            cls._actions[action_name] = func
            if validate:
                cls._validators[action_name] = validate
            
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    # Run validation if provided
                    if validate:
                        validation_result = validate(**kwargs)
                        if validation_result is not True:
                            if isinstance(validation_result, dict):
                                raise ValidationError(
                                    validation_result.get('field', 'unknown'),
                                    validation_result.get('message', 'Validation failed')
                                )
                            else:
                                raise ValidationError('input', str(validation_result))
                    
                    # Execute the action
                    if inspect.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    return {
                        "success": True,
                        "data": result,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                except ValidationError as e:
                    return {
                        "success": False,
                        "error": {
                            "type": "validation",
                            "field": e.field,
                            "message": e.message
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }
                except ServerActionError as e:
                    return {
                        "success": False,
                        "error": {
                            "type": "server_action",
                            "code": e.code,
                            "message": e.message
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": {
                            "type": "internal",
                            "message": str(e)
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            # Store original function for direct access
            wrapper._original_func = func
            wrapper._action_name = action_name
            return wrapper
        
        return decorator
    
    @classmethod
    def get_action(cls, name: str) -> Optional[Callable]:
        """Get a registered action by name"""
        return cls._actions.get(name)
    
    @classmethod
    def list_actions(cls) -> Dict[str, str]:
        """List all registered actions with their docstrings"""
        return {
            name: (func.__doc__ or "No description").strip()
            for name, func in cls._actions.items()
        }
    
    @classmethod
    async def execute(cls, name: str, request: Request, response=None, params=None) -> Dict[str, Any]:
        """
        Execute a server action
        
        Args:
            name: Action name
            request: FastAPI request object
            response: FastAPI response object (for setting cookies, headers, etc.)
            params: Action parameters as dict
            
        Returns:
            Action result as dictionary
        """
        if params is None:
            params = {}
        
        action = cls.get_action(name)
        if not action:
            raise HTTPException(status_code=404, detail=f"Action '{name}' not found")
        
        # Build kwargs from params
        kwargs = dict(params)
        
        # Add request context if function accepts it
        sig = inspect.signature(action)
        if 'request' in sig.parameters:
            kwargs['request'] = request
        
        # Add response context if function accepts it
        if response is not None and 'response' in sig.parameters:
            kwargs['response'] = response
        
        # Add database session if function accepts it
        if 'session' in sig.parameters or 'db' in sig.parameters:
            kwargs['session'] = get_session()
        
        # Execute the wrapped function
        wrapper = cls._actions[name]
        if hasattr(wrapper, '_original_func'):
            # Call the wrapper with error handling
            if inspect.iscoroutinefunction(wrapper):
                return await wrapper(**kwargs)
            else:
                return wrapper(**kwargs)
        else:
            # Direct execution for backwards compatibility
            if inspect.iscoroutinefunction(action):
                result = await action(**kwargs)
            else:
                result = action(**kwargs)
            
            return {
                "success": True,
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            }


# Convenience decorator
server_action = ServerAction.register


# Built-in common server actions
@server_action()
async def get_health_status():
    """Health check action"""
    return {
        "status": "healthy",
        "version": "5.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@server_action()
async def get_current_user(request: Request):
    """Get currently authenticated user"""
    try:
        token = AuthManager.get_token_from_request(request)
        if token:
            user = AuthManager.verify_token(token)
            return {
                "id": user.get("id"),
                "email": user.get("email"),
                "username": user.get("username")
            }
        return None
    except Exception:
        return None


class FormValidator:
    """Form validation utilities for server actions"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if not any(c.isupper() for c in password):
            return False, "Password must contain uppercase letters"
        if not any(c.islower() for c in password):
            return False, "Password must contain lowercase letters"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain digits"
        return True, ""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: list) -> tuple[bool, str]:
        """Validate that required fields are present and non-empty"""
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Field '{field}' is required"
        return True, ""


# Schema-based validation
class ActionSchema:
    """Schema definition for server action validation"""
    
    def __init__(self, **fields):
        self.fields = fields
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, Optional[Dict[str, str]]]:
        """
        Validate data against schema
        
        Returns:
            Tuple of (is_valid, errors_dict)
        """
        errors = {}
        
        for field_name, field_config in self.fields.items():
            if field_name not in data:
                if field_config.get('required', False):
                    errors[field_name] = f"Field '{field_name}' is required"
                continue
            
            value = data[field_name]
            field_type = field_config.get('type')
            
            # Type validation
            if field_type and not isinstance(value, field_type):
                errors[field_name] = f"Field '{field_name}' must be of type {field_type.__name__}"
                continue
            
            # Custom validation
            if 'validator' in field_config:
                validator = field_config['validator']
                if callable(validator):
                    is_valid, error_msg = validator(value)
                    if not is_valid:
                        errors[field_name] = error_msg
        
        return len(errors) == 0, errors if errors else None


__all__ = [
    'ServerAction',
    'server_action', 
    'ServerActionError',
    'ValidationError',
    'FormValidator',
    'ActionSchema',
    'get_health_status',
    'get_current_user',
]