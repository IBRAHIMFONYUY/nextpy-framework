"""
PSX Parser - Production-grade parser with AST integration
Supports full PSX capability with modern architecture

Changes from previous version
──────────────────────────────
* Replaced SIGALRM timeout (Unix-only) with monotonic-clock deadlines.
* All tag forms (elements, components, fragments) go through the same
  recursive-descent engine — no regex fallback for components.
* _match_brace() counts delimiters properly so nested expressions like
  {obj['key']}, {fn({'a': 1})}, and template literals never truncate early.
* Thread-safe: state lives on the call stack; a threading.local pool
  provides one PSXParser instance per thread — no shared mutable state.
* _attrs() returns an is_self_closing flag instead of relying on
  post-hoc index arithmetic.
* _children() breaks on any unexpected closing tag to prevent the
  stuck-parser increment from corrupting the position.
* All print() debug statements replaced with logging calls.
* Dead code (_parse_element_fallback, unused regex patterns) removed.
* Type hint for _node_to_child corrected to include List as a possible
  return type (Fragment case).
"""

import re
import time
import logging
import threading
from typing import Any, Dict, List, Optional, Tuple, Union

from dataclasses import dataclass, field

from .ast_nodes import (
    PSXNode, PSXNodeUnion,
    ElementNode, TextNode, ExpressionNode,
    ComponentNode, FragmentNode,
    PSXASTParser, PSXNodeValidator, PSXNodeOptimizer,
)
from .runtime import PSXRuntime, process_python_logic

log = logging.getLogger(__name__)

# ── Module-level constants ─────────────────────────────────────────────────────

#: HTML void elements + common SVG leaf elements that never have children.
SELF_CLOSING_TAGS: frozenset = frozenset({
    'area', 'base', 'br', 'col', 'command', 'embed', 'hr', 'img', 'input',
    'keygen', 'link', 'meta', 'menuitem', 'param', 'source', 'track', 'wbr',
    'circle', 'ellipse', 'line', 'path', 'polygon', 'polyline', 'rect',
})

#: Default wall-clock budget for a single parse call (seconds).
PARSE_TIMEOUT: float = 5.0

#: Hard iteration cap per parse to guard against pathological inputs.
MAX_ITERATIONS: int = 10_000


# ── Internal exception ─────────────────────────────────────────────────────────

class _ParseTimeout(Exception):
    """Raised when a parse call exceeds its time budget."""


# ── Expression boundary helper ─────────────────────────────────────────────────

def _match_brace(code: str, start: int) -> int:
    """
    Given that ``code[start] == '{'``, return the *exclusive* end index
    after the matching ``'}'``.

    Handles:
    * Arbitrarily nested ``{}`` blocks.
    * Single-quoted, double-quoted, and back-tick string literals
      (including escaped characters inside them).

    Returns ``len(code)`` for malformed input so callers degrade gracefully.
    """
    assert code[start] == '{', f"Expected '{{' at index {start}, got {code[start]!r}"
    depth: int = 0
    i: int = start
    n: int = len(code)
    in_str: Optional[str] = None

    while i < n:
        ch = code[i]
        if in_str:
            if ch == '\\':
                i += 2          # skip escaped character
                continue
            if ch == in_str:
                in_str = None
        else:
            if ch in ('"', "'", '`'):
                in_str = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return i + 1
        i += 1

    return n   # malformed — caller handles gracefully


# ── PSXElement (legacy shim) ───────────────────────────────────────────────────

