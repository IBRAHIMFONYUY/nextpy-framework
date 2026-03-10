"""
PSX Parser - Core parsing and rendering functionality
Supports full PSX capability: Expressions, Conditions, Lists, Components, Props, Events, Fragments, Dynamic attributes, Inline styles, Children, Keys, Spread props, Self-closing tags, AND REVOLUTIONARY PYTHON LOGIC!
"""

import re
from typing import Any, Dict, List, Union, Optional
from dataclasses import dataclass
from .python_logic import process_python_logic


@dataclass
class PSXElement:
    """Represents a PSX (Python Syntax eXtension) element with full capability"""
    tag: str
    props: Dict[str, Any]
    children: List[Union[str, 'PSXElement']]
    key: Optional[str] = None
    
    def __str__(self) -> str:
        """Convert to HTML string"""
        return self.to_html()
    
    def to_html(self, context: Dict[str, Any] = None) -> str:
        """Convert PSX element to HTML string with full PSX capability"""
        context = context or {}
        
        # Process revolutionary Python logic in children first
        processed_children = []
        for child in self.children:
            if isinstance(child, str):
                # Process Python logic in text content
                processed_child = process_python_logic(child, context)
                processed_children.append(processed_child)
            elif isinstance(child, PSXElement):
                # Recursively process child elements
                processed_children.append(child)
            else:
                processed_children.append(str(child))
        
        # Build props string with full PSX capability
        props_str = self._build_props_string(context)
        
        # Build children string
        children_str = self._build_children_string(processed_children, context)
        
        # Handle self-closing tags
        self_closing_tags = {
            'img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col',
            'embed', 'source', 'track', 'wbr', 'command', 'keygen', 'menuitem', 'param'
        }

        if self.tag in self_closing_tags and not children_str:
            return f"<{self.tag}{props_str} />"

        # Add key if present
        key_attr = f' key="{self.key}"' if self.key else ''
        
        return f"<{self.tag}{props_str}{key_attr}>{children_str}</{self.tag}>"
    
    def _build_props_string(self, context: Dict[str, Any]) -> str:
        """Build props string with full PSX capability"""
        props_list = []
        
        for key, value in self.props.items():
            # Skip special PSX props
            if key in ['key', 'children']:
                continue
            
            # Map React-style `className` to HTML `class`
            attr_name = 'class' if key == 'className' else key
            
            # Handle different value types
            if isinstance(value, bool) and value:
                props_list.append(attr_name)
            elif value is not None and value != "":
                # Process Python logic in prop values
                if isinstance(value, str):
                    # Check for Python logic in props
                    if '{python:' in value or '{py:' in value or '{for ' in value or '{if ' in value:
                        processed_value = process_python_logic(value, context)
                        props_list.append(f'{attr_name}="{processed_value}"')
                    # Handle expressions
                    elif '{' in value and '}' in value:
                        processed_value = self._evaluate_expressions_in_string(value, context)
                        props_list.append(f'{attr_name}="{processed_value}"')
                    else:
                        props_list.append(f'{attr_name}="{value}"')
                elif callable(value):
                    # Handle event handlers
                    func_name = getattr(value, '__name__', 'handler')
                    props_list.append(f'{attr_name}="python_call_{func_name}"')
                else:
                    props_list.append(f'{attr_name}="{value}"')
        
        return " " + " ".join(props_list) if props_list else ""
    
    def _build_children_string(self, children: List[Union[str, 'PSXElement']], context: Dict[str, Any]) -> str:
        """Build children string with full PSX capability"""
        children_parts = []
        
        for child in children:
            if isinstance(child, PSXElement):
                children_parts.append(child.to_html(context))
            else:
                # Process any remaining expressions
                if isinstance(child, str) and '{' in child and '}' in child:
                    processed_child = self._evaluate_expressions_in_string(child, context)
                    children_parts.append(processed_child)
                else:
                    children_parts.append(str(child))
        
        return "".join(children_parts)
    
    def _evaluate_expressions_in_string(self, s: str, context: Dict[str, Any]) -> str:
        """Find {expressions} in string and evaluate them using context"""
        def repl(match):
            expr = match.group(1).strip()
            try:
                # Check for Python logic
                if expr.startswith('python:') or expr.startswith('py:') or expr.startswith('for ') or expr.startswith('if '):
                    return process_python_logic(f'{{{expr}}}', context)
                else:
                    # Regular expression evaluation
                    return str(eval(expr, {}, context))
            except Exception:
                return f'{{expr error: {expr}}}'

        return re.sub(r'\{([^}]+)\}', repl, s)


