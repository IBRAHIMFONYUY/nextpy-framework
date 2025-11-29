"""
Hooks Provider for SSR Integration
Enables hooks to work seamlessly in server-side rendered pages
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class HooksContext:
    """Context for hooks across requests"""
    component_id: str
    state_data: Dict[str, Any]
    request_id: Optional[str] = None


class HooksProvider:
    """Global hooks provider for SSR"""
    
    _instance = None
    _request_contexts: Dict[str, HooksContext] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def create_context(cls, component_id: str, request_id: Optional[str] = None) -> HooksContext:
        """Create new hooks context for a request"""
        context = HooksContext(
            component_id=component_id,
            state_data={},
            request_id=request_id
        )
        if request_id:
            cls._request_contexts[request_id] = context
        return context
    
    @classmethod
    def get_context(cls, request_id: str) -> Optional[HooksContext]:
        """Get hooks context for a request"""
        return cls._request_contexts.get(request_id)
    
    @classmethod
    def cleanup_request(cls, request_id: str):
        """Clean up context after request"""
        if request_id in cls._request_contexts:
            del cls._request_contexts[request_id]


def with_hooks(component_id: str):
    """Decorator to enable hooks in page components"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            from nextpy.hooks import StateManager
            StateManager.set_component(component_id)
            try:
                return func(*args, **kwargs)
            finally:
                StateManager.reset_hook_index()
        return wrapper
    return decorator
