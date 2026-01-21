"""
NextPy JSX Preprocessor - Transform Python files with JSX syntax to valid Python
Converts <div>...</div> to jsx('<div>...</div>') calls
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from .plugins import plugin_manager, PluginContext
    PLUGINS_AVAILABLE = True
except ImportError:
    PLUGINS_AVAILABLE = False
    plugin_manager = None


class JSXSyntaxError(Exception):
    """Custom exception for JSX syntax errors"""
    
    def __init__(self, message: str, line_number: int = None, column: int = None, file_path: str = None):
        self.message = message
        self.line_number = line_number
        self.column = column
        self.file_path = file_path
        
        # Build detailed error message
        error_parts = ["JSX Syntax Error"]
        if file_path:
            error_parts.append(f"in file '{file_path}'")
        if line_number is not None:
            error_parts.append(f"at line {line_number}")
            if column is not None:
                error_parts.append(f"column {column}")
        
        error_parts.append(f": {message}")
        super().__init__(" ".join(error_parts))


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
    
    def preprocess_content(self, content: str, file_path: str = None) -> str:
        """Preprocess content containing JSX with enhanced error handling and plugin support"""
        try:
            # Validate basic JSX structure
            self._validate_jsx_structure(content, file_path)
            
            # Apply plugins if available
            if PLUGINS_AVAILABLE and plugin_manager:
                plugin_context = PluginContext(
                    file_path=Path(file_path) if file_path else Path("unknown"),
                    file_content=content,
                    metadata={},
                    config={},
                    debug=False
                )
                
                plugin_result = plugin_manager.transform_content(plugin_context)
                
                if not plugin_result.success:
                    # Log plugin errors but continue processing
                    for error in plugin_result.errors:
                        print(f"Plugin error: {error}")
                
                content = plugin_result.content
                
                # Log warnings
                for warning in plugin_result.warnings:
                    print(f"Plugin warning: {warning}")
            
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
                try:
                    # Validate individual JSX block
                    self._validate_jsx_block(jsx_content, content, start, file_path)
                    
                    # Replace JSX with function call
                    function_call = self.transform_jsx_to_function_call(jsx_content)
                    
                    # Replace the original return statement
                    original_return = content[start:end]
                    new_return = original_return.replace(jsx_content, function_call)
                    content = content[:start] + new_return + content[end:]
                except Exception as e:
                    line_num = self._get_line_number(content, start)
                    raise JSXSyntaxError(
                        f"Error processing JSX block: {str(e)}",
                        line_number=line_num,
                        file_path=file_path
                    )
            
            return content
            
        except JSXSyntaxError:
            # Re-raise JSX syntax errors as-is
            raise
        except Exception as e:
            # Wrap other exceptions
            raise JSXSyntaxError(
                f"Unexpected error during JSX preprocessing: {str(e)}",
                file_path=file_path
            )
    
    def preprocess_file(self, file_path: Path) -> str:
        """Preprocess a Python file with JSX"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise JSXSyntaxError(
                f"File not found: {file_path}",
                file_path=str(file_path)
            )
        except UnicodeDecodeError as e:
            raise JSXSyntaxError(
                f"Unable to read file (encoding error): {str(e)}",
                file_path=str(file_path)
            )
        except Exception as e:
            raise JSXSyntaxError(
                f"Error reading file: {str(e)}",
                file_path=str(file_path)
            )
        
        return self.preprocess_content(content, str(file_path))
    
    def preprocess_and_save(self, file_path: Path, output_path: Path = None):
        """Preprocess file and save result with error handling"""
        if output_path is None:
            output_path = file_path
        
        try:
            content = self.preprocess_file(file_path)
            
            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except JSXSyntaxError:
            # Re-raise JSX syntax errors as-is
            raise
        except Exception as e:
            raise JSXSyntaxError(
                f"Error saving processed file: {str(e)}",
                file_path=str(file_path)
            )
    
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
    
    def _validate_jsx_structure(self, content: str, file_path: str = None):
        """Validate basic JSX structure in content"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_num = i + 1
            stripped = line.strip()
            
            # Check for unclosed tags
            if '<' in stripped and '>' not in stripped:
                # Might be a multi-line JSX, check if it's properly closed later
                continue
            
            # Check for malformed JSX tags
            if '<' in stripped:
                # Count opening and closing tags
                open_tags = len(re.findall(r'<[^/][^>]*>', stripped))
                close_tags = len(re.findall(r'</[^>]*>', stripped))
                self_closing = len(re.findall(r'<[^>]*/>', stripped))
                
                if open_tags > close_tags + self_closing:
                    raise JSXSyntaxError(
                        f"Unclosed JSX tag detected",
                        line_number=line_num,
                        file_path=file_path
                    )
    
    def _validate_jsx_block(self, jsx_content: str, full_content: str, position: int, file_path: str = None):
        """Validate individual JSX block for syntax errors"""
        # Remove surrounding whitespace
        jsx_content = jsx_content.strip()
        
        if not jsx_content.startswith('<') or not jsx_content.endswith('>'):
            raise JSXSyntaxError(
                f"Invalid JSX block: must start with '<' and end with '>'",
                file_path=file_path
            )
        
        # Check for basic tag structure
        if not re.match(r'^<[^>]+>$', jsx_content):
            # More complex JSX, check for nested structure
            stack = []
            i = 0
            while i < len(jsx_content):
                if jsx_content[i] == '<':
                    if i + 1 < len(jsx_content) and jsx_content[i + 1] == '/':
                        # Closing tag
                        if not stack:
                            raise JSXSyntaxError(
                                f"Unexpected closing tag",
                                file_path=file_path
                            )
                        stack.pop()
                        i += 1
                    elif i + 1 < len(jsx_content) and jsx_content[i + 1] == '!':
                        # Comment or DOCTYPE, skip to next '>'
                        i = jsx_content.find('>', i)
                        if i == -1:
                            raise JSXSyntaxError(
                                f"Unclosed comment/DOCTYPE",
                                file_path=file_path
                            )
                    else:
                        # Opening tag
                        tag_end = jsx_content.find('>', i)
                        if tag_end == -1:
                            raise JSXSyntaxError(
                                f"Unclosed opening tag",
                                file_path=file_path
                            )
                        
                        tag_content = jsx_content[i + 1:tag_end]
                        if not tag_content.endswith('/'):
                            # Not self-closing, add to stack
                            tag_name = re.match(r'^\w+', tag_content)
                            if tag_name:
                                stack.append(tag_name.group(0))
                    i = tag_end + 1
                else:
                    i += 1
            
            if stack:
                raise JSXSyntaxError(
                    f"Unclosed tag(s): {', '.join(stack)}",
                    file_path=file_path
                )
    
    def _get_line_number(self, content: str, position: int) -> int:
        """Get line number for a given position in content"""
        lines_before = content[:position].count('\n')
        return lines_before + 1


# Global preprocessor instance
preprocessor = JSXPreprocessor()


def preprocess_file(file_path: Path, output_path: Path = None) -> str:
    """Convenience function to preprocess a file"""
    return preprocessor.preprocess_and_save(file_path, output_path)


def preprocess_content(content: str, file_path: str = None) -> str:
    """Convenience function to preprocess content with error handling"""
    try:
        return preprocessor.preprocess_content(content, file_path)
    except JSXSyntaxError:
        raise
    except Exception as e:
        raise JSXSyntaxError(
            f"JSX preprocessing failed: {str(e)}",
            file_path=file_path
        )


def is_jsx_file(file_path: Path) -> bool:
    """Convenience function to check if file contains JSX"""
    return preprocessor.is_jsx_file(file_path)
