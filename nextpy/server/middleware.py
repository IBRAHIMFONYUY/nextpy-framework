"""
NextPy Middleware - Request/Response middleware for the server
"""

import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class NextPyMiddleware(BaseHTTPMiddleware):
    """
    Core middleware for NextPy applications
    Handles:
    - Request timing
    - Cache headers
    - Security headers
    - HTMX detection
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        request.state.is_htmx = request.headers.get("HX-Request") == "true"
        request.state.htmx_target = request.headers.get("HX-Target")
        request.state.htmx_trigger = request.headers.get("HX-Trigger")
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        if request.state.is_htmx:
            response.headers["HX-Push-Url"] = str(request.url.path)
            
        return response


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Optional authentication middleware
    Can be added to protect routes
    """
    
    def __init__(self, app, protected_paths: list = None, login_path: str = "/login"):
        super().__init__(app)
        self.protected_paths = protected_paths or []
        self.login_path = login_path
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        
        for protected in self.protected_paths:
            if path.startswith(protected):
                session = request.cookies.get("session")
                if not session:
                    from starlette.responses import RedirectResponse
                    return RedirectResponse(
                        url=f"{self.login_path}?next={path}",
                        status_code=302,
                    )
                    
        return await call_next(request)


class CacheMiddleware(BaseHTTPMiddleware):
    """
    Caching middleware for static content
    """
    
    CACHE_EXTENSIONS = {".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        path = request.url.path
        
        if any(path.endswith(ext) for ext in self.CACHE_EXTENSIONS):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        elif path.startswith("/_nextpy/"):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
            
        return response
