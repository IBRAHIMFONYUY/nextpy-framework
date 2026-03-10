"""
PSX Compiler - Simple and direct AST-based compiler for PSX syntax
"""

import ast
import re
from typing import Any, Dict, Optional


class PSXTransformer(ast.NodeTransformer):
    """
    AST Transformer that converts PSX syntax into valid Python
    """
    
    def __init__(self):
        self.psx_function_name = "psx"
    
    def visit_Return(self, node: ast.Return) -> ast.Return:
        """Transform return statements containing PSX syntax"""
        if node.value is None:
            return node
        
        # Check if this is a tuple with PSX content
        if isinstance(node.value, ast.Tuple):
            psx_content = self._extract_psx_from_tuple(node.value)
            if psx_content:
                # Create psx() call
                node.value = self._create_psx_call(psx_content)
        
        return node
    
    def _extract_psx_from_tuple(self, tuple_node: ast.Tuple) -> Optional[str]:
        """Extract PSX content from a tuple node"""
        try:
            # Reconstruct the tuple content as a string
            content_parts = []
            
            for elt in tuple_node.elts:
                if isinstance(elt, ast.Constant):
                    content_parts.append(str(elt.value))
                else:
                    # For non-constant elements, try to unparse them
                    try:
                        content_parts.append(ast.unparse(elt))
                    except:
                        continue
            
            content = "".join(content_parts)
            
            # Check if this looks like PSX
            if "<" in content and ">" in content:
                return content.strip()
                
        except Exception:
            pass
        
        return None
    
    def _create_psx_call(self, psx_code: str) -> ast.Call:
        """Create an AST node for psx("""<code>""") call"""
        # Create the string argument
        string_arg = ast.Constant(value=psx_code)
        
        # Create the psx() function call
        psx_call = ast.Call(
            func=ast.Name(id=self.psx_function_name, ctx=ast.Load()),
            args=[string_arg],
            keywords=[]
        )
        
        return psx_call


class PSXCompiler:
    """
    Main PSX compiler that transforms PSX syntax into valid Python
    """
    
    def __init__(self):
        self.transformer = PSXTransformer()
    
    def compile(self, source_code: str) -> str:
        """
        Compile PSX syntax into valid Python code
        """
        try:
            # Parse the source code into AST
            tree = ast.parse(source_code)
            
            # Transform the AST
            transformed_tree = self.transformer.visit(tree)
            
            # Fix missing locations
            ast.fix_missing_locations(transformed_tree)
            
            # Convert back to source code
            compiled_code = ast.unparse(transformed_tree)
            
            return compiled_code
            
        except Exception as e:
            # If transformation fails, return original code
            print(f"PSX compilation warning: {e}")
            return source_code


# Global compiler instance
_compiler = PSXCompiler()


def compile_psx(source_code: str) -> str:
    """
    Compile PSX syntax into valid Python code
    """
    return _compiler.compile(source_code)


def compile_psx_file(file_path: str) -> str:
    """
    Compile a Python file containing PSX syntax
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    return _compiler.compile(source_code)


def is_psx_file(file_path: str) -> bool:
    """
    Check if a file likely contains PSX syntax
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Quick check for PSX patterns
        return (
            "<" in content and 
            ">" in content and
            ("return (" in content or "return(" in content)
        )
    except:
        return False