class PSXParser:
    """Parse PSX syntax with full capability including revolutionary Python logic"""
    
    def __init__(self):
        self.psx_pattern = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)\s*([^>]*)>(.*?)</\1>', re.DOTALL)
        self.self_closing_pattern = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)\s*([^>]*)\s*/>', re.DOTALL)
        self.prop_pattern = re.compile(
            r'([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*\{([^}]+)\}|'
            r'([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*"([^"]*)"|'
            r'([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*\'([^\']*)\'|'
            r'([a-zA-Z][a-zA-Z0-9-]+)|'
            r'(\.\.\.\w+)'  # Spread props
        )
    
    def parse_props(self, props_str: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Parse PSX props string with full capability"""
        props = {}
        context = context or {}
        
        if not props_str.strip():
            return props
        
        for match in self.prop_pattern.finditer(props_str):
            groups = match.groups()
            
            if groups[0] and groups[1]:  # {prop} syntax - Python expression
                prop_name = groups[0]
                prop_value = groups[1].strip()
                props[prop_name] = '{' + prop_value + '}'
            elif groups[2] and groups[3]:  # "prop" syntax
                props[groups[2]] = groups[3]
            elif groups[4] and groups[5]:  # 'prop' syntax
                props[groups[4]] = groups[5]
            elif groups[6]:  # prop without value (boolean)
                props[groups[6]] = True
            elif groups[7]:  # spread props ...props
                spread_name = groups[7][3:]  # Remove ...
                if spread_name in context:
                    spread_value = context[spread_name]
                    if isinstance(spread_value, dict):
                        props.update(spread_value)
        
        return props
    
    def parse_psx(self, psx_str: str, context: Dict[str, Any] = None) -> PSXElement:
        """Parse PSX string to PSXElement with full capability"""
        psx_str = psx_str.strip()
        context = context or {}
        
        # Process revolutionary Python logic first
        psx_str = process_python_logic(psx_str, context)
        
        # Try self-closing tag first
        self_closing_match = self.self_closing_pattern.match(psx_str)
        if self_closing_match:
            tag = self_closing_match.group(1)
            props_str = self_closing_match.group(2)
            props = self.parse_props(props_str, context)
            return PSXElement(tag, props, [])
        
        # Try regular tag
        match = self.psx_pattern.match(psx_str)
        if match:
            tag = match.group(1)
            props_str = match.group(2)
            children_str = match.group(3)
            
            props = self.parse_props(props_str, context)
            children = self.parse_children(children_str, context)
            
            # Extract key from props
            key = props.pop('key', None)
            
            return PSXElement(tag, props, children, key)
        
        # If no PSX tags found, treat as text
        return psx_str
    
    def parse_children(self, children_str: str, context: Dict[str, Any] = None) -> List[Union[str, PSXElement]]:
        """Parse children string with full PSX capability"""
        children = []
        context = context or {}
        
        # Process Python logic in children first
        children_str = process_python_logic(children_str, context)
        
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
                    
                    children.append(self.parse_psx(psx_content, context))
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
_parser = PSXParser()


def psx(psx_str: str, context: Dict[str, Any] = None) -> PSXElement:
    """Parse PSX string to PSXElement with full capability"""
    return _parser.parse_psx(psx_str, context)


def _evaluate_expressions_in_string(s: str, context: Dict[str, Any]) -> str:
    """Find {expressions} in string and evaluate them using context"""
    def repl(match):
        expr = match.group(1).strip()
        try:
            # Check for Python logic
            if expr.startswith('python:') or expr.startswith('py:') or expr.startswith('for ') or expr.startswith('if '):
                return process_python_logic(f'{{{expr}}}', context)
            else:
                return str(eval(expr, {}, context))
        except Exception:
            return f'{{expr error: {expr}}}'

    return re.sub(r'\{([^}]+)\}', repl, s)


def render_psx(element, context: Dict[str, Any] = None) -> str:
    """Render PSX element to HTML string with full PSX capability"""
    if isinstance(element, PSXElement):
        return element.to_html(context)
    elif isinstance(element, str):
        if context:
            # Process Python logic in string
            processed = process_python_logic(element, context)
            # Then evaluate expressions
            if '{' in processed and '}' in processed:
                return _evaluate_expressions_in_string(processed, context)
            return processed
        return element
    else:
        return str(element)


# Revolutionary PSX Features
def fragment(children: Any) -> str:
    """Fragment component for multiple children"""
    if isinstance(children, list):
        return ''.join(str(child) for child in children)
    elif hasattr(children, 'to_html'):
        return children.to_html()
    else:
        return str(children)


def key(key_value: str, element: PSXElement) -> PSXElement:
    """Add key to PSX element"""
    element.key = key_value
    return element


# Export all PSX components
__all__ = [
    'PSXElement', 'PSXParser', 'psx', 'render_psx', 
    'fragment', 'key', 'process_python_logic'
]
