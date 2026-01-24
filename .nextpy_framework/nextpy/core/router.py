"""
NextPy Router - File-based routing system inspired by Next.js
Supports:
- File-based routing (pages/index.py -> /)
- Dynamic routes (pages/[slug].py -> /:slug)
- Nested routes (pages/blog/[id].py -> /blog/:id)
- Catch-all routes (pages/[...path].py -> /*)
- API routes (pages/api/*.py)
- Demo pages when no project exists
"""

import os
import re
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from pydantic import BaseModel
from .demo_router import demo_router


class RouteParams(BaseModel):
    """Type-safe route parameters"""
    params: Dict[str, str] = {}
    query: Dict[str, str] = {}


@dataclass
class Route:
    """Represents a single route in the application"""
    path: str
    file_path: Path
    handler: Optional[Callable] = None
    is_dynamic: bool = False
    is_api: bool = False
    is_catch_all: bool = False
    param_names: List[str] = field(default_factory=list)
    pattern: Optional[re.Pattern] = None
    
    def matches(self, url_path: str) -> Optional[Dict[str, str]]:
        """Check if this route matches the given URL path"""
        if self.pattern:
            match = self.pattern.match(url_path)
            if match:
                return match.groupdict()
        elif self.path == url_path:
            return {}
        return None


@dataclass  
class DynamicRoute(Route):
    """A route with dynamic segments like [slug] or [...path]"""
    is_dynamic: bool = True


