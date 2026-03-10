"""
PSX (Python Syntax eXtension) Parser for NextPy
Pure Python-based HTML structure without JavaScript patterns
Replaces JSX with PSX - Python functions only, no arrow functions
"""

import re
import ast
import inspect
from typing import Any, Dict, List, Union, Callable
from dataclasses import dataclass


@dataclass
class PSXElement:
    """Represents a PSX (Python Syntax eXtension) element"""
    tag: str
    props: Dict[str, Any]
    children: List[Union[str, 'PSXElement']]
    
    def __str__(self) -> str:
        """Convert to HTML string"""
        return self.to_html()
    
    def to_html(self, context: Dict[str, Any] = None) -> str:
        """Convert PSX element to HTML string.

        Evaluates any {expressions} in text nodes and prop values using `context`.
        Supports Python functions instead of JavaScript patterns.
        """
        # Build props string
        props_str = ""
        if self.props:
            props_list = []
            for key, value in self.props.items():
                # Map React-style `className` to HTML `class`
                attr_name = 'class' if key == 'className' else key

                # Handle Python functions for event handlers
                if key.startswith("on_") and callable(value):
                    # Convert Python function to JavaScript event handler call
                    func_name = getattr(value, '__name__', 'handler')
                    props_list.append(f'{attr_name}="python_call_{func_name}"')
                elif isinstance(value, bool) and value:
                    props_list.append(attr_name)
                elif value is not None and value != "":
                    # If value looks like a stored expression token '{expr}', evaluate at render time
                    if isinstance(value, str) and value.startswith('{') and value.endswith('}') and context is not None:
                        inner = value[1:-1].strip()
                        try:
                            evaluated = str(eval(inner, {}, context))
                        except Exception:
                            evaluated = ''
                        props_list.append(f'{attr_name}="{evaluated}"')
                    # If string contains inline {expr} parts, evaluate those
                    elif isinstance(value, str) and '{' in value and '}' in value and context is not None:
                        from re import sub
                        evaluated = _evaluate_expressions_in_string(value, context)
                        props_list.append(f'{attr_name}="{evaluated}"')
                    else:
                        props_list.append(f'{attr_name}="{value}"')

            props_str = " " + " ".join(props_list) if props_list else ""

        # Build children string
        children_str = ""
        if self.children:
            children_parts = []
            for child in self.children:
                if isinstance(child, PSXElement):
                    children_parts.append(child.to_html(context))
                else:
                    # Evaluate any {expressions} inside text nodes
                    if isinstance(child, str) and '{' in child and '}' in child and context is not None:
                        children_parts.append(_evaluate_expressions_in_string(child, context))
                    else:
                        children_parts.append(str(child))
            children_str = "".join(children_parts)

        # Handle self-closing tags
        self_closing_tags = {
            'img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col',
            'embed', 'source', 'track', 'wbr', 'command', 'keygen', 'menuitem', 'param'
        }

        if self.tag in self_closing_tags and not children_str:
            return f"<{self.tag}{props_str} />"

        return f"<{self.tag}{props_str}>{children_str}</{self.tag}>"


class PSXParser:
    """Parse PSX syntax from Python source code - Pure Python patterns only"""
    
    def __init__(self):
        self.psx_pattern = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)\s*([^>]*)>(.*?)</\1>', re.DOTALL)
        self.self_closing_pattern = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)\s*([^>]*)\s*/>', re.DOTALL)
        self.prop_pattern = re.compile(r'([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*\{([^}]+)\}|([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*"([^"]*)"|([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*\'([^\']*)\'|([a-zA-Z][a-zA-Z0-9-]+)')
        
        # Store Python functions for event handlers
        self.python_functions: Dict[str, Callable] = {}
    
    def register_python_function(self, name: str, func: Callable):
        """Register a Python function for use in PSX"""
        self.python_functions[name] = func
    
    def parse_props(self, props_str: str) -> Dict[str, Any]:
        """Parse PSX props string - supports Python expressions"""
        props = {}
        if not props_str.strip():
            return props
        
        # Simple prop parsing - can be enhanced
        for match in self.prop_pattern.finditer(props_str):
            groups = match.groups()
            if groups[0] and groups[1]:  # {prop} syntax - Python expression
                prop_name = groups[0]
                prop_value = groups[1].strip()
                # Store as a raw expression token to be evaluated at render time
                props[prop_name] = '{' + prop_value + '}'
            elif groups[2] and groups[3]:  # "prop" syntax
                props[groups[2]] = groups[3]
            elif groups[4] and groups[5]:  # 'prop' syntax
                props[groups[4]] = groups[5]
            elif groups[6]:  # prop without value (boolean)
                props[groups[6]] = True
        
        return props
    
    def parse_psx(self, psx_str: str) -> PSXElement:
        """Parse PSX string to PSXElement"""
        psx_str = psx_str.strip()
        
        # Try self-closing tag first
        self_closing_match = self.self_closing_pattern.match(psx_str)
        if self_closing_match:
            tag = self_closing_match.group(1)
            props_str = self_closing_match.group(2)
            props = self.parse_props(props_str)
            return PSXElement(tag, props, [])
        
        # Try regular tag
        match = self.psx_pattern.match(psx_str)
        if match:
            tag = match.group(1)
            props_str = match.group(2)
            children_str = match.group(3)
            
            props = self.parse_props(props_str)
            children = self.parse_children(children_str)
            
            return PSXElement(tag, props, children)
        
        # If no PSX tags found, treat as text
        return psx_str
    
    def parse_children(self, children_str: str) -> List[Union[str, PSXElement]]:
        """Parse children string"""
        children = []
        
        # Split by PSX tags and text
        parts = re.split(r'(<[^>]+>)', children_str)
        
        i = 0
        while i < len(parts):
            part = parts[i].strip()
            
            if not part:
                i += 1
                continue
            
            # Check if it's an opening tag
            if part.startswith('<') and not part.startswith('</'):
                # Find the matching closing tag
                tag_match = re.match(r'<([a-zA-Z][a-zA-Z0-9]*)', part)
                if tag_match:
                    tag = tag_match.group(1)
                    # Find the complete PSX element
                    psx_content = part
                    depth = 1
                    j = i + 1
                    
                    while j < len(parts) and depth > 0:
                        if parts[j].startswith(f'</{tag}>'):
                            depth -= 1
                        elif parts[j].startswith(f'<{tag}') and not parts[j].startswith('</'):
                            depth += 1
                        psx_content += parts[j]
                        j += 1
                    
                    children.append(self.parse_psx(psx_content))
                    i = j - 1
                else:
                    children.append(part)
            elif part.startswith('</'):
                # Closing tag - skip
                pass
            else:
                # Text content
                if part:
                    children.append(part)
            
            i += 1
        
        return children


