"""
PSX Parser - Production-grade parser with AST integration
Supports full PSX capability with modern architecture
"""

import re
import json
from typing import Any, Dict, List, Union, Optional, Tuple
from dataclasses import dataclass, field
from .ast_nodes import (
    PSXNode, PSXNodeUnion, NodeType, LogicType,
    ElementNode, TextNode, ExpressionNode, LogicNode,
    IfNode, ForNode, WhileNode, TryNode,
    ComponentNode, FragmentNode,
    PSXASTParser, PSXNodeValidator, PSXNodeOptimizer
)
from .runtime import PSXRuntime, process_python_logic


@dataclass
class PSXElement:
    """Legacy PSX element - maintained for backwards compatibility"""
    tag: str
    props: Dict[str, Any] = field(default_factory=dict)
    children: List[Union[str, 'PSXElement']] = field(default_factory=list)
    key: Optional[str] = None
    
    def to_ast(self) -> ElementNode:
        """Convert legacy PSXElement to production-grade AST"""
        # Separate events from props
        events = {}
        attributes = {}
        
        for key, value in self.props.items():
            if key.startswith('on') and callable(value):
                events[key] = value.__name__
            else:
                attributes[key] = value
        
        # Convert children
        ast_children = []
        for child in self.children:
            if isinstance(child, str):
                ast_children.append(TextNode(content=child))
            elif isinstance(child, PSXElement):
                ast_children.append(child.to_ast())
        
        return ElementNode(
            tag=self.tag,
            attributes=attributes,
            events=events,
            children=ast_children,
            key=self.key,
            self_closing=self.tag in {
                'img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col',
                'embed', 'source', 'track', 'wbr', 'command', 'keygen', 'menuitem', 'param'
            }
        )
    
    def to_html(self, context: Dict[str, Any] = None) -> str:
        """Convert PSX element to HTML string"""
        context = context or {}
        runtime = PSXRuntime(context)
        
        # Convert to AST and render
        ast_node = self.to_ast()
        return runtime._render_node(ast_node)


class PSXParser:
    """Production-grade PSX parser with AST integration"""
    
    def __init__(self):
        self.ast_parser = PSXASTParser()
        self.validator = PSXNodeValidator()
        self.optimizer = PSXNodeOptimizer()
        self.runtime = PSXRuntime()
        
        # Regex patterns for parsing
        self.psx_pattern = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)\s*([^>]*)>(.*?)</\1>', re.DOTALL)
        self.self_closing_pattern = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)\s*([^>]*)\s*/>', re.DOTALL)
        self.prop_pattern = re.compile(
            r'([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*\{([^}]+)\}|'
            r'([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*"([^"]*)"|'
            r'([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*\'([^\']*)\'|'
            r'([a-zA-Z][a-zA-Z0-9-]+)|'
            r'(\.\.\.\w+)'  # Spread props
        )
    
    def parse_psx(self, psx_str: str, context: Dict[str, Any] = None) -> PSXNodeUnion:
        """Parse PSX string to production-grade AST node"""
        context = context or {}
        
        # Process Python logic first
        psx_str = process_python_logic(psx_str, context)
        
        # Try to parse as element
        ast_node = self._parse_element(psx_str, context)
        if ast_node:
            return self.optimizer.optimize_node(ast_node)
        
        # Try to parse as component
        ast_node = self._parse_component(psx_str, context)
        if ast_node:
            return self.optimizer.optimize_node(ast_node)
        
        # Try to parse as fragment
        ast_node = self._parse_fragment(psx_str, context)
        if ast_node:
            return self.optimizer.optimize_node(ast_node)
        
        # Default to text node
        return TextNode(content=psx_str)
    
    def _parse_element(self, psx_str: str, context: Dict[str, Any]) -> Optional[ElementNode]:
        """Parse PSX string to ElementNode"""
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
        
        # Check for regular tags
        tag_match = self.psx_pattern.match(psx_str)
        if tag_match:
            tag = tag_match.group(1)
            props_str = tag_match.group(2).strip()
            children_str = tag_match.group(3)
            
            props = self._parse_props(props_str, context)
            children = self._parse_children(children_str, context)
            
            return ElementNode(
                tag=tag,
                attributes=props['attributes'],
                events=props['events'],
                children=children,
                spread_props=props['spread_props']
            )
        
        return None
    
    def _parse_component(self, psx_str: str, context: Dict[str, Any]) -> Optional[ComponentNode]:
        """Parse PSX string to ComponentNode"""
        # Component pattern (uppercase first letter)
        component_pattern = re.compile(r'<([A-Z][a-zA-Z0-9]*)\s*([^>]*)>(.*?)</\1>', re.DOTALL)
        
        match = component_pattern.match(psx_str)
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
        
        return None
    
    def _parse_fragment(self, psx_str: str, context: Dict[str, Any]) -> Optional[FragmentNode]:
        """Parse PSX string to FragmentNode"""
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
        
        # Split by PSX tags and text
        parts = re.split(r'(<[^>]+>)', children_str)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Try to parse as PSX element/component
            ast_node = self.parse_psx(part, context)
            if ast_node and not isinstance(ast_node, TextNode):
                children.append(ast_node)
            else:
                # Handle expressions in text
                if '{' in part and '}' in part:
                    # Parse expressions
                    text_parts = self._parse_text_with_expressions(part)
                    children.extend(text_parts)
                else:
                    children.append(TextNode(content=part))
        
        return children
    
    def _parse_text_with_expressions(self, text: str) -> List[PSXNodeUnion]:
        """Parse text containing expressions"""
        nodes = []
        
        # Split by expressions
        parts = re.split(r'(\{[^}]+\})', text)
        
        for part in parts:
            if part.startswith('{') and part.endswith('}'):
                # Expression
                expr = part[1:-1].strip()
                parsed_ast = self.ast_parser.parse_expression(expr)
                nodes.append(ExpressionNode(
                    expression=expr,
                    parsed_expression=parsed_ast
                ))
            elif part:
                # Text
                nodes.append(TextNode(content=part))
        
        return nodes


