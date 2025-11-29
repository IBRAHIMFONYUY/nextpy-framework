"""
NextPy Performance Optimization
Decorators and utilities for performance monitoring and optimization
"""

import time
import functools
from typing import Callable, Any
import asyncio


def timeit(func: Callable) -> Callable:
    """Decorator to measure execution time"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.3f}s")
        return result
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.3f}s")
        return result
    
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def batch_processor(batch_size: int = 100):
    """Process items in batches for performance"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(items: list) -> list:
            results = []
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                batch_results = await asyncio.gather(*[func(item) for item in batch])
                results.extend(batch_results)
            return results
        return wrapper
    return decorator


class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        cutoff = now - self.window_seconds
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff]
        
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True
        
        return False


# Global rate limiter
rate_limiter = RateLimiter()
