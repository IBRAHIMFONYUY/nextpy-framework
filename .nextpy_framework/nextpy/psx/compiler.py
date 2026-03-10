"""
PSX Compiler - Python AST-based compiler for PSX syntax
Transforms PSX syntax into valid Python code before execution
"""

import ast
import re
from typing import Any, Dict, Optional


class PSXTransformer(ast.NodeTransformer):
    """
    AST Transformer that converts PSX syntax into valid Python
    Transforms return statements with PSX into psx() calls
    """
    
    def __init__(self):
        self.psx_function_name = "psx"
        self.in_psx_block = False
    
    def visit_Return(self, node: ast.Return) -> ast.Return:
        """Transform return statements containing PSX syntax"""
        if node.value is None:
            return node
        
        # Check if the return value contains PSX syntax
        if self._contains_psx(node.value):
            # Transform the PSX syntax
            new_value = self._transform_psx_node(node.value)
            if new_value:
                node.value = new_value
        
        return node
    
    def visit_Assign(self, node: ast.Assign) -> ast.Assign:
        """Transform assignments containing PSX syntax"""
        if node.value and self._contains_psx(node.value):
            new_value = self._transform_psx_node(node.value)
            if new_value:
                node.value = new_value
        
        return node
    
    def _contains_psx(self, node: ast.AST) -> bool:
        """Check if an AST node contains PSX syntax"""
        try:
            # Get the source representation
            if isinstance(node, ast.Tuple):
                # For tuples, check each element
                for elt in node.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        if "<" in elt.value and ">" in elt.value:
                            return True
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                return "<" in node.value and ">" in node.value
            return False
        except:
            return False
    
    def _transform_psx_node(self, node: ast.AST) -> Optional[ast.AST]:
        """Transform a PSX AST node into a psx() call"""
        try:
            # Get the source code of the node
            code = ast.unparse(node)
            
            # Handle different PSX patterns
            if self._is_psx_tuple(code):
                # Handle return (<div>...</div>)
                psx_code = self._extract_psx_from_tuple(code)
                return self._create_psx_call(psx_code)
            elif self._is_psx_direct(code):
                # Handle direct PSX without parentheses
                return self._create_psx_call(code.strip())
            
        except Exception as e:
            # If transformation fails, return original node
            pass
        
        return None
    
    def _is_psx_tuple(self, code: str) -> bool:
        """Check if code is a tuple containing PSX"""
        code = code.strip()
        return (
            code.startswith("(") and 
            code.endswith(")") and 
            "<" in code and 
            ">" in code
        )
    
    def _is_psx_direct(self, code: str) -> bool:
        """Check if code is direct PSX without tuple"""
        code = code.strip()
        return (
            code.startswith("<") and 
            code.endswith(">") and
            not code.startswith("(")
        )
    
    def _extract_psx_from_tuple(self, code: str) -> str:
        """Extract PSX code from tuple parentheses"""
        # Remove outer parentheses
        code = code.strip()
        if code.startswith("(") and code.endswith(")"):
            code = code[1:-1].strip()
        
        return code
    
    def _create_psx_call(self, psx_code: str) -> ast.Call:
        """Create an AST node for psx("""<code>""") call"""
        # Create the string argument
        string_arg = ast.Constant(value=psx_code.strip())
        
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
        
        Args:
            source_code: Python source code with PSX syntax
            
        Returns:
            Valid Python code with PSX transformed to psx() calls
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
            
        except SyntaxError as e:
            # If there's a syntax error, return original code
            # In production, you might want to raise an error or log this
            return source_code
        except Exception as e:
            # If transformation fails, return original code
            return source_code
    
    def compile_file(self, file_path: str) -> str:
        """
        Compile a Python file containing PSX syntax
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Compiled Python code
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        return self.compile(source_code)
    
    def is_psx_file(self, file_path: str) -> bool:
        """
        Check if a file likely contains PSX syntax
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            True if file likely contains PSX
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


# Global compiler instance
_compiler = PSXCompiler()


def compile_psx(source_code: str) -> str:
    """
    Compile PSX syntax into valid Python code
    
    Args:
        source_code: Python source code with PSX syntax
        
    Returns:
        Valid Python code with PSX transformed
    """
    return _compiler.compile(source_code)


def compile_psx_file(file_path: str) -> str:
    """
    Compile a Python file containing PSX syntax
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Compiled Python code
    """
    return _compiler.compile_file(file_path)


def is_psx_file(file_path: str) -> bool:
    """
    Check if a file likely contains PSX syntax
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        True if file likely contains PSX
    """
    return _compiler.is_psx_file(file_path)


# Example usage and testing
def _test_compiler():
    """Test the PSX compiler with example code"""
    
    # Example PSX code
    psx_code = '''
def Home(props=None):
    props = props or {}
    title = props.get("title", "Welcome to NextPy")
    message = props.get("message", "Your Python-powered web framework with PSX")
    
    return (
        <div class="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-500 to-purple-600">
            <div class="text-center text-white">
                <h1 class="mb-4 text-5xl font-bold">{title}</h1>
                <p class="text-xl">{message}</p>
                <a href="/about" class="inline-block px-6 py-3 mt-8 font-semibold text-blue-600 transition-all duration-300 transform bg-white rounded-lg shadow-lg hover:bg-gray-100 hover:text-blue-700 hover:scale-105">
                    Learn More
                </a>
            </div>
        </div>
    )

def getServerSideProps(context):
    return {
        "props": {
            "title": "Welcome to NextPy",
            "message": "Your Python-powered web framework with PSX"
        }
    }

default = Home
'''
    
    # Compile the code
    compiled = compile_psx(psx_code)
    
    print("=== PSX Compiler Test ===")
    print("Original code contains PSX syntax with <div> tags")
    print("Compiled code:")
    print(compiled)
    print("=== End Test ===")


if __name__ == "__main__":
    _test_compiler()
