"""
Interactive Component Decorator for NextPy PSX - PRODUCTION VERSION
Enables client-side interactivity with proper handler registration
"""

import inspect
import re
from functools import wraps
from typing import Callable, Dict, Any, Optional, List


def extract_handler_functions(component_func: Callable) -> Dict[str, str]:
    """
    Extract all named event handler functions from component source.
    
    Returns: {handler_name: handler_code}
    """
    handlers = {}
    
    try:
        # Try to get source - might be wrapped
        source = inspect.getsource(component_func)
    except (OSError, TypeError):
        return handlers
    
    # Split by function definitions at component level (4+ spaces)
    lines = source.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        # Look for def handle_* or def on_* at indentation level 4 (nested in component)
        match = re.match(r'^    def\s+((?:handle|on)_\w+)\s*\([^)]*\)\s*:', line)
        if match:
            func_name = match.group(1)
            func_lines = []
            i += 1
            # Collect lines until next def or end of component
            while i < len(lines):
                next_line = lines[i]
                # Stop if we hit another def at same level or less indentation
                if next_line.startswith('    def ') or (next_line and not next_line.startswith('        ')):
                    break
                # Add if it's body (starts with 8 spaces)
                if next_line.startswith('        '):
                    func_lines.append(next_line[8:])  # Remove 8 spaces
                i += 1
            
            # Store handler
            body = '\n'.join(func_lines).strip()
            if body:
                handlers[func_name] = body
        else:
            i += 1
    
    return handlers


def python_code_to_js(python_code: str) -> str:
    """
    Convert Python event handler code to JavaScript.
    
    IMPROVED: More robust pattern matching and error handling.
    NOTE: This is a transitional approach. Future versions should use
    an instruction-based system instead of code translation.
    
    PATTERN SUPPORT:
    - setState(value) -> stateManager.set('state', value)
    - setXxxx(value) -> stateManager.set('xxx', value) [auto-camelCase conversion]
    - Function calls, operators, string literals
    - Python to JS equivalents (print -> console.log, and -> &&, etc.)
    
    LIMITATIONS:
    - Complex Python expressions may fail
    - Nested function calls have limited support
    - User input in state values could cause issues
    """
    js_code = python_code
    
    # SECURITY: Prevent dangerous patterns
    dangerous_patterns = [
        r'eval\s*\(',
        r'__import__\s*\(',
        r'exec\s*\(',
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, js_code, re.IGNORECASE):
            print(f"⚠️ WARNING: Handler contains dangerous pattern: {pattern}")
            js_code = re.sub(pattern, '/* BLOCKED */ ', js_code)
    
    # Pattern 1: Replace setXxxx(expression) with stateManager.set patterns
    def replace_setter(match):
        setter_name = match.group(1)  # "Count" from "setCount"
        expression = match.group(2)   # The argument (may contain nested parens)
        state_key = setter_name[0].lower() + setter_name[1:]  # "count"
        
        # IMPROVED: Handle nested function calls better
        expression = expression.strip()
        
        # Handle common nested patterns
        expr_js = expression
        expr_js = re.sub(r'\.upper\s*\(\s*\)', '.toUpperCase()', expr_js)
        expr_js = re.sub(r'\.lower\s*\(\s*\)', '.toLowerCase()', expr_js)
        expr_js = re.sub(r'\.strip\s*\(\s*\)', '.trim()', expr_js)
        expr_js = re.sub(r'len\s*\(\s*(\w+)\s*\)', r'\1.length', expr_js)
        
        return f"this.stateManager.set('{state_key}', {expr_js})"
    
    # Find all setXxxx(...) calls - IMPROVED regex to handle nested parens
    # This pattern matches setName(arg) where arg can contain balanced parens
    js_code = re.sub(
        r'set([A-Z]\w*)\s*\(([^)]*(?:\([^)]*\)[^)]*)*)\)',
        replace_setter,
        js_code
    )
    
    # Pattern 2: String conversions
    replacements = [
        (r'\bprint\s*\(', 'console.log('),          # print() -> console.log()
        (r'\.upper\s*\(\)', '.toUpperCase()'),      # .upper() -> .toUpperCase()
        (r'\.lower\s*\(\)', '.toLowerCase()'),      # .lower() -> .toLowerCase()
        (r'\.strip\s*\(\)', '.trim()'),             # .strip() -> .trim()
        (r'\blen\s*\((\w+)\)', r'\1.length'),       # len(x) -> x.length
    ]
    
    for pattern, replacement in replacements:
        js_code = re.sub(pattern, replacement, js_code)
    
    # Pattern 3: Logical operators
    logical_replacements = [
        (r'\s+and\s+', ' && '),                     # and -> &&
        (r'\s+or\s+', ' || '),                      # or -> ||
        (r'\bnot\s+', '!'),                         # not -> !
        (r'is\s+None', '=== null'),                 # is None -> === null
        (r'is\s+not\s+None', '!== null'),           # is not None -> !== null
    ]
    
    for pattern, replacement in logical_replacements:
        js_code = re.sub(pattern, replacement, js_code)
    
    # Pattern 4: List/dict operations
    js_code = re.sub(r'\.append\s*\(', '.push(', js_code)  # .append() -> .push()
    js_code = re.sub(r'\.pop\s*\(', '.pop(', js_code)      # .pop() -> .pop()
    
    return js_code