# Global parser instance
_parser = PSXParser()


def psx(psx_str: str, context: Dict[str, Any] = None) -> PSXElement:
    """
    Parse PSX string to PSXElement (legacy interface)
    Automatically captures local variables for expression evaluation
    """
    import inspect
    
    # Capture variables from caller's frame
    captured_locals = {}
    try:
        frame = inspect.currentframe().f_back
        if frame:
            # Filter out internal variables
            frame_locals = frame.f_locals
            captured_locals = {
                k: v for k, v in frame_locals.items()
                if not k.startswith('_') and 
                   not callable(v) and
                   not hasattr(v, '__call__')
            }
    except Exception:
        pass
    
    # Merge provided context with captured locals
    merged_context = captured_locals.copy()
    if context:
        merged_context.update(context)
    
    # Parse with production-grade parser
    ast_node = _parser.parse_psx(psx_str, merged_context)
    
    # Convert to legacy PSXElement for backwards compatibility
    if isinstance(ast_node, ElementNode):
        return PSXElement(
            tag=ast_node.tag,
            props=ast_node.attributes,
            children=[],
            key=ast_node.key
        )
    else:
        # For non-elements, wrap in div
        return PSXElement(
            tag='div',
            props={},
            children=[str(ast_node)]
        )


def render_psx(element, context: Dict[str, Any] = None) -> str:
    """Render PSX element to HTML string"""
    if isinstance(element, PSXElement):
        return element.to_html(context)
    elif isinstance(element, str):
        return element
    else:
        return str(element)


# Legacy exports
def fragment(children: Any) -> str:
    """Fragment component for multiple children"""
    if isinstance(children, list):
        return ''.join(str(child) for child in children)
    else:
        return str(children)


def key(key_value: str, element: PSXElement) -> PSXElement:
    """Add key to PSX element"""
    element.key = key_value
    return element


# Export all PSX components
__all__ = [
    # Legacy interface
    'PSXElement', 'PSXParser', 'psx', 'render_psx', 
    'fragment', 'key', 'process_python_logic',
    
    # Production-grade interface
    'PSXASTParser', 'PSXNodeValidator', 'PSXNodeOptimizer'
]
