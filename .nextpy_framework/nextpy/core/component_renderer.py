"""
NextPy Component Renderer - Renders Next.js-style Python components
Handles component-based pages similar to Next.js, including true JSX syntax
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from ..jsx import JSXElement, render_jsx
from ..jsx_transformer import load_jsx_module
from ..jsx_preprocessor import is_jsx_file


class ComponentRenderer:
    """Renders Next.js-style Python components to HTML"""
    
    def __init__(self):
        self.cache = {}
    
    def load_component_module(self, file_path: Path):
        """Load a Python module from file path"""
        if file_path in self.cache:
            return self.cache[file_path]
        
        # Check if file contains JSX syntax
        if is_jsx_file(file_path):
            # Load with JSX transformer
            module = load_jsx_module(file_path)
        else:
            # Load regular Python module
            spec = importlib.util.spec_from_file_location(
                file_path.stem, 
                file_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        
        self.cache[file_path] = module
        return module
    
    def render_page(self, file_path: Path, context: Dict[str, Any] = None) -> str:
        """
        Render a page component to HTML
        Supports Next.js-style patterns:
        - Default export component
        - getServerSideProps
        - getStaticProps
        """
        if context is None:
            context = {}
        
        try:
            module = self.load_component_module(file_path)
            
            # Check for data fetching functions
            page_props = {}
            
            # getServerSideProps (runs on every request)
            if hasattr(module, 'getServerSideProps'):
                if callable(module.getServerSideProps):
                    result = module.getServerSideProps(context)
                    if isinstance(result, dict) and 'props' in result:
                        page_props.update(result['props'])
            
            # getStaticProps (runs at build time)
            elif hasattr(module, 'getStaticProps'):
                if callable(module.getStaticProps):
                    result = module.getStaticProps(context)
                    if isinstance(result, dict) and 'props' in result:
                        page_props.update(result['props'])
            
            # Get the main component
            component = None
            
            # Try default export first
            if hasattr(module, 'default'):
                component = module.default
            # Try named export with file name
            elif hasattr(module, file_path.stem):
                component = getattr(module, file_path.stem)
            # Try Component function
            elif hasattr(module, 'Component'):
                component = module.Component
            # Try Page function
            elif hasattr(module, 'Page'):
                component = module.Page
            
            if component is None:
                raise ValueError(f"No component found in {file_path}")
            
            # Render the component with props
            if callable(component):
                # Check if it's a decorated component
                if hasattr(component, 'is_component'):
                    rendered = component(page_props)
                else:
                    rendered = component(page_props)
            else:
                # It's already a JSX element
                rendered = component
            
            # Convert to HTML
            html = render_jsx(rendered)
            
            # Wrap in basic HTML structure if not already present
            if not html.strip().startswith('<html'):
                html = self._wrap_in_html(html, page_props)
            
            return html
            
        except Exception as e:
            return self._render_error_page(str(e), file_path)
    
    def _wrap_in_html(self, content: str, props: Dict[str, Any]) -> str:
        """Wrap content in basic HTML structure"""
        title = props.get('title', 'NextPy App')
        description = props.get('description', 'NextPy Application')
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; }}
    </style>
</head>
<body>
    {content}
</body>
</html>"""
    
    def _render_error_page(self, error: str, file_path: Path) -> str:
        """Render an error page"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Error - NextPy</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; 
                padding: 2rem; background: #fef2f2; }}
        .error {{ background: white; padding: 2rem; border-radius: 8px; 
                 border-left: 4px solid #ef4444; max-width: 800px; }}
        h1 {{ color: #dc2626; margin-bottom: 1rem; }}
        pre {{ background: #f3f4f6; padding: 1rem; border-radius: 4px; 
              overflow-x: auto; margin-top: 1rem; }}
    </style>
</head>
<body>
    <div class="error">
        <h1>Component Rendering Error</h1>
        <p>Failed to render component from: <code>{file_path}</code></p>
        <pre>{error}</pre>
    </div>
</body>
</html>"""
    
    def render_api_route(self, file_path: Path, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render API route (Next.js API routes style)
        """
        try:
            module = self.load_component_module(file_path)
            
            # Get HTTP method handlers
            method = request_data.get('method', 'GET').upper()
            handler = None
            
            if hasattr(module, method.lower()):
                handler = getattr(module, method.lower())
            elif hasattr(module, 'handler'):
                handler = module.handler
            elif hasattr(module, 'default'):
                handler = module.default
            
            if handler is None or not callable(handler):
                return {'error': f'No handler found for method {method}'}
            
            # Call the handler
            if method in ['GET', 'DELETE']:
                result = handler(request_data)
            else:
                # POST, PUT, PATCH
                result = handler(request_data)
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def clear_cache(self):
        """Clear the module cache"""
        self.cache.clear()


# Global renderer instance
renderer = ComponentRenderer()


def render_component(file_path: Path, context: Dict[str, Any] = None) -> str:
    """Convenience function to render a component"""
    return renderer.render_page(file_path, context)


def render_api(file_path: Path, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to render an API route"""
    return renderer.render_api_route(file_path, request_data)