def generate_handler_registration_script(
    handlers: Dict[str, str], 
    component_id: str,
    event_types: Optional[Dict[str, str]] = None
) -> str:
    """
    Generate JavaScript to register all handlers for a component.
    
    IMPROVED: Supports multiple event types and dynamic binding.
    
    Args:
        handlers: {handler_name: handler_code}
        component_id: Component ID for scoping
        event_types: Optional {handler_name: 'click'|'change'|'submit'...}
    """
    if not handlers:
        return ""
    
    # Default event type is 'click'
    if event_types is None:
        event_types = {name: 'click' for name in handlers}
    
    script = f"""
// Handler registration for component: {component_id}
(function() {{
    const componentId = '{component_id}';
    const component = NextPyRuntime.components.get(componentId);
    
    if (!component) {{
        console.warn('Component not found: ' + componentId);
        return;
    }}
    
    // Store handlers on the component
    component._handlers = {{}};
"""
    
    for handler_name, handler_body in handlers.items():
        js_body = python_code_to_js(handler_body)
        event_type = event_types.get(handler_name, 'click')
        
        # Create the handler function with error handling
        script += f"""
    // Handler: {handler_name} (event: {event_type})
    component._handlers['{handler_name}'] = function(e) {{
        try {{
            {js_body}
        }} catch (error) {{
            console.error('Error in handler {handler_name}:', error);
            console.error('Event:', e);
        }}
    }};
    
    // IMPROVED: Register with all matching elements using data-handler
    // Supports multiple event types: data-handler-click, data-handler-change, etc.
    document.querySelectorAll('[data-handler="{handler_name}"], [data-handler-{event_type}="{handler_name}"]').forEach(el => {{
        el.addEventListener('{event_type}', component._handlers['{handler_name}'].bind(component));
    }});
"""
    
    script += """
})();
"""
    return script


def convert_handler_attributes_in_html(html: str, handlers: Dict[str, str]) -> str:
    """
    Convert onClick/onChange/etc. attributes from JSX to data-handler format.
    
    IMPROVED: Supports multiple event types and better attribute patterns.
    
    Converts:
    - onClick={handle_increment} -> data-handler-click="handle_increment"
    - onChange={handle_change} -> data-handler-change="handle_change"
    - on{EventName}={handler} -> data-handler-{eventname}="handler"
    """
    
    # Pattern 1: onClick={handler_name}, onChange={handler_name}, etc.
    # Matches: onClick, onChange, onSubmit, onFocus, onBlur, onMouseEnter, etc.
    pattern = r'\bon([A-Z][a-z]*)\s*=\s*\{(\w+)\}'
    
    def replace_event_handler(match):
        event_name = match.group(1).lower()  # "Click" -> "click"
        handler_name = match.group(2)
        
        # Only replace if it's a known handler
        if handler_name in handlers:
            # Return data-handler attribute with event type and default onclick behavior
            return f'data-handler-{event_name}="{handler_name}" on{match.group(1)}="return false;"'
        return match.group(0)
    
    html = re.sub(pattern, replace_event_handler, html)
    
    # Pattern 2: data-event="click:handler_name" format (alternative syntax)
    # This allows more flexible specification if developer uses this pattern
    
    return html


