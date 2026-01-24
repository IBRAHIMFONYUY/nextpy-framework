"""
NextPy Component Router - Enhanced router for component-based pages
Supports both template-based and component-based rendering
"""

import os
import re
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from pydantic import BaseModel

from .router import Route, DynamicRoute, RouteParams
from .component_renderer import ComponentRenderer


@dataclass
class ComponentRoute(Route):
    """A route that renders components instead of templates"""
    use_components: bool = True
    renderer: ComponentRenderer = field(default_factory=ComponentRenderer)


class ComponentRouter:
    """
    Enhanced router that supports both template-based and component-based pages
    Automatically detects which rendering system to use based on file content
    """
    
    def __init__(self, pages_dir: str = "pages", templates_dir: str = "templates"):
        self.pages_dir = Path(pages_dir)
        self.templates_dir = Path(templates_dir)
        self.routes: List[Route] = []
        self.api_routes: List[Route] = []
        self._route_cache: Dict[str, Route] = {}
        self.renderer = ComponentRenderer()
        
    def scan_pages(self) -> None:
        """Scan pages directory and register all routes"""
        if not self.pages_dir.exists():
            return
            
        # Scan for both .py and .py.jsx files
        for file_path in self.pages_dir.rglob("*.py"):
            if file_path.name.startswith("_"):
                continue
                
            route = self._create_route_from_file(file_path)
            if route:
                if route.is_api:
                    self.api_routes.append(route)
                else:
                    self.routes.append(route)
                    
        # Also scan for .py.jsx files
        for file_path in self.pages_dir.rglob("*.py.jsx"):
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
            if part.endswith(".py.jsx"):
                part = part[:-7]
            elif part.endswith(".py"):
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
                
        # Check if this is a component-based page
        use_components = self._is_component_page(file_path)
        
        route_path = path
        
        handler = self._load_handler(file_path, use_components)
        
        route_class = ComponentRoute if use_components else (DynamicRoute if is_dynamic else Route)
        
        route = route_class(
            path=route_path,
            file_path=file_path,
            handler=handler,
            is_api=is_api,
            is_dynamic=is_dynamic,
            param_names=param_names,
            pattern=pattern
        )
        
        # Add component-specific attributes
        if use_components:
            route.use_components = True
            route.renderer = self.renderer
        
        return route
        
    def _is_component_page(self, file_path: Path) -> bool:
        """Check if a page uses components or templates with enhanced JSX detection"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Enhanced JSX patterns for more robust detection
            jsx_patterns = [
                'return (',
                'default = ',
                'className=',
                '<div',
                '<h1',
                '<h2',
                '<h3',
                '<p',
                '<button',
                '<section',
                '<article',
                '<header',
                '<footer',
                '<nav',
                '<main',
                '<aside',
                '<span',
                '<img',
                '<a',
                '<ul',
                '<ol',
                '<li',
                '<form',
                '<input',
                '<label',
                '<select',
                '<textarea',
                'export function',
                'def.*return.*<',
                'jsx(',
                'render_jsx(',
                'from nextpy.true_jsx',
                'from .jsx import',
                'getServerSideProps',
                'getStaticProps',
                'props.get(',
                'props = props or',
                'function.*Component',
                'const.*=.*\(.*\)',
                'className=',
                'htmlFor=',
                'onClick=',
                'onChange=',
                'onSubmit=',
                'href=',
                'src=',
                'alt=',
                'placeholder=',
                'type=',
                'value=',
                'disabled=',
                'readOnly=',
                'required=',
                'checked=',
                'selected=',
                'multiple=',
                'accept=',
                'maxLength=',
                'minLength=',
                'pattern=',
                'min=',
                'max=',
                'step=',
                'autoComplete=',
                'autoFocus=',
                'tabIndex=',
                'accessKey=',
                'draggable=',
                'hidden=',
                'spellCheck=',
                'contentEditable=',
                'dir=',
                'lang=',
                'title=',
                'style=',
                'id=',
                'name=',
                'data-',
                'aria-',
                'role=',
            ]
            
            # Check for template indicators (to differentiate from JSX)
            template_indicators = [
                'def get_template(',
                'return "',
                'templates/',
                '.html',
                '{% extends',
                '{% block',
                '{% include',
                '{% for',
                '{% if',
                '{{ ',
                '}}',
                '|filter',
                '{% end',
                'jinja2',
                'render_template(',
            ]
            
            # Enhanced scoring system with weighted patterns
            component_score = 0
            template_score = 0
            
            # Weight JSX patterns more heavily
            for pattern in jsx_patterns:
                if '*' in pattern:
                    # Regex pattern
                    if re.search(pattern, content):
                        component_score += 2
                else:
                    # Simple string pattern
                    count = content.count(pattern)
                    if count > 0:
                        component_score += count * 2
            
            # Additional JSX-specific checks
            if file_path.suffix == '.py.jsx':
                component_score += 10  # Strong indicator
            
            # Check for JSX return patterns
            jsx_return_patterns = [
                r'return\s*\(\s*<',
                r'return\s+<',
                r'default\s*=\s*\w+',
                r'function\s+\w+\s*\(.*\)\s*{',
                r'const\s+\w+\s*=\s*\(.*\)\s*=>',
            ]
            
            for pattern in jsx_return_patterns:
                if re.search(pattern, content, re.MULTILINE):
                    component_score += 3
            
            # Check for component imports
            component_import_patterns = [
                r'from\s+.*components',
                r'import\s+.*from\s+.*components',
                r'import\s+{.*}',
                r'from\s+nextpy\.',
                r'from\s+\.jsx',
            ]
            
            for pattern in component_import_patterns:
                if re.search(pattern, content):
                    component_score += 2
            
            # Weight template patterns
            for pattern in template_indicators:
                if pattern in content:
                    template_score += 3
            
            # Special checks for template files
            if file_path.suffix == '.py' and not file_path.name.endswith('.jsx'):
                # Check if it looks like a traditional template page
                if 'def get_template(' in content and 'return "' in content:
                    template_score += 5
            
            # Debug information (can be removed in production)
            # print(f"File: {file_path.name}, Component Score: {component_score}, Template Score: {template_score}")
            
            return component_score > template_score
            
        except Exception as e:
            # If there's an error reading the file, default to False
            print(f"Error checking if {file_path} is component page: {e}")
            return False
        
    def _load_handler(self, file_path: Path, use_components: bool = False) -> Optional[Callable]:
        """Load the appropriate handler based on rendering type"""
        if use_components:
            return self._create_component_handler(file_path)
        else:
            return self._create_template_handler(file_path)
    
    def _create_component_handler(self, file_path: Path) -> Callable:
        """Create a handler for component-based pages"""
        def handler(context: Dict[str, Any] = None):
            if context is None:
                context = {}
            return self.renderer.render_page(file_path, context)
        return handler
    
    def _create_template_handler(self, file_path: Path) -> Optional[Callable]:
        """Load the traditional template-based handler"""
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
                        
                if hasattr(module, "Page"):
                    return module.Page
                    
        except Exception as e:
            print(f"Error loading handler from {file_path}: {e}")
            
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
        
    def render_route(self, route: Route, context: Dict[str, Any] = None) -> str:
        """Render a route using the appropriate renderer"""
        if context is None:
            context = {}
            
        if isinstance(route, ComponentRoute) and route.use_components:
            return route.renderer.render_page(route.file_path, context)
        elif route.handler and callable(route.handler):
            return route.handler(context)
        else:
            return f"<h1>Route {route.path} has no handler</h1>"
    
    def handle_api_route(self, route: Route, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle API route requests"""
        if isinstance(route, ComponentRoute) and route.use_components:
            return route.renderer.render_api_route(route.file_path, request_data)
        elif route.handler and callable(route.handler):
            return route.handler(request_data)
        else:
            return {'error': f'API route {route.path} has no handler'}
        
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
        self.renderer.clear_cache()
        
        if file_path.exists():
            route = self._create_route_from_file(file_path)
            if route:
                if route.is_api:
                    self.api_routes.append(route)
                else:
                    self.routes.append(route)
                    
        self._sort_routes()
    
    def get_component_routes(self) -> List[ComponentRoute]:
        """Get only component-based routes"""
        return [r for r in self.routes if isinstance(r, ComponentRoute) and r.use_components]
    
    def get_template_routes(self) -> List[Route]:
        """Get only template-based routes"""
        return [r for r in self.routes if not (isinstance(r, ComponentRoute) and r.use_components)]


# Export the router instance
component_router = ComponentRouter()
