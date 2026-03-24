"""
Clean PSX Parser - Tokenizer + Stack Architecture
Avoids regex parsing, infinite loops, and handles nested tags correctly
"""

import re
from typing import Any, Dict, List, Union, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Token:
    """Represents a PSX token"""
    type: str  # "tag", "expr", "text"
    value: str
    position: int


class PSXTokenizer:
    """Fast PSX tokenizer - O(n) performance"""
    
    def __init__(self, src: str):
        self.src = src
        self.i = 0
        self.n = len(src)
    
    def next(self) -> Optional[Token]:
        """Get next token from source"""
        if self.i >= self.n:
            return None
        
        c = self.src[self.i]
        
        # Tag token
        if c == "<":
            j = self.src.find(">", self.i)
            if j == -1:
                # Unclosed tag, treat as text
                j = self.n
            token = self.src[self.i:j+1]
            self.i = j + 1
            return Token("tag", token, self.i)
        
        # Expression token
        elif c == "{":
            depth = 1
            j = self.i + 1
            
            while j < self.n and depth > 0:
                if self.src[j] == "{":
                    depth += 1
                elif self.src[j] == "}":
                    depth -= 1
                j += 1
            
            if depth > 0:
                # Unclosed expression, treat as text
                j = self.n
            
            token = self.src[self.i:j]
            self.i = j
            return Token("expr", token, self.i)
        
        # Text token
        else:
            j = self.i
            while j < self.n and self.src[j] not in "<{":
                j += 1
            
            token = self.src[self.i:j]
            self.i = j
            return Token("text", token, self.i)


class CleanPSXParser:
    """Clean PSX parser using tokenizer + stack"""
    
    def __init__(self):
        pass
    
    def parse(self, src: str, context: Dict[str, Any] = None) -> 'CleanPSXElement':
        """Parse PSX source to PSXElement tree with context capture"""
        context = context or {}
        
        # Pre-process React-style .map() syntax
        src = self._preprocess_map_syntax(src)
        
        tokenizer = PSXTokenizer(src)
        stack = []
        root = None
        
        while True:
            token = tokenizer.next()
            if not token:
                break
            
            if token.type == "tag":
                result = self._handle_tag_token(token, stack, context)
                if result:  # Got the root element
                    root = result
            elif token.type == "expr":
                self._handle_expr_token(token, stack, context)
            elif token.type == "text":
                self._handle_text_token(token, stack, context)
        
        # Get root element - either from closing tag or remaining in stack
        if not root and stack:
            root = stack[-1]
        
        return root or CleanPSXElement("div", {}, ["No content"], context)
    
    def _preprocess_map_syntax(self, src: str) -> str:
        """Convert React-style .map() to Python for loops"""
        # Simple regex to convert .map() patterns
        pattern = r'\{(\w+)\.map\((.*?)\)\}'
        
        def repl(match):
            iterable = match.group(1)
            lambda_func = match.group(2)
            # Extract the lambda body (simplified)
            if 'lambda' in lambda_func:
                # Extract variable name and body
                lambda_parts = lambda_func.split(':')
                if len(lambda_parts) >= 2:
                    var_name = lambda_parts[0].replace('lambda', '').strip()
                    body = ':'.join(lambda_parts[1:]).strip()
                    return f'{{for {var_name} in {iterable}: {body}}}'
            # Return original if no transformation
            return match.group(0)
        
        return re.sub(pattern, repl, src)
    
    def _handle_tag_token(self, token: Token, stack: List['CleanPSXElement'], context: Dict[str, Any]) -> 'CleanPSXElement':
        """Handle tag tokens with proper nesting"""
        value = token.value
        
        if value.startswith("</"):
            # Closing tag
            if stack:
                node = stack.pop()
                if stack:
                    stack[-1].children.append(node)
                else:
                    # This is the root element
                    return node
        elif value.startswith("<"):
            # Opening tag
            if value.endswith("/>") or value in ["<br>", "<hr>", "<img>", "<input>", "<meta>", "<link>"]:
                # Self-closing tag
                tag_name = value[1:-2].split()[0] if value.endswith("/>") else value[1:-1].split()[0]
                node = CleanPSXElement(tag_name, {}, [], context)
                if stack:
                    stack[-1].children.append(node)
                else:
                    stack.append(node)
            else:
                # Regular opening tag - parse props
                tag_content = value[1:-1]  # Remove < and >
                parts = tag_content.split()
                tag_name = parts[0] if parts else "div"
                props_str = " ".join(parts[1:]) if len(parts) > 1 else ""
                
                # Parse props robustly
                props = {}
                if props_str:
                    # Improved prop parsing - handle expressions, quotes, and boolean props
                    import re
                    # Match key={value}, key="value", key='value', or key (boolean)
                    prop_pattern = re.compile(
                        r'([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*\{([^}]+)\}|'
                        r'([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*"([^"]*)"|'
                        r'([a-zA-Z][a-zA-Z0-9-]*)\s*=\s*\'([^\']*)\'|'
                        r'([a-zA-Z][a-zA-Z0-9-]+)'
                    )
                    
                    for match in prop_pattern.finditer(props_str):
                        groups = match.groups()
                        if groups[0] and groups[1]:  # key={value}
                            props[groups[0]] = '{' + groups[1].strip() + '}'
                        elif groups[2] and groups[3]:  # key="value"
                            props[groups[2]] = groups[3]
                        elif groups[4] and groups[5]:  # key='value'
                            props[groups[4]] = groups[5]
                        elif groups[6]:  # key (boolean)
                            props[groups[6]] = True
                
                node = CleanPSXElement(tag_name, props, [], context)
                stack.append(node)
        
        return None
    
    def _handle_expr_token(self, token: Token, stack: List['CleanPSXElement'], context: Dict[str, Any]):
        """Handle expression tokens"""
        if stack:
            stack[-1].children.append(token.value)
    
    def _handle_text_token(self, token: Token, stack: List['CleanPSXElement'], context: Dict[str, Any]):
        """Handle text tokens"""
        text = token.value.strip()
        if text and stack:
            stack[-1].children.append(text)