# Global parser instance
parser = PSXParser()


def psx(psx_str: str) -> PSXElement:
    """Parse PSX string to PSXElement"""
    return parser.parse_psx(psx_str)


def register_python_function(name: str, func: Callable):
    """Register a Python function for use in PSX event handlers"""
    parser.register_python_function(name, func)


def _evaluate_expressions_in_string(s: str, context: Dict[str, Any]) -> str:
    """Find {expressions} in string `s` and evaluate them using `context`."""
    def repl(match):
        expr = match.group(1).strip()
        try:
            return str(eval(expr, {}, context or {}))
        except Exception:
            return ''

    return re.sub(r'\{([^}]+)\}', repl, s)


def render_psx(element, context: Dict[str, Any] = None) -> str:
    """Render PSX element to HTML string, evaluating {expressions} with `context`.

    Usage: `render_psx(element, context)`
    """
    if isinstance(element, PSXElement):
        return element.to_html(context)
    elif isinstance(element, str):
        if context and '{' in element and '}' in element:
            return _evaluate_expressions_in_string(element, context)
        return element
    else:
        return str(element)


class Component:
    """Base class for PSX components"""
    
    def render(self) -> PSXElement:
        """Override this method to define component rendering"""
        raise NotImplementedError("Component must implement render method")
    
    def __call__(self) -> PSXElement:
        """Make component callable"""
        return self.render()


def create_psx_function(psx_str: str):
    """Create a function that returns parsed PSX"""
    def psx_func():
        return psx(psx_str)
    return psx_func


# Decorator for components with PSX
def PSXComponent(func):
    """Decorator to create a component with PSX syntax - Pure Python only"""
    def wrapper(*args, **kwargs):
        # Get the source code of the function
        source = inspect.getsource(func)
        
        # Extract PSX from return statement - handle multiline PSX properly
        # Look for return ( <div>...</div> )
        psx_match = re.search(r'return\s*\(\s*(<[^>]*>(?:[^<]|<(?!/?)[^>]*>)*</[^>]+>)\s*\)', source, re.DOTALL)
        if psx_match:
            psx_str = psx_match.group(1)
            return psx(psx_str)
        else:
            # Try to find PSX without parentheses - return <div>...</div>
            psx_match = re.search(r'return\s+([ \t]*<[^>]*>(?:[^<]|<(?!/?)[^>]*>)*</[^>]+>[ \t]*)', source, re.DOTALL)
            if psx_match:
                psx_str = psx_match.group(1).strip()
                return psx(psx_str)
        
        # Fallback to regular function call
        return func(*args, **kwargs)
    
    return wrapper


# Alternative decorator that doesn't require source code parsing
def psx_component(func):
    """Simple PSX component decorator - works with direct PSX syntax"""
    def wrapper(*args, **kwargs):
        # Execute the function to get the PSX element
        result = func(*args, **kwargs)
        
        # If result is already a PSXElement, return it
        if hasattr(result, 'to_html'):
            return result
        
        # If result is a string that looks like PSX, parse it
        if isinstance(result, str) and result.strip().startswith('<'):
            return psx(result)
        
        return result
    
    return wrapper


# Python function helpers for common patterns
def create_onclick_handler(func: Callable) -> str:
    """Create a proper onclick handler from Python function"""
    func_name = getattr(func, '__name__', 'handler')
    register_python_function(func_name, func)
    return f"python_call_{func_name}"


def map_list(items: List[Any], func: Callable) -> List[Any]:
    """Python equivalent of JavaScript map function"""
    return [func(item) for item in items]


# Export all PSX components
__all__ = [
    'PSXElement', 'PSXParser', 'psx', 'render_psx', 'Component', 
    'PSXComponent', 'psx_component', 'create_psx_function', 'register_python_function',
    'create_onclick_handler', 'map_list'
]
