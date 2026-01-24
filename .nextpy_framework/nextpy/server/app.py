"""
NextPy Server Application - FastAPI-based server
Handles routing, SSR, API routes, and static file serving
"""

import os
import sys
import asyncio
import importlib.util
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from nextpy.core.router import Router
from nextpy.core.component_router import ComponentRouter, ComponentRoute
from nextpy.core.demo_router import demo_router
from nextpy.core.component_renderer import ComponentRenderer, render_api, render_component
from nextpy.core.data_fetching import (
    PageContext,
    execute_data_fetching,
    PageNotFoundError,
    RedirectError,
)
from nextpy.server.middleware import NextPyMiddleware
from nextpy.security import security_manager
from nextpy.jsx_preprocessor import JSXSyntaxError


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
        self._modules_cache: Dict[str, Any] = {}
        
        if demo_router.should_serve_demo():
            self.router = Router(str(self.pages_dir), str(self.templates_dir))
        else:
            self.router = ComponentRouter(str(self.pages_dir), str(self.templates_dir))
        self.renderer = ComponentRenderer(
            debug=debug
        )
        
        # Scan pages for routes
        self.router.scan_pages()
        
        # Check if we should enable demo mode
        if isinstance(self.router, Router) and demo_router.should_serve_demo():
            self.router.enable_demo_mode()
            print("🎉 NextPy Demo Mode - No project detected")
            print("📚 Showing built-in documentation and examples")
            print("💡 Create a project with: nextpy create my-app")
        
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
        
        # Add security headers middleware
        @self.app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            
            # Add Content Security Policy
            csp_header = security_manager.create_csp_header()
            response.headers["Content-Security-Policy"] = csp_header
            
            # Add other security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
            
            return response
        
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
        """Setup page routes using the router"""
        # Add all routes from the router
        for route in self.router.get_all_routes():
            if route.is_api:
                # API routes - FIXED: use default argument to capture route correctly
                def create_api_handler(route_obj):
                    def api_handler(request, route=route_obj):
                        return self._handle_api_request(request, route, {})
                    return api_handler
                
                self.app.add_api_route(
                    route.path,
                    create_api_handler(route),
                    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
                )
            else:
                # Page routes - FIXED: use default argument to capture route correctly
                def create_page_handler(route_path):
                    async def page_handler(request, path=route_path):
                        return await self._handle_request(request, path)
                    return page_handler
                
                self.app.add_route(
                    route.path,
                    create_page_handler(route.path),
                    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
                )
        
    def _load_module_from_file(self, file_path: Path) -> Optional[Any]:
        """Load a Python module from a file path with caching"""
        try:
            # Convert relative path to absolute path
            if not file_path.is_absolute():
                file_path = Path.cwd() / file_path
            
            # Create cache key
            cache_key = str(file_path.resolve())
            
            # Check cache first (unless in debug mode)
            if not self.debug and cache_key in self._modules_cache:
                return self._modules_cache[cache_key]
            
            module_name = f"nextpy_page_{file_path.stem}_{hash(str(file_path))}"
            
            # Use JSX transformer for JSX files
            from nextpy.jsx_transformer import JSXTransformer
            transformer = JSXTransformer()
            module = transformer.load_jsx_module(file_path, module_name)
            
            # Cache the module (unless in debug mode)
            if module and not self.debug:
                self._modules_cache[cache_key] = module
            
            return module
            
        except Exception as e:
            if self.debug:
                print(f"Error loading module from {file_path}: {e}")
        return None
        
    async def _handle_request(self, request: Request, path: str) -> Response:
        """Handle a page request"""
        match = self.router.match(path)
        
        if not match:
            return await self._render_404(request)
            
        route, params = match
        
        # Handle demo pages differently
        if hasattr(self.router, "is_demo_mode") and self.router.is_demo_mode() and str(route.file_path) == "demo":
            return await self._handle_demo_page(request, route, params)
        
        if route.is_api:
            return await self._handle_api_request(request, route, params)
            
        if isinstance(route, ComponentRoute) and getattr(route, "use_components", False):
            html = self.router.render_route(
                route,
                context={
                    "params": params,
                    "query": dict(request.query_params),
                    "request": request,
                },
            )
            return HTMLResponse(
                content=html,
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                },
            )
            
        context = PageContext(
            params=params,
            query=dict(request.query_params),
            req=request,
        )
        
        try:
            props = {}
            module = self._load_module_from_file(route.file_path)
            
            if module:
                props = await execute_data_fetching(module, context)
                
                # Execute the page component to get JSX
                content = ""
                if hasattr(module, 'default'):
                    component = module.default
                    component_props = {**props, "params": params}
                    jsx_element = component(component_props)
                    
                    # Convert JSX to HTML
                    try:
                        from nextpy.jsx import render_jsx
                        content = render_jsx(jsx_element)
                    except ImportError:
                        # Fail fast - JSX renderer is required
                        raise RuntimeError("JSX renderer not available. Please install nextpy.jsx module.")
                        
            template_name = self._get_template_name(route, module)
            
            html = await self.renderer.render_async(
                template_name,
                context={
                    **props,
                    "content": content,
                    "params": params,
                    "query": dict(request.query_params),
                    "request": request,
                },
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
                import traceback
                traceback.print_exc()
            return await self._render_error(request, e)
            
    async def _handle_api_request(
        self, 
        request: Request, 
        route,
        params: Optional[Dict[str, str]] = None
    ) -> Response:
        """Handle an API route request"""
        params = params or {}
        
        module = self._load_module_from_file(route.file_path)
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
                import traceback
                traceback.print_exc()
            return JSONResponse(
                {"error": str(e)},
                status_code=500,
            )
        
    def _get_template_name(self, route, module: Optional[Any] = None) -> str:
        """Get the template name for a route"""
        if module and hasattr(module, "get_template"):
            return module.get_template()
            
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
        """Render enhanced error pages based on error type"""
        try:
            # Handle specific error types
            if isinstance(error, JSXSyntaxError):
                return await self._render_jsx_error_page(request, error)
            elif isinstance(error, ImportError):
                return await self._render_import_error_page(request, error)
            elif isinstance(error, (ValueError, TypeError)):
                return await self._render_value_error_page(request, error)
            elif isinstance(error, (AttributeError, KeyError)):
                return await self._render_attribute_error_page(request, error)
            elif isinstance(error, (FileNotFoundError, OSError)):
                return await self._render_file_error_page(request, error)
            elif isinstance(error, (ConnectionError, TimeoutError)):
                return await self._render_network_error_page(request, error)
            else:
                return await self._render_generic_error_page(request, error)
                
        except Exception as fallback_error:
            # Ultimate fallback if error page rendering fails
            return HTMLResponse(
                content=self._get_emergency_error_html(error, fallback_error),
                status_code=500
            )
    
    async def _render_jsx_error_page(self, request: Request, error: JSXSyntaxError) -> HTMLResponse:
        """Render JSX syntax error page"""
        error_details = {
            "message": error.message,
            "file_path": error.file_path,
            "line_number": error.line_number,
            "column": error.column,
            "error_type": "JSX Syntax Error"
        }
        
        try:
            html = await self.renderer.render_async(
                "_jsx_error.html",
                context={
                    "request": request,
                    "error": error_details,
                    "debug": self.debug
                },
            )
        except Exception:
            html = self._get_jsx_error_html(error_details)
            
        return HTMLResponse(content=html, status_code=500)
    
    async def _render_import_error_page(self, request: Request, error: ImportError) -> HTMLResponse:
        """Render import error page"""
        error_details = {
            "message": str(error),
            "error_type": "Import Error",
            "suggestions": self._get_import_error_suggestions(error)
        }
        
        try:
            html = await self.renderer.render_async(
                "_import_error.html",
                context={
                    "request": request,
                    "error": error_details,
                    "debug": self.debug
                },
            )
        except Exception:
            html = self._get_import_error_html(error_details)
            
        return HTMLResponse(content=html, status_code=500)
    
    async def _render_value_error_page(self, request: Request, error: Exception) -> HTMLResponse:
        """Render value/type error page"""
        error_details = {
            "message": str(error),
            "error_type": type(error).__name__,
            "error_class": error.__class__.__name__
        }
        
        try:
            html = await self.renderer.render_async(
                "_value_error.html",
                context={
                    "request": request,
                    "error": error_details,
                    "debug": self.debug
                },
            )
        except Exception:
            html = self._get_value_error_html(error_details)
            
        return HTMLResponse(content=html, status_code=500)
    
    async def _render_attribute_error_page(self, request: Request, error: Exception) -> HTMLResponse:
        """Render attribute/key error page"""
        error_details = {
            "message": str(error),
            "error_type": type(error).__name__,
            "missing_attribute": self._extract_missing_attribute(error)
        }
        
        try:
            html = await self.renderer.render_async(
                "_attribute_error.html",
                context={
                    "request": request,
                    "error": error_details,
                    "debug": self.debug
                },
            )
        except Exception:
            html = self._get_attribute_error_html(error_details)
            
        return HTMLResponse(content=html, status_code=500)
    
    async def _render_file_error_page(self, request: Request, error: Exception) -> HTMLResponse:
        """Render file system error page"""
        error_details = {
            "message": str(error),
            "error_type": type(error).__name__,
            "file_path": self._extract_file_path_from_error(error)
        }
        
        try:
            html = await self.renderer.render_async(
                "_file_error.html",
                context={
                    "request": request,
                    "error": error_details,
                    "debug": self.debug
                },
            )
        except Exception:
            html = self._get_file_error_html(error_details)
            
        return HTMLResponse(content=html, status_code=500)
    
    async def _render_network_error_page(self, request: Request, error: Exception) -> HTMLResponse:
        """Render network/timeout error page"""
        error_details = {
            "message": str(error),
            "error_type": type(error).__name__,
            "retry_possible": True
        }
        
        try:
            html = await self.renderer.render_async(
                "_network_error.html",
                context={
                    "request": request,
                    "error": error_details,
                    "debug": self.debug
                },
            )
        except Exception:
            html = self._get_network_error_html(error_details)
            
        return HTMLResponse(content=html, status_code=503)
    
    async def _render_generic_error_page(self, request: Request, error: Exception) -> HTMLResponse:
        """Render generic error page"""
        error_details = {
            "message": str(error),
            "error_type": type(error).__name__,
            "error_class": error.__class__.__name__
        }
        
        if self.debug:
            import traceback
            error_details["traceback"] = traceback.format_exc()
        
        try:
            html = await self.renderer.render_async(
                "_error.html",
                context={
                    "request": request,
                    "error": error_details,
                    "debug": self.debug
                },
            )
        except Exception:
            html = self._get_generic_error_html(error_details)
            
        return HTMLResponse(content=html, status_code=500)
    
    def _get_jsx_error_html(self, error_details: dict) -> str:
        """Generate JSX error HTML fallback"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>JSX Syntax Error - NextPy</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; 
                        padding: 2rem; background: #fef2f2; }}
                .error-container {{ max-width: 800px; margin: 0 auto; }}
                .error-header {{ background: #dc2626; color: white; padding: 1rem; border-radius: 8px 8px 0 0; }}
                .error-content {{ background: white; padding: 2rem; border-radius: 0 0 8px 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .error-title {{ font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem; }}
                .error-message {{ color: #dc2626; font-family: monospace; background: #fef2f2; padding: 1rem; border-radius: 4px; margin: 1rem 0; }}
                .error-details {{ background: #f3f4f6; padding: 1rem; border-radius: 4px; margin: 1rem 0; }}
                .error-suggestions {{ background: #ecfdf5; padding: 1rem; border-radius: 4px; margin: 1rem 0; }}
                .code {{ font-family: monospace; background: #1f2937; color: #f3f4f6; padding: 0.5rem; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-header">
                    <h1>🚫 JSX Syntax Error</h1>
                </div>
                <div class="error-content">
                    <div class="error-title">JSX Syntax Error Detected</div>
                    <div class="error-message">{error_details.get('message', 'Unknown JSX syntax error')}</div>
                    
                    {f'<div class="error-details"><strong>File:</strong> {error_details.get("file_path", "Unknown")}</div>' if error_details.get('file_path') else ''}
                    {f'<div class="error-details"><strong>Line:</strong> {error_details.get("line_number", "Unknown")}</div>' if error_details.get('line_number') else ''}
                    {f'<div class="error-details"><strong>Column:</strong> {error_details.get("column", "Unknown")}</div>' if error_details.get('column') else ''}
                    
                    <div class="error-suggestions">
                        <strong>Common JSX Issues:</strong>
                        <ul>
                            <li>Check for unclosed tags: <code>&lt;div&gt;content&lt;/div&gt;</code></li>
                            <li>Ensure proper attribute syntax: <code>className="my-class"</code></li>
                            <li>Verify component names are capitalized: <code>MyComponent</code></li>
                            <li>Check for missing quotes in attributes</li>
                            <li>Ensure proper nesting of elements</li>
                        </ul>
                    </div>
                    
                    {f'<div class="error-suggestions"><strong>Debug Mode:</strong> {"Enabled" if self.debug else "Disabled"}</div>'}
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_import_error_html(self, error_details: dict) -> str:
        """Generate import error HTML fallback"""
        suggestions = error_details.get('suggestions', [])
        suggestions_html = "\n".join([f"<li>{suggestion}</li>" for suggestion in suggestions])
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Import Error - NextPy</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; 
                        padding: 2rem; background: #fefce8; }}
                .error-container {{ max-width: 800px; margin: 0 auto; }}
                .error-header {{ background: #ca8a04; color: white; padding: 1rem; border-radius: 8px 8px 0 0; }}
                .error-content {{ background: white; padding: 2rem; border-radius: 0 0 8px 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .error-message {{ color: #ca8a04; font-family: monospace; background: #fefce8; padding: 1rem; border-radius: 4px; margin: 1rem 0; }}
                .error-suggestions {{ background: #ecfdf5; padding: 1rem; border-radius: 4px; margin: 1rem 0; }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-header">
                    <h1>📦 Import Error</h1>
                </div>
                <div class="error-content">
                    <div class="error-title">Module Import Failed</div>
                    <div class="error-message">{error_details.get('message', 'Unknown import error')}</div>
                    
                    <div class="error-suggestions">
                        <strong>Possible Solutions:</strong>
                        <ul>{suggestions_html}</ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_value_error_html(self, error_details: dict) -> str:
        """Generate value error HTML fallback"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>{error_details.get('error_type', 'Error')} - NextPy</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; 
                        padding: 2rem; background: #fef2f2; }}
                .error-container {{ max-width: 800px; margin: 0 auto; }}
                .error-header {{ background: #dc2626; color: white; padding: 1rem; border-radius: 8px 8px 0 0; }}
                .error-content {{ background: white; padding: 2rem; border-radius: 0 0 8px 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .error-message {{ color: #dc2626; font-family: monospace; background: #fef2f2; padding: 1rem; border-radius: 4px; margin: 1rem 0; }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-header">
                    <h1>⚠️ {error_details.get('error_type', 'Error')}</h1>
                </div>
                <div class="error-content">
                    <div class="error-title">{error_details.get('error_class', 'Runtime Error')}</div>
                    <div class="error-message">{error_details.get('message', 'Unknown error occurred')}</div>
                    {f'<pre>{error_details.get("traceback", "")}</pre>' if self.debug and error_details.get('traceback') else ''}
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_attribute_error_html(self, error_details: dict) -> str:
        """Generate attribute error HTML fallback"""
        missing_attr = error_details.get('missing_attribute', '')
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Attribute Error - NextPy</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; 
                        padding: 2rem; background: #fef2f2; }}
                .error-container {{ max-width: 800px; margin: 0 auto; }}
                .error-header {{ background: #dc2626; color: white; padding: 1rem; border-radius: 8px 8px 0 0; }}
                .error-content {{ background: white; padding: 2rem; border-radius: 0 0 8px 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .error-message {{ color: #dc2626; font-family: monospace; background: #fef2f2; padding: 1rem; border-radius: 4px; margin: 1rem 0; }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-header">
                    <h1>🔍 Attribute Error</h1>
                </div>
                <div class="error-content">
                    <div class="error-title">Missing Attribute or Key</div>
                    <div class="error-message">{error_details.get('message', 'Unknown attribute error')}</div>
                    {f'<div class="error-suggestions"><strong>Missing:</strong> <code>{missing_attr}</code></div>' if missing_attr else ''}
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_file_error_html(self, error_details: dict) -> str:
        """Generate file error HTML fallback"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>File Error - NextPy</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; 
                        padding: 2rem; background: #fef2f2; }}
                .error-container {{ max-width: 800px; margin: 0 auto; }}
                .error-header {{ background: #dc2626; color: white; padding: 1rem; border-radius: 8px 8px 0 0; }}
                .error-content {{ background: white; padding: 2rem; border-radius: 0 0 8px 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .error-message {{ color: #dc2626; font-family: monospace; background: #fef2f2; padding: 1rem; border-radius: 4px; margin: 1rem 0; }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-header">
                    <h1>📁 File System Error</h1>
                </div>
                <div class="error-content">
                    <div class="error-title">File Access Error</div>
                    <div class="error-message">{error_details.get('message', 'Unknown file error')}</div>
                    {f'<div class="error-details"><strong>File Path:</strong> <code>{error_details.get("file_path", "Unknown")}</code></div>' if error_details.get('file_path') else ''}
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_network_error_html(self, error_details: dict) -> str:
        """Generate network error HTML fallback"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Network Error - NextPy</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; 
                        padding: 2rem; background: #fef2f2; }}
                .error-container {{ max-width: 800px; margin: 0 auto; }}
                .error-header {{ background: #f59e0b; color: white; padding: 1rem; border-radius: 8px 8px 0 0; }}
                .error-content {{ background: white; padding: 2rem; border-radius: 0 0 8px 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .error-message {{ color: #f59e0b; font-family: monospace; background: #fef2f2; padding: 1rem; border-radius: 4px; margin: 1rem 0; }}
                .retry-button {{ background: #f59e0b; color: white; padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-header">
                    <h1>🌐 Network Error</h1>
                </div>
                <div class="error-content">
                    <div class="error-title">Connection or Timeout Error</div>
                    <div class="error-message">{error_details.get('message', 'Network error occurred')}</div>
                    <button class="retry-button" onclick="window.location.reload()">Retry</button>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_generic_error_html(self, error_details: dict) -> str:
        """Generate generic error HTML fallback"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Server Error - NextPy</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; 
                        padding: 2rem; background: #fef2f2; }}
                .error-container {{ max-width: 800px; margin: 0 auto; }}
                .error-header {{ background: #dc2626; color: white; padding: 1rem; border-radius: 8px 8px 0 0; }}
                .error-content {{ background: white; padding: 2rem; border-radius: 0 0 8px 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .error-message {{ color: #dc2626; font-family: monospace; background: #fef2f2; padding: 1rem; border-radius: 4px; margin: 1rem 0; }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-header">
                    <h1>💥 Server Error</h1>
                </div>
                <div class="error-content">
                    <div class="error-title">{error_details.get('error_type', 'Server Error')}</div>
                    <div class="error-message">{error_details.get('message', 'An unexpected error occurred')}</div>
                    {f'<pre>{error_details.get("traceback", "")}</pre>' if self.debug and error_details.get('traceback') else ''}
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_emergency_error_html(self, original_error: Exception, fallback_error: Exception) -> str:
        """Ultimate fallback error page"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Critical Error - NextPy</title>
            <style>
                body {{ font-family: monospace; background: #000; color: #ff0000; padding: 2rem; }}
            </style>
        </head>
        <body>
            <h1>🚨 CRITICAL SYSTEM ERROR</h1>
            <p>Original Error: {str(original_error)}</p>
            <p>Fallback Error: {str(fallback_error)}</p>
            <p>Please check the server logs for more information.</p>
        </body>
        </html>
        """
    
    def _get_import_error_suggestions(self, error: ImportError) -> list:
        """Get suggestions for import errors"""
        error_str = str(error).lower()
        suggestions = []
        
        if "no module named" in error_str:
            suggestions.append("Install the missing module using pip")
            suggestions.append("Check if the module name is spelled correctly")
        elif "cannot import" in error_str:
            suggestions.append("Verify the function/class exists in the module")
            suggestions.append("Check for circular imports")
        elif "module not found" in error_str:
            suggestions.append("Ensure the module is in the correct directory")
            suggestions.append("Check PYTHONPATH includes the module directory")
        else:
            suggestions.append("Check if all dependencies are installed")
            suggestions.append("Verify the import statement syntax")
            suggestions.append("Ensure the file exists and is accessible")
        
        return suggestions
    
    def _extract_missing_attribute(self, error: Exception) -> str:
        """Extract missing attribute name from error message"""
        error_str = str(error)
        if "has no attribute '" in error_str:
            start = error_str.find("has no attribute '") + 19
            end = error_str.find("'", start)
            if start > 18 and end > start:
                return error_str[start:end]
        elif "Key '" in error_str:
            start = error_str.find("Key '") + 5
            end = error_str.find("'", start)
            if start > 4 and end > start:
                return error_str[start:end]
        return ""
    
    def _extract_file_path_from_error(self, error: Exception) -> str:
        """Extract file path from error message"""
        error_str = str(error)
        # Try to extract file path from common error patterns
        import re
        
        # Pattern for file paths in error messages
        patterns = [
            r"[\'/]([^\'/]+\.py[\']?)",
            r"file: ([^\s]+)",
            r'File "([^"]+)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_str)
            if match:
                return match.group(1)
        
        return ""
        
    async def _handle_demo_page(self, request: Request, route, params: Dict[str, str]) -> Response:
        """Handle demo page requests"""
        try:
            # Call the demo page function
            demo_function = route.handler
            if callable(demo_function):
                # Demo pages return JSX elements, render them
                from ..jsx import render_jsx
                jsx_element = demo_function()
                html = render_jsx(jsx_element)
                
                return HTMLResponse(
                    content=html,
                    headers={
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                        "Pragma": "no-cache",
                        "Expires": "0",
                    },
                )
            else:
                return await self._render_404(request)
                
        except Exception as e:
            if self.debug:
                import traceback
                traceback.print_exc()
            return await self._render_error(request, e)
        
    def reload_routes(self) -> None:
        """Reload all routes (for hot reload)"""
        self._modules_cache.clear()
        if demo_router.should_serve_demo():
            self.router = Router(str(self.pages_dir), str(self.templates_dir))
            self.router.enable_demo_mode()
        else:
            self.router = ComponentRouter(str(self.pages_dir), str(self.templates_dir))
        
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
