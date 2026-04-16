"""
NextPy Component Renderer - Renders Next.js-style Python components
Handles component-based pages similar to Next.js, including true JSX syntax
"""

import importlib.util
import sys
import time
import os
import inspect
import html
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
            
            # Convert to HTML, passing page props as context for {expressions}
            # Check if this is a PSX component and handle Server/Client components
            if hasattr(component, '_is_psx_component') or 'psx' in str(type(rendered)):
                # Import server/client component system
                try:
                    from ..psx.server_client_components import render_component
                    result = render_component(component, page_props)
                    
                    # Handle client component return format
                    if isinstance(result, dict) and result.get('is_client'):
                        # Client component - extract HTML and prepare for hydration
                        html = result['html']
                        
                        # Add client component hydration script
                        hydration_script = f"""
                        <script>
                        window.__NEXTPY_CLIENT_COMPONENTS__ = window.__NEXTPY_CLIENT_COMPONENTS__ || [];
                        window.__NEXTPY_CLIENT_COMPONENTS__.push({{
                            id: '{result['component_id']}',
                            props: {repr(result['props'])},
                            hasInteractivity: {result['has_interactivity']}
                        }});
                        </script>
                        """
                        
                        # Append hydration script to HTML
                        if '</body>' in html:
                            html = html.replace('</body>', f'{hydration_script}</body>')
                        else:
                            html += hydration_script
                            
                    else:
                        # Server component - just use the HTML
                        html = result
                        
                except ImportError:
                    # Fallback to regular PSX rendering
                    from ..psx.core.parser import render_psx
                    html = render_psx(rendered, page_props)
            else:
                html = render_jsx(rendered, page_props)
            
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
        """Wrap content in full NextPy HTML document (Dev + Prod ready)"""

        title = html.escape(props.get('title', 'NextPy App'))
        description = html.escape(props.get('description', 'NextPy Application'))

        dev_mode = props.get("dev", True)

        # 🔥 Inject Dev Tools (only in dev mode)
        dev_scripts = ""
        if dev_mode:
            dev_scripts = """
    <script>
    /* ===============================
    NextPy Live Error Overlay
    ================================ */

    const socket = new WebSocket("ws://localhost:8765");

    let lastError = null;

    // Handle WebSocket connection errors gracefully
    socket.onerror = (error) => {
        console.log("NextPy Live Error Overlay: WebSocket connection failed - development tool not available");
    };
    
    socket.onclose = (event) => {
        if (event.code !== 1000) {
            console.log("NextPy Live Error Overlay: WebSocket connection closed");
        }
    };

    socket.onmessage = (event) => {
        const err = JSON.parse(event.data);
        lastError = err;
        showErrorOverlay(err);
    };

    function showErrorOverlay(err) {
        let overlay = document.getElementById("nextpy-error-overlay");

        if (!overlay) {
            overlay = document.createElement("div");
            overlay.id = "nextpy-error-overlay";
            document.body.appendChild(overlay);
        }

        overlay.innerHTML = `
        <div style="
            position:fixed;
            inset:0;
            
            color:white;
            z-index:9999;
            padding:20px;
            font-family:monospace;
        ">
            <h2 style="color:#ff5555;">🚨 NextPy Runtime Error</h2>
            <p><b>${err.message}</b></p>

            <p>
                📄 <span onclick="openFile('${err.file}', ${err.line})"
                style="color:#4ade80;cursor:pointer;">
                    ${err.file}:${err.line}
                </span>
            </p>

            <pre style="margin-top:10px;">${err.code || ''}</pre>

            <div style="margin-top:15px;display:flex;gap:10px;">
                <button onclick="closeOverlay()">Close</button>
                <button onclick="highlightError()">Highlight</button>
                <button onclick="copyError()">Copy</button>
                <button onclick="explainError()">🤖 Explain</button>
            </div>
        </div>
        `;
    }

    function closeOverlay() {
        document.getElementById("nextpy-error-overlay")?.remove();
    }

    function highlightError() {
        document.body.style.outline = "3px solid red";
    }

    function copyError() {
        navigator.clipboard.writeText(JSON.stringify(lastError, null, 2));
        alert("Copied error!");
    }

    function openFile(file, line) {
        fetch(`/__nextpy/open?file=${file}&line=${line}`);
    }

    function explainError() {
        if (!lastError) return;

        let suggestions = [];

        if (lastError.message.includes("NoneType")) {
            suggestions.push("Check for null/None before usage.");
        }
        if (lastError.message.includes("not defined")) {
            suggestions.push("Variable might not be declared or imported.");
        }
        if (lastError.message.includes("unexpected indent")) {
            suggestions.push("Fix indentation in your code.");
        }

        alert("🧠 Suggestions:\\n\\n" + suggestions.join("\\n"));
    }
    </script>
    """

        return f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>{title}</title>
    <meta name="description" content="{description}">

    <link rel="stylesheet" href="./public/tailwind.css">

    <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      
    }}
    </style>

    </head>

    <body>

    <div id="__nextpy_root">
    {content}
    </div>

    {dev_scripts}

    </body>
    </html>
    """
        
   

    def _render_error_page(self, error: str, file_path: Path) -> str:
        """Render a professional NextPy error page (production-grade UI)"""

        safe_error = html.escape(error)
        safe_path = html.escape(str(file_path))

        return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>NextPy Error</title>

    <style>
    :root {{
        --bg: #0b1220;
        --card: #0f172a;
        --border: #1e293b;
        --accent: #ef4444;
        --text: #e2e8f0;
        --muted: #94a3b8;
        --button: #1f2937;
        --button-hover: #334155;
    }}

    * {{
        box-sizing: border-box;
    }}

    body {{
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: radial-gradient(circle at top, #1e293b, #020617);
        color: var(--text);
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
    }}

    .container {{
        width: 92%;
        max-width: 950px;
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        box-shadow: 0 25px 80px rgba(0,0,0,0.6);
        overflow: hidden;
        animation: fadeIn 0.3s ease;
    }}

    .header {{
        padding: 1.2rem 1.5rem;
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    .header svg {{
        width: 20px;
        height: 20px;
        color: var(--accent);
    }}

    .header h1 {{
        font-size: 1rem;
        font-weight: 600;
    }}

    .subtitle {{
        padding: 0 1.5rem;
        color: var(--muted);
        font-size: 0.9rem;
        margin-top: 4px;
    }}

    .section {{
        padding: 1.2rem 1.5rem;
    }}

    .file {{
        font-family: monospace;
        background: #020617;
        border: 1px solid var(--border);
        padding: 0.6rem;
        border-radius: 6px;
        font-size: 0.85rem;
    }}

    .toggle {{
        margin-top: 12px;
        color: #38bdf8;
        cursor: pointer;
        font-size: 0.85rem;
    }}

    pre {{
        margin-top: 12px;
        background: #020617;
        border: 1px solid var(--border);
        padding: 1rem;
        border-radius: 6px;
        overflow-x: auto;
        max-height: 350px;
        display: none;
        font-size: 0.8rem;
        line-height: 1.4;
    }}

    .actions {{
        padding: 1rem 1.5rem;
        border-top: 1px solid var(--border);
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }}

    button {{
        display: flex;
        align-items: center;
        gap: 6px;
        background: var(--button);
        color: var(--text);
        border: 1px solid var(--border);
        padding: 0.5rem 0.9rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.85rem;
        transition: all 0.2s ease;
    }}

    button:hover {{
        background: var(--button-hover);
    }}

    button svg {{
        width: 14px;
        height: 14px;
    }}

    .footer {{
        padding: 0.8rem 1.5rem;
        font-size: 0.75rem;
        color: var(--muted);
        border-top: 1px solid var(--border);
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    </head>

    <body>

    <div class="container">

        <div class="header">
            <!-- Warning Icon -->
            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path d="M12 9v4m0 4h.01M10.29 3.86l-8 14A1 1 0 003 20h18a1 1 0 00.87-1.5l-8-14a1 1 0 00-1.74 0z"/>
            </svg>
            <h1>Rendering Error</h1>
        </div>

        <div class="subtitle">
            An error occurred while rendering a component.
        </div>

        <div class="section">
            <div class="file">{safe_path}</div>

            <div class="toggle" onclick="toggleError()">Show details</div>

            <pre id="errorBox">{safe_error}</pre>
        </div>

        <div class="actions">

            <button onclick="retry()">
                <!-- Refresh Icon -->
                <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M4 4v6h6M20 20v-6h-6M5.6 19A9 9 0 1019 5.6"/>
                </svg>
                Retry
            </button>

            <button onclick="goHome()">
                <!-- Home Icon -->
                <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M3 12l9-9 9 9M9 21V9h6v12"/>
                </svg>
                Home
            </button>

            <button onclick="copyError()">
                <!-- Copy Icon -->
                <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <rect x="9" y="9" width="13" height="13" rx="2"/>
                    <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                </svg>
                Copy
            </button>

            <button onclick="explainError()">
                <!-- Brain/AI Icon -->
                <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path d="M9 3a3 3 0 00-3 3v1a3 3 0 000 6v1a3 3 0 003 3"/>
                    <path d="M15 3a3 3 0 013 3v1a3 3 0 010 6v1a3 3 0 01-3 3"/>
                </svg>
                Explain
            </button>

        </div>

        <div class="footer">
            NextPy Development Mode
        </div>

    </div>

    <script>
    function toggleError() {{
        const box = document.getElementById("errorBox");
        const toggle = document.querySelector(".toggle");

        if (box.style.display === "none" || box.style.display === "") {{
            box.style.display = "block";
            toggle.innerText = "Hide details";
        }} else {{
            box.style.display = "none";
            toggle.innerText = "Show details";
        }}
    }}

    function retry() {{
        location.reload();
    }}

    function goHome() {{
        window.location.href = "/";
    }}

    function copyError() {{
        const text = document.getElementById("errorBox").innerText;
        navigator.clipboard.writeText(text);
    }}

    function explainError() {{
        alert("AI debugging module will analyze this error in future versions.");
    }}
    </script>

    </body>
    </html>
    """

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