# Import PSXElement from the existing parser
from .parser import PSXElement


# Use CleanPSXElement for better expression handling
class CleanPSXElement(PSXElement):
    """Enhanced PSXElement with clean expression evaluation and context merging"""
    
    def __init__(self, tag: str, props: Dict[str, Any], children: List[Any], parse_context: Dict[str, Any] = None):
        """Initialize with parse-time context"""
        super().__init__(tag, props, children)
        self.parse_context = parse_context or {}
    
    def to_html(self, render_context: Dict[str, Any] = None) -> str:
        """Convert to HTML with merged context (parse-time + render-time)"""
        
        # Merge parse-time and render-time contexts (render-time takes precedence)
        merged_context = self.parse_context.copy()
        if render_context:
            merged_context.update(render_context)
        
        # Build props string with merged context
        props_str = self._build_props_string(merged_context)
        
        # Build children string with merged context
        children_str = self._build_children_string(merged_context)
        
        # Handle self-closing tags
        self_closing_tags = {
            'img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col',
            'embed', 'source', 'track', 'wbr', 'command', 'keygen', 'menuitem', 'param'
        }
        
        if self.tag in self_closing_tags and not children_str:
            return f"<{self.tag}{props_str} />"
        
        # Generate initial HTML
        html = f"<{self.tag}{props_str}>{children_str}</{self.tag}>"
        
        # Post-process to handle any remaining conditional blocks
        if '{if ' in html or '{for ' in html:
            from .python_logic import process_python_logic
            html = process_python_logic(html, merged_context)
        
        return html
    
    def _build_props_string(self, context: Dict[str, Any]) -> str:
        """Build props string with expression evaluation"""
        props_list = []
        
        for key, value in self.props.items():
            if key in ['key', 'children']:
                continue
            
            attr_name = 'class' if key == 'className' else key
            
            if isinstance(value, bool) and value:
                props_list.append(attr_name)
            elif value is not None and value != "":
                if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
                    # Evaluate expression in props
                    try:
                        expr = value[1:-1].strip()
                        evaluated = self.evaluate_expression(expr, context)
                        props_list.append(f'{attr_name}="{evaluated}"')
                    except:
                        props_list.append(f'{attr_name}="{value}"')
                else:
                    props_list.append(f'{attr_name}="{value}"')
        
        return " " + " ".join(props_list) if props_list else ""
    
    def _build_children_string(self, context: Dict[str, Any]) -> str:
        """Build children string with expression evaluation"""
        children_parts = []
        
        # First, collect all string children to handle multi-line logic blocks properly
        string_children = []
        for child in self.children:
            if isinstance(child, PSXElement):
                # Process existing PSXElement and add to result
                if string_children:
                    # Process accumulated string children as one block
                    combined_text = ''.join(string_children)
                    if '{' in combined_text:
                        from .python_logic import process_python_logic
                        processed = process_python_logic(combined_text, context)
                        children_parts.append(processed)
                    else:
                        children_parts.append(combined_text)
                    string_children = []
                
                children_parts.append(child.to_html(context))
            elif isinstance(child, str):
                string_children.append(child)
            else:
                # Process non-string, non-PSXElement
                if string_children:
                    combined_text = ''.join(string_children)
                    if '{' in combined_text:
                        from .python_logic import process_python_logic
                        processed = process_python_logic(combined_text, context)
                        children_parts.append(processed)
                    else:
                        children_parts.append(combined_text)
                    string_children = []
                children_parts.append(str(child))
        
        # Process any remaining string children
        if string_children:
            combined_text = ''.join(string_children)
            if '{' in combined_text:
                from .python_logic import process_python_logic
                processed = process_python_logic(combined_text, context)
                children_parts.append(processed)
            else:
                children_parts.append(combined_text)
        
        return "".join(children_parts)
    
    def evaluate_expression(self, expr: str, context: Dict[str, Any]) -> str:
        """Evaluate a single expression safely"""
        try:
            expr = expr.strip("{} ")
            if expr.startswith('for ') or expr.startswith('if ') or expr.startswith('python:'):
                from .python_logic import process_python_logic
                return process_python_logic(f'{{{expr}}}', context)
            else:
                result = str(eval(expr, {"__builtins__": {}}, context))
                return result
        except Exception as e:
            return f'{{expr error: {expr}}}'
    
    def _evaluate_expressions_in_string(self, s: str, context: Dict[str, Any]) -> str:
        """Evaluate expressions in string - compatibility method"""
        import re
        
        def repl(match):
            expr = match.group(1).strip()
            return self.evaluate_expression(f'{{{expr}}}', context)
        
        # Use safer pattern that avoids nested brace recursion
        pattern = re.compile(r'\{([^{}]+)\}')
        return pattern.sub(repl, s)


# Global clean parser instance
_clean_parser = CleanPSXParser()


def parse_psx_clean(src: str, context: Dict[str, Any] = None) -> PSXElement:
    """Parse PSX using clean tokenizer + stack approach"""
    return _clean_parser.parse(src, context)


def create_clean_psx_element(tag: str, props: Dict[str, Any], children: List) -> CleanPSXElement:
    """Create a clean PSX element"""
    return CleanPSXElement(tag, props, children)
