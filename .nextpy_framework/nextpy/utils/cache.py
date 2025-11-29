"""
NextPy Caching Utilities
Simple in-memory cache with TTL support
"""

import time
from typing import Any, Optional, Dict, Callable
import functools


class Cache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self):
        self._store: Dict[str, tuple] = {}
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set cache value with TTL in seconds"""
        self._store[key] = (value, time.time() + ttl)
    
    def get(self, key: str) -> Optional[Any]:
        """Get cache value if not expired"""
        if key not in self._store:
            return None
        
        value, expiry = self._store[key]
        if time.time() > expiry:
            del self._store[key]
            return None
        
        return value
    
    def delete(self, key: str):
        """Delete cache value"""
        if key in self._store:
            del self._store[key]
    
    def clear(self):
        """Clear all cache"""
        self._store.clear()
    
    def cleanup_expired(self):
        """Remove expired entries"""
        now = time.time()
        expired = [k for k, (_, expiry) in self._store.items() if now > expiry]
        for k in expired:
            del self._store[k]


# Global cache instance
_cache = Cache()


def get_cache() -> Cache:
    """Get global cache instance"""
    return _cache


def cache_result(ttl: int = 3600):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = _cache.get(key)
            if cached is not None:
                return cached
            result = await func(*args, **kwargs)
            _cache.set(key, result, ttl)
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = _cache.get(key)
            if cached is not None:
                return cached
            result = func(*args, **kwargs)
            _cache.set(key, result, ttl)
            return result
        
        if hasattr(func, '__call__'):
            import inspect
            if inspect.iscoroutinefunction(func):
                return async_wrapper
        
        return sync_wrapper
    
    return decorator
