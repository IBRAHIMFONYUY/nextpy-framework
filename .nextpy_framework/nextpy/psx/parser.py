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
    
    def parse_psx(self, psx_str: str, context: Dict[str, Any] = None) -> Union[PSXElement, str]:
        """Parse PSX string to PSXElement with full capability"""
        print(f"DEBUG: PSXParser.parse_psx called with: {psx_str[:50]}...")
        context = context or {}
        
        # First process Python logic in the entire string
        psx_str = process_python_logic(psx_str, context)
        
        # Check for self-closing tags first
        self_closing_match = self.self_closing_pattern.match(psx_str)
        if self_closing_match:
            tag = self_closing_match.group(1)
            props_str = self_closing_match.group(2).strip()
            props = self.parse_props(props_str, context)
            
            # Extract key from props
            key = props.pop('key', None)
            
            return PSXElement(tag, props, [], key)
        
        # Check for regular tags
        tag_match = self.psx_pattern.match(psx_str)
        if tag_match:
            tag = tag_match.group(1)
            props_str = tag_match.group(2).strip()
            children_str = tag_match.group(3)
            
            # Parse props
            props = self.parse_props(props_str, context)
            
            # Parse children
            children = self.parse_children(children_str, context)
            
            # Extract key from props
            key = props.pop('key', None)
            
            return PSXElement(tag, props, children, key)
        
        # If no PSX tags found, treat as text
        return psx_str
    
    def parse_children(self, children_str: str, context: Dict[str, Any] = None) -> List[Union[str, PSXElement]]:
        """Parse children string with full PSX capability - Clean and simple"""
        children = []
        context = context or {}
        
        # Split by PSX tags and text - simple approach
        parts = re.split(r'(<[^>]+>)', children_str)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Check if it's an opening tag
            if part.startswith('<') and not part.startswith('</'):
                # Try to parse as PSX element
                try:
                    element = self.parse_psx(part, context)
                    children.append(element)
                except:
                    # If parsing fails, treat as text
                    children.append(part)
            elif part.startswith('</'):
                # Closing tag - skip
                continue
            else:
                # Text content - check for expressions
                if '{' in part and '}' in part:
                    # Process expressions in text
                    processed_part = self._evaluate_expressions_in_string(part, context)
                    children.append(processed_part)
                else:
                    children.append(part)
        
        return children


# Global parser instance
_parser = PSXParser()


def psx(psx_str: str, context: Dict[str, Any] = None) -> PSXElement:
    """
    Parse PSX string to PSXElement with full capability.
    Automatically captures local variables from the caller's frame.
    Optimized to only capture variables when braces are found.
    """
    import inspect
    
    # Only capture variables if PSX contains expressions (optimization)
    if '{' not in psx_str:
        # No expressions, skip variable capture for performance
        merged_context = context or {}
        print("DEBUG: No expressions found, skipping variable capture")
    else:
        # Enhanced variable capture - walk up the execution stack
        captured_locals = {}
    try:
            # Walk up the stack to find component function frames
            frame = inspect.currentframe().f_back
            stack_depth = 0
            max_depth = 10  # Prevent infinite loops
            
            while frame and stack_depth < max_depth:
                filename = frame.f_code.co_filename
                function_name = frame.f_code.co_name
                
                # Capture from user files (not in nextpy framework core, or in pages/components)
                is_user_file = (
                    'nextpy' not in filename or 
                    'pages' in filename or 
                    'components' in filename
                )
                
                # Skip internal frames but capture from component functions
                if is_user_file and function_name != '<module>':
                    # Filter out internal variables
                    frame_locals = frame.f_locals
                    filtered_locals = {
                        k: v for k, v in frame_locals.items()
                        if not k.startswith('_') and 
                           k not in ['frame', 'stack_depth', 'max_depth', 'captured_locals', 
                                        'psx_str', 'context', 'inspect'] and
                           not callable(v) and
                           not hasattr(v, '__call__')  # Skip functions/callables
                    }
                    captured_locals.update(filtered_locals)
                    
                    # Debug output for variable capture
                    print(f"DEBUG: Captured {len(filtered_locals)} variables from {function_name} in {filename}")
                    for key, value in list(filtered_locals.items())[:5]:  # Show first 5
                        print(f"  - {key}: {type(value).__name__}")
                    if len(filtered_locals) > 5:
                        print(f"  ... and {len(filtered_locals) - 5} more")
                
                frame = frame.f_back
                stack_depth += 1
                
    except Exception as e:
        print(f"DEBUG: Variable capture failed: {e}")
    
    # Merge provided context with captured locals (context takes precedence)
    merged_context = captured_locals.copy()
    if context:
        merged_context.update(context)
    
    print(f"DEBUG: Final merged context has {len(merged_context)} variables")
        
    try:
        # Try the clean tokenizer + stack parser first
        from .clean_parser import parse_psx_clean
        result = parse_psx_clean(psx_str, merged_context)
        print("DEBUG: Clean parser succeeded")
        return result
    except Exception as e:
        print(f"DEBUG: Clean parser failed: {e}")
        # Fallback to the old parser if clean parser fails
        return _parser.parse_psx(psx_str, merged_context)


def render_psx(element, context: Dict[str, Any] = None) -> str:
    """Render PSX element to HTML string with full PSX capability"""
    if isinstance(element, PSXElement):
        return element.to_html(context)
    elif isinstance(element, str):
        if context:
            # Process Python logic in string
            processed = process_python_logic(element, context)
            # Then evaluate expressions using the element's method
            if '{' in processed and '}' in processed:
                # Create a temporary element to access its method
                temp_element = PSXElement("div", {}, [])
                return temp_element._evaluate_expressions_in_string(processed, context)
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
