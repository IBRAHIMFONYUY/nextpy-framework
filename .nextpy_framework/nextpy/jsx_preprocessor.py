"""
JSX Preprocessor - Transform Python files with JSX syntax to valid Python
Converts <div>...</div> to jsx('<div>...</div>') calls
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple


class JSXPreprocessor:
    """Preprocess Python files containing JSX syntax"""
    
    def __init__(self):
        # Pattern to match JSX elements
        self.jsx_pattern = re.compile(r'(<[^>]+>)', re.MULTILINE | re.DOTALL)
        self.return_pattern = re.compile(r'return\s*\(\s*(<.*?>)\s*\)', re.MULTILINE | re.DOTALL)
        self.simple_return_pattern = re.compile(r'return\s+(<.*?>)', re.MULTILINE | re.DOTALL)
        
    def find_jsx_blocks(self, content: str) -> List[Tuple[int, int, str]]:
        """Find all JSX blocks in the content"""
        jsx_blocks = []
        
        # Find return statements with JSX
        for match in self.return_pattern.finditer(content):
            start, end = match.span()
            jsx_content = match.group(1)
            jsx_blocks.append((start, end, jsx_content))
        
        # Find simple return statements
        for match in self.simple_return_pattern.finditer(content):
            start, end = match.span()
            jsx_content = match.group(1)
            jsx_blocks.append((start, end, jsx_content))
        
        return jsx_blocks
    
    def transform_jsx_to_function_call(self, jsx_str: str) -> str:
        """Transform JSX string to function call"""
        # Escape the JSX string for Python
        escaped_jsx = jsx_str.replace('"', '\\"').replace('\n', '\\n')
        return f'jsx("{escaped_jsx}")'
    
    def preprocess_content(self, content: str) -> str:
        """Preprocess content containing JSX"""
        # Add import statement if not present
        if 'from nextpy.true_jsx import jsx' not in content and 'import jsx' not in content:
            # Find the first import line or add at the top
            lines = content.split('\n')
            import_index = 0
            
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_index = i + 1
                elif line.strip() and not line.startswith('#'):
                    break
            
            lines.insert(import_index, 'from nextpy.true_jsx import jsx, render_jsx')
            content = '\n'.join(lines)
        
        # Transform JSX blocks
        jsx_blocks = self.find_jsx_blocks(content)
        
        # Process blocks in reverse order to maintain positions
        for start, end, jsx_content in reversed(jsx_blocks):
            # Replace JSX with function call
            function_call = self.transform_jsx_to_function_call(jsx_content)
            
            # Replace the original return statement
            original_return = content[start:end]
            new_return = original_return.replace(jsx_content, function_call)
            content = content[:start] + new_return + content[end:]
        
        return content
    
    def preprocess_file(self, file_path: Path) -> str:
        """Preprocess a Python file with JSX"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.preprocess_content(content)
    
    def preprocess_and_save(self, file_path: Path, output_path: Path = None):
        """Preprocess file and save result"""
        if output_path is None:
            output_path = file_path
        
        content = self.preprocess_file(file_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def is_jsx_file(self, file_path: Path) -> bool:
        """Check if file contains JSX syntax"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for JSX patterns
            return bool(self.return_pattern.search(content) or 
                       self.simple_return_pattern.search(content))
        except:
            return False


# Global preprocessor instance
preprocessor = JSXPreprocessor()


def preprocess_file(file_path: Path, output_path: Path = None) -> str:
    """Convenience function to preprocess a file"""
    return preprocessor.preprocess_and_save(file_path, output_path)


def preprocess_content(content: str) -> str:
    """Convenience function to preprocess content"""
    return preprocessor.preprocess_content(content)


def is_jsx_file(file_path: Path) -> bool:
    """Convenience function to check if file contains JSX"""
    return preprocessor.is_jsx_file(file_path)