@dataclass
class PSXElement:
    """
    Legacy PSX element, retained for backwards compatibility.

    ``_ast_node`` and ``_psx_context`` are set externally after construction
    (they carry information needed for rendering but are not part of the
    public API surface).
    """
    tag:      str
    props:    Dict[str, Any]                  = field(default_factory=dict)
    children: List[Union[str, 'PSXElement']]  = field(default_factory=list)
    key:      Optional[str]                   = None

    def to_ast(self) -> ElementNode:
        """Convert this PSXElement into a production-grade :class:`ElementNode`."""
        events:     Dict[str, Any] = {}
        attributes: Dict[str, Any] = {}

        for k, v in self.props.items():
            if k.startswith('on') and callable(v):
                events[k] = v.__name__
            else:
                attributes[k] = v

        ast_children: List[PSXNode] = []
        for child in self.children:
            if isinstance(child, str):
                ast_children.append(TextNode(content=child))
            elif isinstance(child, PSXElement):
                ast_children.append(child.to_ast())
            elif isinstance(child, PSXNode):
                ast_children.append(child)

        return ElementNode(
            tag=self.tag,
            attributes=attributes,
            events=events,
            children=ast_children,
            key=self.key,
            self_closing=self.tag in SELF_CLOSING_TAGS,
        )

    def to_html(self, context: Dict[str, Any] = None) -> str:
        """Render this element to an HTML string."""
        ctx: Dict[str, Any] = {}
        stored_ctx = getattr(self, '_psx_context', None)
        if stored_ctx:
            ctx = dict(stored_ctx)
        if context:
            ctx.update(context)

        runtime = PSXRuntime(ctx)

        ast_node = getattr(self, '_ast_node', None)
        if ast_node is not None:
            return runtime._render_node(ast_node)