class Router:
    """
    File-based router that scans the pages directory
    and creates routes similar to Next.js
    """
    
    def __init__(self, pages_dir: str = "pages", templates_dir: str = "templates"):
        self.pages_dir = Path(pages_dir)
        self.templates_dir = Path(templates_dir)
        self.routes: List[Route] = []
        self.api_routes: List[Route] = []
        self._route_cache: Dict[str, Route] = {}
        self._demo_mode = False
        
    def enable_demo_mode(self):
        """Enable demo mode when no project exists"""
        self._demo_mode = True
        
    def is_demo_mode(self) -> bool:
        """Check if router is in demo mode"""
        return self._demo_mode
        
    def scan_pages(self) -> None:
        """Scan the pages directory and register all routes"""
        if not self.pages_dir.exists():
            return
            
        for file_path in self.pages_dir.rglob("*.py"):
            if file_path.name.startswith("_"):
                continue
                
            route = self._create_route_from_file(file_path)
            if route:
                if route.is_api:
                    self.api_routes.append(route)
                else:
                    self.routes.append(route)
                    
        self._sort_routes()
        
    def _create_route_from_file(self, file_path: Path) -> Optional[Route]:
        """Create a Route object from a Python file"""
        relative_path = file_path.relative_to(self.pages_dir)
        parts = list(relative_path.parts)
        
        is_api = parts[0] == "api" if parts else False
        
        route_parts = []
        param_names = []
        is_dynamic = False
        is_catch_all = False
        
        for part in parts:
            if part.endswith(".py"):
                part = part[:-3]
                
            if part == "index":
                continue
                
            catch_all_match = re.match(r"\[\.\.\.(\w+)\]", part)
            dynamic_match = re.match(r"\[(\w+)\]", part)
            
            if catch_all_match:
                param_name = catch_all_match.group(1)
                param_names.append(param_name)
                route_parts.append(f"(?P<{param_name}>.+)")
                is_dynamic = True
                is_catch_all = True
            elif dynamic_match:
                param_name = dynamic_match.group(1)
                param_names.append(param_name)
                route_parts.append(f"(?P<{param_name}>[^/]+)")
                is_dynamic = True
            else:
                route_parts.append(part)
                
        if is_api and route_parts and route_parts[0] == "api":
            route_parts = route_parts[1:]
            
        path = "/" + "/".join(route_parts) if route_parts else "/"
        
        if is_api:
            path = "/api" + path if path != "/" else "/api"
            
        pattern = None
        if is_dynamic:
            pattern_str = "^" + path.replace("/", r"\/") + "$"
            pattern_str = re.sub(r"\\\(\?P", "(?P", pattern_str)
            pattern_str = pattern_str.replace(r"\[", "[").replace(r"\]", "]")
            pattern_str = pattern_str.replace(r"\+", "+")
            try:
                pattern = re.compile(pattern_str)
            except re.error:
                pattern = re.compile("^" + path + "$")
                
        handler = self._load_handler(file_path)
        
        route_class = DynamicRoute if is_dynamic else Route
        return route_class(
            path=path,
            file_path=file_path,
            handler=handler,
            is_dynamic=is_dynamic,
            is_api=is_api,
            is_catch_all=is_catch_all,
            param_names=param_names,
            pattern=pattern,
        )
        
    def _load_handler(self, file_path: Path) -> Optional[Callable]:
        """Dynamically load the handler function from a page file using JSX transformer"""
        try:
            # Use JSX transformer for consistent loading
            from ..jsx_transformer import JSXTransformer
            transformer = JSXTransformer()
            module = transformer.load_jsx_module(file_path, file_path.stem)
            
            if module:
                for func_name in ["handler", "page", "get", "post", "default"]:
                    if hasattr(module, func_name):
                        return getattr(module, func_name)
        except Exception as e:
            # Fallback to regular import if JSX transformer fails
            try:
                spec = importlib.util.spec_from_file_location(
                    file_path.stem, 
                    file_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    for func_name in ["handler", "page", "get", "post", "default"]:
                        if hasattr(module, func_name):
                            return getattr(module, func_name)
            except Exception:
                pass  # Silently fail if both methods fail
                
        return None
        
    def _sort_routes(self) -> None:
        """Sort routes so static routes come before dynamic ones"""
        def route_priority(route: Route) -> Tuple[int, int, str]:
            if route.is_catch_all:
                return (2, len(route.param_names), route.path)
            elif route.is_dynamic:
                return (1, len(route.param_names), route.path)
            else:
                return (0, 0, route.path)
                
        self.routes.sort(key=route_priority)
        self.api_routes.sort(key=route_priority)
        
    def match(self, url_path: str) -> Optional[Tuple[Route, Dict[str, str]]]:
        """Find a route that matches the given URL path"""
        url_path = url_path.rstrip("/") or "/"
        
        # Check demo routes first if in demo mode
        if self.is_demo_mode():
            demo_page = demo_router.get_demo_page(url_path)
            if demo_page:
                # Create a demo route
                from .demo_pages import HomePage  # Import here to avoid circular import
                demo_route = Route(
                    path=url_path,
                    file_path=Path("demo"),
                    handler=demo_page,
                    is_dynamic=False,
                    is_api=False
                )
                return (demo_route, {})
        
        if url_path in self._route_cache:
            route = self._route_cache[url_path]
            params = route.matches(url_path) or {}
            return (route, params)
            
        routes = self.api_routes if url_path.startswith("/api") else self.routes
        
        for route in routes:
            params = route.matches(url_path)
            if params is not None:
                if not route.is_dynamic:
                    self._route_cache[url_path] = route
                return (route, params)
                
        return None
        
    def get_all_routes(self) -> List[Route]:
        """Get all registered routes"""
        return self.routes + self.api_routes
        
    def get_static_routes(self) -> List[Route]:
        """Get only static (non-dynamic) routes for SSG"""
        return [r for r in self.routes if not r.is_dynamic]
        
    def reload_route(self, file_path: Path) -> None:
        """Reload a specific route (for hot reload)"""
        self.routes = [r for r in self.routes if r.file_path != file_path]
        self.api_routes = [r for r in self.api_routes if r.file_path != file_path]
        self._route_cache.clear()
        
        if file_path.exists():
            route = self._create_route_from_file(file_path)
            if route:
                if route.is_api:
                    self.api_routes.append(route)
                else:
                    self.routes.append(route)
                    
        self._sort_routes()
