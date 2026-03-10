"""
PSX Preprocessor - Regex-based PSX syntax transformer
Transforms PSX syntax into valid Python before AST parsing
"""

import re
from typing import Any, Dict, Optional


class PSXPreprocessor:
    """
    Preprocessor that transforms PSX syntax into valid Python code
    Uses regex to find and replace PSX patterns before Python parsing
    """
    
    def __init__(self):
        self.psx_function_name = "psx"
        # Pattern to match return statements with PSX
        self.return_psx_pattern = re.compile(
            r'return\s*\(\s*([^)]*(?:<[^>]*>[^<]*</[^>]*>[^)]*)*)\s*\)',
            re.DOTALL | re.MULTILINE
        )
        # Pattern to match PSX content
        self.psx_content_pattern = re.compile(
            r'<[^>]*>(?:[^<]|<(?!/?)[^>]*>)*</[^>]*>',
            re.DOTALL
        )
    
    def compile(self, source_code: str) -> str:
        """
        Transform PSX syntax into valid Python code
        """
        try:
            # Transform return statements with PSX
            transformed_code = self.return_psx_pattern.sub(
                self._replace_return_psx,
                source_code
            )
            
            return transformed_code
            
        except Exception as e:
            # If transformation fails, return original code
            print(f"PSX preprocessing warning: {e}")
            return source_code
    
    def _replace_return_psx(self, match) -> str:
        """
        Replace a return statement containing PSX with psx() call
        """
        psx_content = match.group(1).strip()
        
        # Clean up the PSX content - remove extra whitespace and newlines
        psx_content = self._clean_psx_content(psx_content)
        
        # Create the psx() call
        return f'return {self.psx_function_name}("""\n{psx_content}\n""")'
    
    def _clean_psx_content(self, content: str) -> str:
        """
        Clean up PSX content by normalizing whitespace and indentation
        """
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove leading indentation but keep structure
            stripped = line.strip()
            if stripped:
                cleaned_lines.append(stripped)
            else:
                cleaned_lines.append('')
        
        # Join with single spaces for compact PSX
        cleaned_content = ' '.join(filter(None, cleaned_lines))
        
        return cleaned_content


class PSXCompiler:
    """
    Main PSX compiler that uses preprocessing
    """
    
    def __init__(self):
        self.preprocessor = PSXPreprocessor()
    
    def compile(self, source_code: str) -> str:
        """
        Compile PSX syntax into valid Python code
        """
        return self.preprocessor.compile(source_code)
    
    def compile_file(self, file_path: str) -> str:
        """
        Compile a Python file containing PSX syntax
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        return self.compile(source_code)
    
    def is_psx_file(self, file_path: str) -> bool:
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
    return _compiler.compile_file(file_path)


def is_psx_file(file_path: str) -> bool:
    """
    Check if a file likely contains PSX syntax
    """
    return _compiler.is_psx_file(file_path)


# Test function
def _test_compiler():
    """Test the PSX compiler with example code"""
    
    # Example PSX code
    psx_code = '''def Home(props=None):
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

default = Home'''
    
    # Compile the code
    compiled = compile_psx(psx_code)
    
    print("=== PSX Compiler Test ===")
    print("Compiled code:")
    print(compiled)
    print("=== End Test ===")


if __name__ == "__main__":
    _test_compiler()
