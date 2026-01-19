"""
True JSX Parser for Python - Parse actual JSX syntax in Python files
Allows writing <div>...</div> directly in Python code
"""

import re
import ast
import inspect
from typing import Any, Dict, List, Union
from dataclasses import dataclass


@dataclass
class JSXElement:
    """Represents a JSX element"""
    tag: str
    props: Dict[str, Any]
    children: List[Union[str, 'JSXElement']]
    
    def __str__(self) -> str:
        """Convert to HTML string"""
        return self.to_html()
    
    def to_html(self) -> str:
        """Convert JSX element to HTML string"""
        # Build props string
        props_str = ""
        if self.props:
            props_list = []
            for key, value in self.props.items():
                if isinstance(value, bool) and value:
                    props_list.append(key)
                elif value is not None and value != "":
                    if key.startswith("on_") and callable(value):
                        continue
                    props_list.append(f'{key}="{value}"')
            props_str = " " + " ".join(props_list) if props_list else ""

        # Build children string
        children_str = ""
        if self.children:
            children_parts = []
            for child in self.children:
                if isinstance(child, JSXElement):
                    children_parts.append(child.to_html())
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


class JSXParser:
    """Parse JSX syntax from Python source code"""
    
    def __init__(self):
        self.jsx_pattern = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)\s*([^>]*)>(.*?)</\1>', re.DOTALL)
        self.self_closing_pattern = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)\s*([^>]*)\s*/>', re.DOTALL)
        self.prop_pattern = re.compile(r'([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*\{([^}]+)\}|([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*"([^"]*)"|([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*\'([^\']*)\'|([a-zA-Z][a-zA-Z0-9-]+)')
    
    def parse_props(self, props_str: str) -> Dict[str, Any]:
        """Parse JSX props string"""
        props = {}
        if not props_str.strip():
            return props
        
        # Simple prop parsing - can be enhanced
        for match in self.prop_pattern.finditer(props_str):
            groups = match.groups()
            if groups[0] and groups[1]:  # {prop} syntax
                prop_name = groups[0]
                prop_value = groups[1].strip()
                # Try to evaluate as Python expression
                try:
                    props[prop_name] = eval(prop_value)
                except:
                    props[prop_name] = prop_value
            elif groups[2] and groups[3]:  # "prop" syntax
                props[groups[2]] = groups[3]
            elif groups[4] and groups[5]:  # 'prop' syntax
                props[groups[4]] = groups[5]
            elif groups[6]:  # prop without value (boolean)
                props[groups[6]] = True
        
        return props
    
    def parse_jsx(self, jsx_str: str) -> JSXElement:
        """Parse JSX string to JSXElement"""
        jsx_str = jsx_str.strip()
        
        # Try self-closing tag first
        self_closing_match = self.self_closing_pattern.match(jsx_str)
        if self_closing_match:
            tag = self_closing_match.group(1)
            props_str = self_closing_match.group(2)
            props = self.parse_props(props_str)
            return JSXElement(tag, props, [])
        
        # Try regular tag
        match = self.jsx_pattern.match(jsx_str)
        if match:
            tag = match.group(1)
            props_str = match.group(2)
            children_str = match.group(3)
            
            props = self.parse_props(props_str)
            children = self.parse_children(children_str)
            
            return JSXElement(tag, props, children)
        
        # If no JSX tags found, treat as text
        return jsx_str
    
    def parse_children(self, children_str: str) -> List[Union[str, JSXElement]]:
        """Parse children string"""
        children = []
        
        # Split by JSX tags and text
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
                    # Find the complete JSX element
                    jsx_content = part
                    depth = 1
                    j = i + 1
                    
                    while j < len(parts) and depth > 0:
                        if parts[j].startswith(f'</{tag}>'):
                            depth -= 1
                        elif parts[j].startswith(f'<{tag}') and not parts[j].startswith('</'):
                            depth += 1
                        jsx_content += parts[j]
                        j += 1
                    
                    children.append(self.parse_jsx(jsx_content))
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
parser = JSXParser()


def jsx(jsx_str: str) -> JSXElement:
    """Parse JSX string to JSXElement"""
    return parser.parse_jsx(jsx_str)


def render_jsx(element) -> str:
    """Render JSX element to HTML string"""
    if isinstance(element, JSXElement):
        return element.to_html()
    elif isinstance(element, str):
        return element
    else:
        return str(element)


class Component:
    """Base class for JSX components"""
    
    def render(self) -> JSXElement:
        """Override this method to define component rendering"""
        raise NotImplementedError("Component must implement render method")
    
    def __call__(self) -> JSXElement:
        """Make component callable"""
        return self.render()


def create_jsx_function(jsx_str: str):
    """Create a function that returns parsed JSX"""
    def jsx_func():
        return jsx(jsx_str)
    return jsx_func


# Decorator for components with JSX
def JSXComponent(func):
    """Decorator to create a component with JSX syntax"""
    def wrapper(*args, **kwargs):
        # Get the source code of the function
        source = inspect.getsource(func)
        
        # Extract JSX from return statement
        jsx_match = re.search(r'return\s*\(\s*(<.*?>)\s*\)', source, re.DOTALL)
        if jsx_match:
            jsx_str = jsx_match.group(1)
            return jsx(jsx_str)
        else:
            # Try to find JSX without parentheses
            jsx_match = re.search(r'return\s*(<.*?>)', source, re.DOTALL)
            if jsx_match:
                jsx_str = jsx_match.group(1)
                return jsx(jsx_str)
        
        # Fallback to regular function call
        return func(*args, **kwargs)
    
    return wrapper
