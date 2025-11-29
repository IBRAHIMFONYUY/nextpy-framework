"""
NextPy Server Application - FastAPI-based server
Handles routing, SSR, API routes, and static file serving
"""

import os
import asyncio
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from nextpy.core.router import Router
from nextpy.core.renderer import Renderer
from nextpy.core.data_fetching import (
    PageContext,
    execute_data_fetching,
    PageNotFoundError,
    RedirectError,
)
from nextpy.server.middleware import NextPyMiddleware


class NextPyApp:
    """
    Main NextPy application class
    Wraps FastAPI and provides Next.js-like functionality
    """
    
    def __init__(
        self,
        pages_dir: str = "pages",
        templates_dir: str = "templates",
        public_dir: str = "public",
        out_dir: str = "out",
        debug: bool = False,
    ):
        self.pages_dir = Path(pages_dir)
        self.templates_dir = Path(templates_dir)
        self.public_dir = Path(public_dir)
        self.out_dir = Path(out_dir)
        self.debug = debug
        
        self.router = Router(str(self.pages_dir), str(self.templates_dir))
        self.renderer = Renderer(
            str(self.templates_dir),
            str(self.pages_dir),
            str(self.public_dir),
        )
        
        self.app = FastAPI(
            title="NextPy Application",
            debug=debug,
        )
        
        self._setup_middleware()
        self._setup_static_files()
        self._setup_routes()
        
    def _setup_middleware(self) -> None:
        """Configure middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.app.add_middleware(NextPyMiddleware)
        
    def _setup_static_files(self) -> None:
        """Mount static file directories"""
        if self.public_dir.exists():
            self.app.mount(
                "/static",
                StaticFiles(directory=str(self.public_dir)),
                name="static",
            )
            
        nextpy_static = self.out_dir / "_nextpy" / "static"
        if nextpy_static.exists():
            self.app.mount(
                "/_nextpy/static",
                StaticFiles(directory=str(nextpy_static)),
                name="nextpy_static",
            )
            
    def _setup_routes(self) -> None:
        """Set up the catch-all route handler"""
        self.router.scan_pages()
        
        for route in self.router.api_routes:
            self._register_api_route(route)
            
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def catch_all(request: Request, path: str = "") -> Response:
            return await self._handle_request(request, f"/{path}")
            
        @self.app.get("/")
        async def index(request: Request) -> Response:
            return await self._handle_request(request, "/")
            
    def _register_api_route(self, route) -> None:
        """Register an API route with FastAPI"""
        if route.handler:
            methods = self._get_handler_methods(route.handler)
            
            @self.app.api_route(route.path, methods=methods)
            async def api_handler(request: Request) -> Response:
                return await self._handle_api_request(request, route)
                
    def _get_handler_methods(self, handler: Callable) -> list:
        """Get HTTP methods supported by a handler"""
        methods = []
        module = handler.__module__ if hasattr(handler, "__module__") else None
        
        if module:
            import sys
            mod = sys.modules.get(module)
            if mod:
                if hasattr(mod, "get") or hasattr(mod, "GET"):
                    methods.append("GET")
                if hasattr(mod, "post") or hasattr(mod, "POST"):
                    methods.append("POST")
                if hasattr(mod, "put") or hasattr(mod, "PUT"):
                    methods.append("PUT")
                if hasattr(mod, "delete") or hasattr(mod, "DELETE"):
                    methods.append("DELETE")
                if hasattr(mod, "patch") or hasattr(mod, "PATCH"):
                    methods.append("PATCH")
                    
        return methods or ["GET", "POST"]
        
    async def _handle_request(self, request: Request, path: str) -> Response:
        """Handle a page request"""
        match = self.router.match(path)
        
        if not match:
            return await self._render_404(request)
            
        route, params = match
        
        if route.is_api:
            return await self._handle_api_request(request, route, params)
            
        context = PageContext(
            params=params,
            query=dict(request.query_params),
            req=request,
        )
        
        try:
            props = {}
            if route.handler:
                module = self._get_module_from_handler(route.handler)
                if module:
                    props = await execute_data_fetching(module, context)
                    
            template_name = self._get_template_name(route)
            
            html = await self.renderer.render_async(
                template_name,
                context={
                    **props,
                    "params": params,
                    "query": dict(request.query_params),
                    "request": request,
                },
                layout="_base.html" if (self.templates_dir / "_base.html").exists() else None,
            )
            
            return HTMLResponse(
                content=html,
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                },
            )
            
        except PageNotFoundError:
            return await self._render_404(request)
            
        except RedirectError as e:
            status_code = 308 if e.permanent else 307
            return RedirectResponse(url=e.destination, status_code=status_code)
            
        except Exception as e:
            if self.debug:
                raise
            return await self._render_error(request, e)
            
    async def _handle_api_request(
        self, 
        request: Request, 
        route,
        params: Optional[Dict[str, str]] = None
    ) -> Response:
        """Handle an API route request"""
        params = params or {}
        
        if not route.handler:
            return JSONResponse(
                {"error": "Handler not found"},
                status_code=500,
            )
            
        module = self._get_module_from_handler(route.handler)
        if not module:
            return JSONResponse(
                {"error": "Module not found"},
                status_code=500,
            )
            
        method = request.method.lower()
        handler = getattr(module, method, None) or getattr(module, method.upper(), None)
        
        if not handler:
            handler = getattr(module, "handler", None) or getattr(module, "default", None)
            
        if not handler:
            return JSONResponse(
                {"error": f"No handler for {request.method}"},
                status_code=405,
            )
            
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(request, params)
            else:
                result = handler(request, params)
                
            if isinstance(result, Response):
                return result
            elif isinstance(result, dict):
                return JSONResponse(result)
            else:
                return JSONResponse({"data": result})
                
        except Exception as e:
            if self.debug:
                raise
            return JSONResponse(
                {"error": str(e)},
                status_code=500,
            )
            
    def _get_module_from_handler(self, handler: Callable) -> Optional[Any]:
        """Get the module that contains the handler"""
        if hasattr(handler, "__module__"):
            import sys
            return sys.modules.get(handler.__module__)
        return None
        
    def _get_template_name(self, route) -> str:
        """Get the template name for a route"""
        relative = route.file_path.relative_to(self.pages_dir)
        template_name = str(relative).replace(".py", ".html")
        
        template_path = self.templates_dir / template_name
        if template_path.exists():
            return template_name
            
        if route.file_path.stem == "index":
            parent_template = self.templates_dir / route.file_path.parent.name / "index.html"
            if parent_template.exists():
                return str(parent_template.relative_to(self.templates_dir))
                
        return "_page.html"
        
    async def _render_404(self, request: Request) -> HTMLResponse:
        """Render the 404 page"""
        try:
            html = await self.renderer.render_async(
                "_404.html",
                context={"request": request},
            )
        except Exception:
            html = """
            <!DOCTYPE html>
            <html>
            <head><title>404 - Not Found</title></head>
            <body>
                <h1>404 - Page Not Found</h1>
                <p>The page you're looking for doesn't exist.</p>
            </body>
            </html>
            """
        return HTMLResponse(content=html, status_code=404)
        
    async def _render_error(self, request: Request, error: Exception) -> HTMLResponse:
        """Render the error page"""
        try:
            html = await self.renderer.render_async(
                "_error.html",
                context={"request": request, "error": str(error)},
            )
        except Exception:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>500 - Server Error</title></head>
            <body>
                <h1>500 - Server Error</h1>
                <p>An error occurred while processing your request.</p>
            </body>
            </html>
            """
        return HTMLResponse(content=html, status_code=500)
        
    def reload_routes(self) -> None:
        """Reload all routes (for hot reload)"""
        self.router = Router(str(self.pages_dir), str(self.templates_dir))
        self.router.scan_pages()


def create_app(
    pages_dir: str = "pages",
    templates_dir: str = "templates",
    public_dir: str = "public",
    out_dir: str = "out",
    debug: bool = False,
) -> FastAPI:
    """
    Factory function to create a NextPy application
    
    Args:
        pages_dir: Directory containing page files
        templates_dir: Directory containing Jinja2 templates
        public_dir: Directory containing static files
        out_dir: Directory for SSG output
        debug: Enable debug mode
        
    Returns:
        FastAPI application instance
    """
    nextpy_app = NextPyApp(
        pages_dir=pages_dir,
        templates_dir=templates_dir,
        public_dir=public_dir,
        out_dir=out_dir,
        debug=debug,
    )
    return nextpy_app.app