# Import after defining helper functions
from ..components.component import component as base_component
from .integration import hydrate_component, get_component_hydrator


def interactive_component(func: Callable) -> Callable:
    """
    Decorator for interactive PSX components with client-side state management.
    
    Properly handles named event handler functions and converts them to JavaScript.
    """
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # First, get the component from the base decorator
        base_component_result = base_component(func)(*args, **kwargs)
        
        # Extract props if provided
        props = args[0] if args and isinstance(args[0], dict) else kwargs
        
        # Get the HTML output
        if hasattr(base_component_result, 'to_html'):
            html = base_component_result.to_html()
        else:
            html = str(base_component_result)
        
        # Extract named handler functions from the component
        handlers = extract_handler_functions(func)
        
        # Convert handler attributes in HTML (onClick={handle_x} -> data-handler="handle_x")
        html = convert_handler_attributes_in_html(html, handlers)
        
        # Hydrate the component
        hydrated_html, hydration_script = hydrate_component(func, props, html)
        
        # Get engine to add full runtime script
        from .engine import get_hydration_engine
        engine = get_hydration_engine()
        full_script = engine.generate_hydration_script()
        
        # Generate handler registration script
        handler_script = generate_handler_registration_script(handlers, 'psx_component_1')
        
        # Combine all scripts
        complete_script = f"{full_script}\n\n{handler_script}\n\n{hydration_script}"
        
        # Create a wrapped result that includes hydration data
        class InteractiveComponentResult:
            def __init__(self, html, script):
                self.html = html
                self.script = script
                self.is_interactive = True
            
            def to_html(self, context=None):
                # Embed the full script in the HTML
                return f"{self.html}\n<script type='text/javascript'>\n{self.script}\n</script>"
            
            def __str__(self):
                return f"{self.html}\n<script type='text/javascript'>\n{self.script}\n</script>"
        
        return InteractiveComponentResult(hydrated_html, complete_script)
    
    return wrapper


def enable_hydration_globally():
    """
    Enable hydration globally by replacing the default @component decorator
    """
    import sys
    from .. import components
    
    # Replace component decorator
    original_component = components.component
    
    def hydrated_component(func):
        # Use interactive_component for all components
        return interactive_component(func)
    
    components.component = hydrated_component
    
    print("✓ Global hydration enabled - all @component decorated functions will be interactive")


# HTML template for embedding hydration script and styles
HYDRATION_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* NextPy Hydration Styles */
        .nextpy-component {{
            position: relative;
        }}
        
        .nextpy-component [data-bind] {{
            transition: all 0.3s ease-in-out;
        }}
        
        .nextpy-state-changed {{
            animation: stateChanged 0.3s ease-in-out;
        }}
        
        @keyframes stateChanged {{
            0% {{ opacity: 0.8; }}
            100% {{ opacity: 1; }}
        }}
    </style>
</head>
<body>
    <div id="app">
        {body}
    </div>
    
    <script type="text/javascript">
        {script}
    </script>
</body>
</html>
'''


def create_interactive_page(html: str, script: str, title: str = "NextPy App") -> str:
    """
    Create a complete interactive HTML page
    
    Args:
        html: Component HTML
        script: Hydration script
        title: Page title
        
    Returns:
        Complete HTML page as string
    """
    page = HYDRATION_TEMPLATE.format(
        title=title,
        body=html,
        script=script
    )
    return page
