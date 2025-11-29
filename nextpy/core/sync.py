"""
NextPy Sync Support
Allow pages to be written with sync functions instead of async
"""

import asyncio
import inspect
from typing import Callable, Any, Dict


def sync_to_async(func: Callable) -> Callable:
    """Convert sync function to async"""
    if inspect.iscoroutinefunction(func):
        return func
    
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    
    return wrapper


async def run_sync(func: Callable, *args, **kwargs) -> Any:
    """Run sync function in async context"""
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


def supports_sync(func: Callable) -> bool:
    """Check if function supports sync"""
    return not inspect.iscoroutinefunction(func)