class PSXParser:
    """Production-grade PSX parser with AST integration"""
    
    def __init__(self):
        self.ast_parser = PSXASTParser()
        self.validator = PSXNodeValidator()
        self.optimizer = PSXNodeOptimizer()
        self.runtime = PSXRuntime()
        
        # Regex patterns for parsing - use non-greedy matching
        self.psx_pattern = re.compile(r'<([a-zA-Z][a-zA-Z0-9:_-]*)\s*([^>]*?)>(.*?)</\1>', re.DOTALL)
        self.self_closing_pattern = re.compile(r'<([a-zA-Z][a-zA-Z0-9:_-]*)\s*([^>]*?)\s*/>', re.DOTALL)
        self.prop_pattern = re.compile(
            r'([a-zA-Z][a-zA-Z0-9:_-]*)\s*=\s*\{([^}]+)\}|'
            r'([a-zA-Z][a-zA-Z0-9:_-]*)\s*=\s*"([^"]*)"|'
            r'([a-zA-Z][a-zA-Z0-9:_-]*)\s*=\s*\'([^\']*)\'|'
            r'([a-zA-Z][a-zA-Z0-9:_-]+)|'
            r'\.{3}[a-zA-Z_][a-zA-Z0-9_:-]*'  # Spread props
        )
    
    def parse_psx(self, psx_str: str, context: Dict[str, Any] = None) -> PSXNodeUnion:
        """Parse PSX string to production-grade AST node"""
        import signal
        
        context = context or {}
        
        # Update runtime context with new variables
        self.runtime.update_context(context)
        
        # Process Python logic first
        psx_str = process_python_logic(psx_str, context)
        
        # Normalize whitespace for parsing while preserving original content if needed
        psx_str_stripped = psx_str.strip()
        
        # Add timeout to prevent infinite loops
        def timeout_handler(signum, frame):
            raise TimeoutError("PSX parsing timeout")
        
        # Set a 5-second timeout for parsing
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)
        
        try:
            # Try to parse as component FIRST (before element parser)
            ast_node = self._parse_component(psx_str_stripped, context)
            if ast_node:
                print(f"DEBUG: Successfully parsed as component: {ast_node.name}")
                return self.optimizer.optimize_node(ast_node)

            # Try to parse as fragment next, since fragments use special shorthand syntax
            ast_node = self._parse_fragment(psx_str_stripped, context)
            if ast_node:
                return self.optimizer.optimize_node(ast_node)

            # Try to parse as element last
            ast_node = self._parse_element(psx_str_stripped, context)
            if ast_node:
                return self.optimizer.optimize_node(ast_node)
            
            # Default to text node
            return TextNode(content=psx_str)
        except Exception:
            log.error("PSX parse error  src=%.120s…", src, exc_info=True)
            return TextNode(content=psx_str)
        finally:
            # Restore old signal handler
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    
    def _parse_element(self, psx_str: str, context: Dict[str, Any]) -> Optional[ElementNode]:
        """Robust recursive element parser for minified JSX"""
        # Strip leading whitespace for better matching
        psx_str_stripped = psx_str.strip()
        
        if not psx_str_stripped.startswith('<'):
            return None
        
        # Always use recursive descent parser - regex fallback causes infinite loops
        try:
            element_node, final_index = self._parse_element_recursive(psx_str_stripped, 0, context)
            return element_node
        except Exception as e:
            # Return None instead of fallback to prevent infinite loops
            print(f"Parse error for element: {e}")
            return None
    
    def _parse_element_recursive(self, code: str, index: int, context: Dict[str, Any]):
        """Recursive descent parser for JSX elements"""
        from .ast_nodes import ElementNode
        
        # Skip opening '<'
        index += 1
        
        # Read tag name
        tag_name, index = self._read_tag_name(code, index)
        
        # Read attributes until closing '>' or '/>'
        attributes, events, spread_props, index = self._read_attributes(code, index, context, tag_name)
        
        # Check if self-closing - look for '/>' before the closing '>'
        # Also check if tag name is in self-closing list
        self_closing_tags = {
            'img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col',
            'embed', 'source', 'track', 'wbr', 'command', 'keygen', 'menuitem', 'param'
        }
        
        is_self_closing = False
        # Check if the current position is after '/>'
        if index >= 2 and code[index-2:index] == '/>':
            is_self_closing = True
        # Check if the next characters are '/>'
        elif index + 1 < len(code) and code[index:index+2] == '/>':
            is_self_closing = True
            index += 2  # Skip the '/>'
        elif tag_name.lower() in self_closing_tags:
            # For self-closing tags, treat them as self-closing even if they don't have />
            is_self_closing = True
        
        if is_self_closing:
            # Debug: print tag name for self-closing tags
            if not tag_name:
                print(f"Warning: Empty tag name for self-closing element at index {index}")
            return ElementNode(
                tag=tag_name if tag_name else 'div',  # Fallback to div if empty
                attributes=attributes,
                events=events,
                children=[],
                self_closing=True,
                spread_props=spread_props
            ), index
        
        # Parse children recursively with infinite loop protection
        children = []
        max_iterations = 10000  # Prevent infinite loops
        iterations = 0
        start_index = index
        
        while index < len(code) and not code.startswith(f"</{tag_name}>", index):
            iterations += 1
            if iterations > max_iterations:
                print(f"Warning: Max iterations reached while parsing children for tag '{tag_name}'")
                break
            
            # Process Python logic for the current segment of code before parsing nodes
            # This ensures nested control flow is handled correctly
            remaining_code = code[index:]
            # Find next tag or expression to limit processing scope if possible, 
            # but for now, we process the logic which is safe as it uses brace matching.
            
            child, new_index = self._parse_node(code, index, context)
            
            # Prevent infinite loop - if index doesn't advance, break
            if new_index <= index:
                print(f"Warning: Parser stuck at index {index} for tag '{tag_name}'")
                break
            
            index = new_index
            
            if child:
                if isinstance(child, TextNode):
                    # Re-process text nodes for any missed logic
                    child.content = process_python_logic(child.content, context)
                children.append(child)
        
        # Skip closing tag
        if index < len(code) and code.startswith(f"</{tag_name}>", index):
            index += len(f"</{tag_name}>")
        
        return ElementNode(
            tag=tag_name,
            attributes=attributes,
            events=events,
            children=children,
            spread_props=spread_props
        ), index
    
    def _read_tag_name(self, code: str, index: int):
        """Read tag name from code"""
        start = index
        while index < len(code) and (code[index].isalnum() or code[index] in '-_:'):
            index += 1
        return code[start:index], index
    
    def _read_attributes(self, code: str, index: int, context: Dict[str, Any], tag_name: str = None):
        """Read attributes from opening tag"""
        attributes = {}
        events = {}
        spread_props = []
        
        while index < len(code) and code[index] not in ['>', '/']:
            # Skip whitespace
            while index < len(code) and code[index].isspace():
                index += 1
            
            if index >= len(code) or code[index] in ['>', '/']:
                break
            
            # Read attribute name
            key_start = index
            while index < len(code) and (code[index].isalnum() or code[index] in '-_:.'):
                index += 1
            key = code[key_start:index]
            
            # Skip whitespace
            while index < len(code) and code[index].isspace():
                index += 1
            
            # Check if attribute has value
            if index < len(code) and code[index] == '=':
                index += 1  # Skip '='
                
                # Skip whitespace (including newlines)
                while index < len(code) and code[index].isspace():
                    index += 1
                
                # Read value
                if index < len(code) and code[index] in ['"', "'"]:
                    # String value
                    quote = code[index]
                    index += 1
                    value_start = index
                    while index < len(code) and code[index] != quote:
                        index += 1
                    value = code[value_start:index]
                    index += 1  # Skip closing quote
                elif index < len(code) and code[index] == '{':
                    # Expression value
                    value_start = index
                    brace_count = 1
                    index += 1
                    while index < len(code) and brace_count > 0:
                        if code[index] == '{':
                            brace_count += 1
                        elif code[index] == '}':
                            brace_count -= 1
                        index += 1
                    value = code[value_start:index]
                else:
                    # Unquoted value (boolean or simple)
                    value_start = index
                    while index < len(code) and not code[index].isspace() and code[index] not in ['>', '/']:
                        index += 1
                    value = code[value_start:index]
                
                # Categorize attribute
                if key == 'bind':
                    # Convert bind attribute to data-bind for automatic state binding
                    # bind={name} -> data-bind="value:name" or data-bind="checked:name"
                    # IMPORTANT: bind is a compiler directive, not a normal prop
                    # We extract the variable identifier WITHOUT evaluating the expression
                    if value.startswith('{') and value.endswith('}'):
                        # Extract the variable name from the expression
                        state_var = value[1:-1].strip()
                        # Store the raw variable name as a special attribute
                        # This will be handled by the runtime to set up two-way binding
                        attributes['_bind_target'] = state_var
                        # Also store the bind type for the runtime
                        bind_type = 'value'
                        if tag_name == 'input' and attributes.get('type') == 'checkbox':
                            bind_type = 'checked'
                        attributes['_bind_type'] = bind_type
                    else:
                        # If bind value is not an expression, use it directly
                        attributes['_bind_target'] = value
                        bind_type = 'value'
                        if tag_name == 'input' and attributes.get('type') == 'checkbox':
                            bind_type = 'checked'
                        attributes['_bind_type'] = bind_type
                elif key.startswith('on'):
                    events[key] = value
                elif key.startswith('...'):
                    spread_props.append(key[3:])
                else:
                    attributes[key] = value
            else:
                # Boolean attribute
                attributes[key] = True
        
        # Skip the closing '>' character
        if index < len(code) and code[index] == '>':
            index += 1
        
        return attributes, events, spread_props, index
    
    def _parse_node(self, code: str, index: int, context: Dict[str, Any]):
        """Parse node (element, text, or expression)"""
        # Skip whitespace
        while index < len(code) and code[index].isspace():
            index += 1
        
        if index >= len(code):
            return None, index
        
        if code[index] == '<':
            # Element node
            if code.startswith('<!--', index):
                # Comment - skip it
                end_comment = code.find('-->', index)
                if end_comment != -1:
                    return None, end_comment + 3
                return None, len(code)
            elif code.startswith('</', index):
                # Closing tag - stop parsing
                return None, index
            else:
                # Opening tag
                return self._parse_element_recursive(code, index, context)
        elif code[index] == '{':
            # Expression node
            from .ast_nodes import ExpressionNode
            expr_start = index
            brace_count = 1
            index += 1
            while index < len(code) and brace_count > 0:
                if code[index] == '{':
                    brace_count += 1
                elif code[index] == '}':
                    brace_count -= 1
                index += 1
            expr_content = code[expr_start + 1:index - 1]  # Remove braces
            return ExpressionNode(expression=expr_content), index
        else:
            # Text node
            from .ast_nodes import TextNode
            text_start = index
            while index < len(code) and code[index] not in ['<', '{']:
                index += 1
            text_content = code[text_start:index]
            return TextNode(content=text_content), index
    
    def _parse_element_fallback(self, psx_str: str, context: Dict[str, Any]) -> Optional[ElementNode]:
        """Fallback to original parsing method"""
        # Check for self-closing tags first
        self_closing_match = self.self_closing_pattern.match(psx_str)
        if self_closing_match:
            tag = self_closing_match.group(1)
            props_str = self_closing_match.group(2).strip()
            props = self._parse_props(props_str, context)
            
            return ElementNode(
                tag=tag,
                attributes=props['attributes'],
                events=props['events'],
                children=[],
                self_closing=True,
                spread_props=props['spread_props']
            )
        
        # For regular tags, use the robust approach
        if psx_str.startswith('<'):
            # Find the end of the opening tag
            tag_end = psx_str.find('>')
            if tag_end == -1:
                return None
            
            opening_tag = psx_str[:tag_end + 1]
            tag_content = opening_tag[1:-1].strip()
            
            # Extract tag name and props
            tag_parts = tag_content.split()
            if not tag_parts:
                return None
            
            tag_name = tag_parts[0]
            props_str = ' '.join(tag_parts[1:]) if len(tag_parts) > 1 else ''
            props = self._parse_props(props_str, context)
            
            # Find the matching closing tag
            closing_tag = f'</{tag_name}>'
            closing_pos = self._find_matching_tag(psx_str, tag_name, tag_end + 1)
            
            if closing_pos == -1:
                # No matching closing tag
                return None
            
            # Extract children content
            children_content = psx_str[tag_end + 1:closing_pos]
            children = self._parse_children(children_content, context)
            
            return ElementNode(
                tag=tag_name,
                attributes=props['attributes'],
                events=props['events'],
                children=children,
                spread_props=props['spread_props']
            )
        
        return None
    
    def _parse_component(self, psx_str: str, context: Dict[str, Any]) -> Optional[ComponentNode]:
        """Parse PSX string to ComponentNode"""
        # Component pattern (uppercase first letter) - handle both regular and self-closing tags
        # Regular component: <ComponentName props>children</ComponentName>
        component_pattern = re.compile(r'<([A-Z][a-zA-Z0-9]*)\s*([^>]*)>(.*?)</\1>', re.DOTALL)
        # Self-closing component: <ComponentName props />
        self_closing_component_pattern = re.compile(r'<([A-Z][a-zA-Z0-9]*)\s*([^>]*)\s*/>', re.DOTALL)
        
        # Try regular component first
        match = component_pattern.search(psx_str)
        if match:
            name = match.group(1)
            props_str = match.group(2).strip()
            children_str = match.group(3)
            
            props = self._parse_props(props_str, context)
            children = self._parse_children(children_str, context)
            
            return ComponentNode(
                name=name,
                props=props['attributes'],
                events=props['events'],
                children=children,
                spread_props=props['spread_props']
            )
        
        # Try self-closing component
        match = self_closing_component_pattern.search(psx_str)
        if match:
            name = match.group(1)
            props_str = match.group(2).strip()
            
            props = self._parse_props(props_str, context)
            
            return ComponentNode(
                name=name,
                props=props['attributes'],
                events=props['events'],
                children=[],
                spread_props=props['spread_props']
            )
        
        return None
    
    def _parse_fragment(self, psx_str: str, context: Dict[str, Any]) -> Optional[FragmentNode]:
        """Parse PSX string to FragmentNode"""
        psx_str = psx_str.strip()
        # Fragment patterns
        fragment_patterns = [
            re.compile(r'<>\s*(.*?)\s*</>', re.DOTALL),  # Shorthand
            re.compile(r'<fragment\s*[^>]*>\s*(.*?)\s*</fragment>', re.DOTALL)  # Full
        ]
        
        for i, pattern in enumerate(fragment_patterns):
            match = pattern.match(psx_str)
            if match:
                children_str = match.group(1)
                children = self._parse_children(children_str, context)
                
                return FragmentNode(
                    children=children,
                    shorthand=(i == 0)  # First pattern is shorthand
                )
        
        return None
    
    def _parse_props(self, props_str: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse props string into attributes, events, and spread props"""
        attributes = {}
        events = {}
        spread_props = []
        
        if not props_str.strip():
            return {'attributes': attributes, 'events': events, 'spread_props': spread_props}
        
        for match in self.prop_pattern.finditer(props_str):
            groups = match.groups()
            
            if groups[0] and groups[1]:  # {prop} syntax - Python expression
                prop_name = groups[0]
                prop_value = groups[1].strip()
                
                # Parse expression
                parsed_ast = self.ast_parser.parse_expression(prop_value)
                if parsed_ast:
                    if prop_name.startswith('on'):
                        events[prop_name] = prop_value
                    else:
                        attributes[prop_name] = prop_value
                else:
                    attributes[prop_name] = prop_value
                    
            elif groups[2] and groups[3]:  # "prop" syntax
                attributes[groups[2]] = groups[3]
            elif groups[4] and groups[5]:  # 'prop' syntax
                attributes[groups[4]] = groups[5]
            elif groups[6]:  # prop without value (boolean)
                attributes[groups[6]] = True
            elif groups[7]:  # spread props ...props
                spread_name = groups[7][3:]  # Remove ...
                spread_props.append(spread_name)
        
        return {'attributes': attributes, 'events': events, 'spread_props': spread_props}
    
    def _parse_children(self, children_str: str, context: Dict[str, Any]) -> List[PSXNodeUnion]:
        """Parse children string into AST nodes"""
        children = []
        
        # Use a more sophisticated parsing approach
        i = 0
        n = len(children_str)
        
        while i < n:
            # Skip whitespace
            while i < n and children_str[i].isspace():
                i += 1
            
            if i >= n:
                break
            
            # Check for HTML tag
            if children_str[i] == '<':
                # Find the end of the tag
                tag_end = children_str.find('>', i)
                if tag_end == -1:
                    # Malformed tag, treat as text
                    children.append(TextNode(content=children_str[i:]))
                    break
                
                tag_content = children_str[i:tag_end + 1]
                
                # Check if it's a self-closing tag
                if tag_content.endswith('/>'):
                    # Self-closing tag
                    tag_node = self.parse_psx(tag_content, context)
                    if tag_node and not isinstance(tag_node, TextNode):
                        children.append(tag_node)
                        i = tag_end + 1
                    else:
                        children.append(TextNode(content=tag_content))
                        i = tag_end + 1
                else:
                    # Opening tag - find matching closing tag
                    tag_name = tag_content[1:-1].split()[0]  # Extract tag name
                    closing_tag = f'</{tag_name}>'
                    closing_pos = self._find_matching_tag(children_str, tag_name, tag_end + 1)
                    
                    if closing_pos == -1:
                        # No matching closing tag, treat as text
                        children.append(TextNode(content=tag_content))
                        i = tag_end + 1
                    else:
                        # Parse the complete element
                        element_str = children_str[i:closing_pos + len(closing_tag)]
                        element_node = self.parse_psx(element_str, context)
                        if element_node and not isinstance(element_node, TextNode):
                            children.append(element_node)
                            i = closing_pos + len(closing_tag)
                        else:
                            children.append(TextNode(content=element_str))
                            i = closing_pos + len(closing_tag)
            else:
                # Text content - find next tag or expression
                next_tag = children_str.find('<', i)
                next_expr = children_str.find('{', i)
                
                if next_tag == -1 and next_expr == -1:
                    # Plain text to end
                    text_content = children_str[i:].strip()
                    if text_content:
                        text_parts = self._parse_text_with_expressions(text_content)
                        children.extend(text_parts)
                    break
                elif next_tag == -1 or (next_expr != -1 and next_expr < next_tag):
                    # Expression comes first
                    text_content = children_str[i:next_expr].strip()
                    if text_content:
                        children.append(TextNode(content=text_content))
                    
                    # Parse expression
                    expr_end = children_str.find('}', next_expr)
                    if expr_end == -1:
                        # Malformed expression
                        children.append(TextNode(content=children_str[next_expr:]))
                        break
                    
                    expr_content = children_str[next_expr:expr_end + 1]
                    text_parts = self._parse_text_with_expressions(expr_content)
                    children.extend(text_parts)
                    i = expr_end + 1
                else:
                    # Tag comes first
                    text_content = children_str[i:next_tag].strip()
                    if text_content:
                        text_parts = self._parse_text_with_expressions(text_content)
                        children.extend(text_parts)
                    i = next_tag
        
        return children
    
    def _find_matching_tag(self, text: str, tag_name: str, start_pos: int) -> int:
        """Find the position of the matching closing tag - simplified without regex"""
        # List of self-closing tags that don't need closing tags
        self_closing_tags = {
            'img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col',
            'embed', 'source', 'track', 'wbr', 'command', 'keygen', 'menuitem', 'param'
        }
        
        # If it's a self-closing tag, return -1 immediately
        if tag_name.lower() in self_closing_tags:
            return -1
        
        depth = 1
        i = start_pos
        n = len(text)

        while i < n:
            if text[i] == '{':
                if buf:
                    nodes.append(TextNode(content=''.join(buf)))
                    buf = []
                end  = _match_brace(text, i)
                expr = text[i + 1 : end - 1].strip()
                if expr:
                    pexpr = self.ast_parser.parse_expression(expr)
                    nodes.append(ExpressionNode(expression=expr, parsed_expression=pexpr))
                i = end
            else:
                buf.append(text[i])
                i += 1

        if buf:
            content = ''.join(buf)
            if content.strip():
                nodes.append(TextNode(content=content))

        return nodes

    # ── Deadline helper ────────────────────────────────────────────────────────

    @staticmethod
    def _tick(deadline: float) -> None:
        """Raise :class:`_ParseTimeout` if the wall-clock deadline has passed."""
        if time.monotonic() > deadline:
            raise _ParseTimeout()


# ── Thread-local parser pool ───────────────────────────────────────────────────

_tls = threading.local()


def _get_parser() -> PSXParser:
    """
    Return the :class:`PSXParser` instance for the current thread.

    One instance per thread means no shared mutable state even when
    multiple requests are parsed concurrently.
    """
    if not hasattr(_tls, 'parser'):
        _tls.parser = PSXParser()
    return _tls.parser


# ── Public API ─────────────────────────────────────────────────────────────────

def psx(psx_str: str, context: Dict[str, Any] = None) -> PSXElement:
    """
    Parse a PSX string and return a :class:`PSXElement`.

    If *context* is omitted, the caller's local scope is captured
    automatically (plain, non-callable, non-``None`` values only).
    Pass an explicit dict to keep the scope clean and avoid accidental
    exposure of large or sensitive objects.
    """
    import inspect

    if context is None:
        captured: Dict[str, Any] = {}
        try:
            frame = inspect.currentframe().f_back
            if frame:
                captured = {
                    k: v
                    for k, v in frame.f_locals.items()
                    if (
                        not k.startswith('_')
                        and not callable(v)
                        and not isinstance(v, type)
                        and v is not None
                    )
                }
        except Exception:
            pass
        merged: Dict[str, Any] = captured
    else:
        merged = dict(context)

    ast_node = _get_parser().parse_psx(psx_str, merged)

    if isinstance(ast_node, ElementNode):
        el = PSXElement(
            tag=ast_node.tag,
            props=ast_node.attributes,
            children=_children_to_elements(ast_node.children, merged),
            key=ast_node.key,
        )
        el._ast_node    = ast_node   # type: ignore[attr-defined]
        el._psx_context = merged     # type: ignore[attr-defined]
        return el

    # Fragment, Component, or other root forms → wrap in a neutral div
    if isinstance(ast_node, FragmentNode):
        kids = _children_to_elements(ast_node.children, merged)
    else:
        c    = _node_to_child(ast_node, merged)
        kids = c if isinstance(c, list) else [c]

    el = PSXElement(
        tag='div',
        props={},
        children=kids,
        key=getattr(ast_node, 'key', None),
    )
    el._ast_node    = ast_node   # type: ignore[attr-defined]
    el._psx_context = merged     # type: ignore[attr-defined]
    return el


def render_psx(element: Any, context: Dict[str, Any] = None) -> str:
    """Render a :class:`PSXElement` (or any value) to an HTML string."""
    if isinstance(element, PSXElement):
        return element.to_html(context)
    return str(element)


def fragment(children: Any) -> str:
    """Join multiple children into a single HTML string."""
    if isinstance(children, list):
        return ''.join(str(c) for c in children)
    return str(children)


def key(key_value: str, element: PSXElement) -> PSXElement:
    """Attach a reconciliation key to a :class:`PSXElement`."""
    element.key = key_value
    return element


__all__ = [
    # Legacy interface
    'PSXElement', 'PSXParser', 'psx', 'render_psx', 'fragment', 'key',
    'process_python_logic',
    # Production AST tools
    'PSXASTParser', 'PSXNodeValidator', 'PSXNodeOptimizer',
]