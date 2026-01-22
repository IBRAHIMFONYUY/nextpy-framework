"""
NextPy Component Renderer - Renders Next.js-style Python components
Handles component-based pages similar to Next.js, including true JSX syntax
"""

import importlib.util
import sys
import time
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from ..true_jsx import JSXElement, render_jsx, JSXComponent

from ..jsx_transformer import load_jsx_module
from ..jsx_preprocessor import is_jsx_file, JSXSyntaxError


# Import auto-debug system
try:
    from ..components.debug.AutoDebug import inject_debug_icon, should_show_debug
    AUTO_DEBUG_AVAILABLE = True
except ImportError:
    AUTO_DEBUG_AVAILABLE = False
    inject_debug_icon = None
    should_show_debug = None


class ComponentRenderer:
    """Renders Next.js-style Python components to HTML"""
    
    def __init__(self, debug: bool = False):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.debug = debug
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'invalidations': 0
        }
        self.render_cache = {}
        self.render_cache_timeout = 60  # 1 minute for rendered content
        
    def _is_cache_valid(self, file_path: Path, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry:
            return False
            
        # Check timeout
        current_time = time.time()
        if current_time - cache_entry.get('timestamp', 0) > self.cache_timeout:
            return False
            
        # In debug mode, check file modification time
        if self.debug and file_path.exists():
            file_mtime = file_path.stat().st_mtime
            cache_mtime = cache_entry.get('file_mtime', 0)
            if file_mtime > cache_mtime:
                return False
                
        return True
        
    def _get_cache_key(self, file_path: Path, context: Dict[str, Any] = None) -> str:
        """Generate cache key for rendered content"""
        context_hash = hash(str(sorted(context.items()))) if context else 0
        return f"{file_path}:{context_hash}"
        
    def _cleanup_expired_cache(self):
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if current_time - entry.get('timestamp', 0) > self.cache_timeout:
                expired_keys.append(key)
                
        for key in expired_keys:
            del self.cache[key]
            self.cache_stats['invalidations'] += 1
            
        # Clean render cache
        expired_render_keys = []
        for key, entry in self.render_cache.items():
            if current_time - entry.get('timestamp', 0) > self.render_cache_timeout:
                expired_render_keys.append(key)
                
        for key in expired_render_keys:
            del self.render_cache[key]
    
    def load_component_module(self, file_path: Path):
        """Load a Python module from file path with enhanced caching"""
        # Check cache first
        cache_entry = self.cache.get(str(file_path))
        
        if self._is_cache_valid(file_path, cache_entry):
            self.cache_stats['hits'] += 1
            return cache_entry['module']
        
        # Cache miss - load module
        self.cache_stats['misses'] += 1
        
        try:
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
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                else:
                    raise ImportError(f"Could not load module from {file_path}")
            
            # Cache the module with metadata
            file_mtime = file_path.stat().st_mtime if file_path.exists() else 0
            cache_entry = {
                'module': module,
                'timestamp': time.time(),
                'file_mtime': file_mtime,
                'file_size': file_path.stat().st_size if file_path.exists() else 0
            }
            
            self.cache[str(file_path)] = cache_entry
            
            # Cleanup expired entries periodically
            if len(self.cache) > 100:  # Cleanup if cache gets too large
                self._cleanup_expired_cache()
            
            return module
            
        except Exception as e:
            # Remove any existing cache entry for this file
            if str(file_path) in self.cache:
                del self.cache[str(file_path)]
            raise e
    
    def render_page(self, file_path: Path, context: Dict[str, Any] = None) -> str:
        """
        Render a page component to HTML with caching
        Supports Next.js-style patterns:
        - Default export component
        - getServerSideProps
        - getStaticProps
        """
        if context is None:
            context = {}
        
        # Check render cache for static props
        render_cache_key = self._get_cache_key(file_path, context)
        render_cache_entry = self.render_cache.get(render_cache_key)
        
        if render_cache_entry and self._is_cache_valid(file_path, render_cache_entry):
            return render_cache_entry['html']
        
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
                    # Check if we have cached static props
                    static_props_key = f"static:{file_path}"
                    static_cache_entry = self.cache.get(static_props_key)
                    
                    if self._is_cache_valid(file_path, static_cache_entry):
                        page_props.update(static_cache_entry['props'])
                    else:
                        result = module.getStaticProps(context)
                        if isinstance(result, dict) and 'props' in result:
                            page_props.update(result['props'])
                            # Cache static props
                            self.cache[static_props_key] = {
                                'props': result['props'],
                                'timestamp': time.time(),
                                'file_mtime': file_path.stat().st_mtime if file_path.exists() else 0
                            }
            
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
            
            # Inject debug icon in development mode
            if AUTO_DEBUG_AVAILABLE and should_show_debug():
                html = inject_debug_icon(html, page_props)
            
            # Wrap in basic HTML structure if not already present
            if not html.strip().startswith('<html'):
                html = self._wrap_in_html(html, page_props)
            
            # Cache the rendered content
            self.render_cache[render_cache_key] = {
                'html': html,
                'timestamp': time.time(),
                'file_mtime': file_path.stat().st_mtime if file_path.exists() else 0
            }
            
            return html
            
        except JSXSyntaxError as e:
            return self._render_error_page(f"JSX Syntax Error: {str(e)}", file_path)
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
    
    def clear_cache(self, file_path: Path = None):
        """Clear the module cache"""
        if file_path:
            # Clear specific file from cache
            file_key = str(file_path)
            if file_key in self.cache:
                del self.cache[file_key]
                self.cache_stats['invalidations'] += 1
            
            # Clear related render cache entries
            keys_to_remove = [key for key in self.render_cache.keys() if key.startswith(str(file_path))]
            for key in keys_to_remove:
                del self.render_cache[key]
        else:
            # Clear all cache
            self.cache.clear()
            self.render_cache.clear()
            self.cache_stats['invalidations'] += len(self.cache)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_stats['hits'],
            'cache_misses': self.cache_stats['misses'],
            'hit_rate_percent': round(hit_rate, 2),
            'cache_invalidations': self.cache_stats['invalidations'],
            'module_cache_size': len(self.cache),
            'render_cache_size': len(self.render_cache),
            'cache_timeout': self.cache_timeout,
            'render_cache_timeout': self.render_cache_timeout
        }
    
    def set_cache_timeout(self, timeout: int):
        """Set cache timeout in seconds"""
        self.cache_timeout = timeout
    
    def set_debug_mode(self, debug: bool):
        """Enable or disable debug mode (affects cache invalidation)"""
        self.debug = debug
        if debug:
            # Clear cache when enabling debug mode to ensure fresh loads
            self.clear_cache()


# Global renderer instance
renderer = ComponentRenderer()


def render_component(file_path: Path, context: Dict[str, Any] = None) -> str:
    """Convenience function to render a component"""
    return renderer.render_page(file_path, context)


def render_api(file_path: Path, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to render an API route"""
    return renderer.render_api_route(file_path, request_data)
