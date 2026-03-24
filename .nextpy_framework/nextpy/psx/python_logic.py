"""
PSX Python Logic Engine - Revolutionary feature allowing real Python logic inside PSX
This makes PSX more powerful than React JSX!
"""

import re
import ast
from typing import Any, Dict, List, Union, Callable


class PSXPythonLogicEngine:
    """
    Engine that can execute real Python logic inside PSX expressions
    This is the revolutionary feature that makes PSX more powerful than React JSX!
    """
    
    def __init__(self):
        # Pattern to detect Python logic blocks in PSX
        self.python_logic_pattern = re.compile(r'\{python:(.*?)\}', re.DOTALL)
        # Pattern for Python expressions
        self.python_expr_pattern = re.compile(r'\{py:(.*?)\}', re.DOTALL)
        
        # Enhanced patterns to handle nested braces (multiple levels of nesting)
        # Uses recursive pattern matching for better nested brace handling
        self.python_loop_pattern = re.compile(
            r'\{for\s+([^:]+?)\s+in\s+([^:]+?):\s*((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}', 
            re.DOTALL
        )
        # Pattern for if without endif (simpler syntax) - handle both single and multi-line
        self.python_cond_simple_pattern = re.compile(
            r'\{if\s+([^:]+?):\s*\}((?:[^{}]|(?:(?!\{else:\}).)*?)*)\{else:\s*\}((?:[^{}]|(?:(?!\{endif\}).)*?)*)\{endif\}', 
            re.DOTALL
        )
        # Pattern for if-else without endif (single line) - NEW
        self.python_cond_else_single_pattern = re.compile(
            r'\{if\s+([^:]+?):\s*([^{}]+?)\s*\}\{else:\s*([^{}]+?)\}', 
            re.DOTALL
        )
        # Pattern for if-else without endif (multi-line)
        self.python_cond_else_pattern = re.compile(
            r'\{if\s+([^:]+?):\s*\}((?:[^{}]|(?:(?!\{else:\}).)*?)*)\{else:\s*\}((?:[^{}]|(?:(?!\{endif\}).)*?)*)\{endif\}', 
            re.DOTALL
        )
        # Pattern for if with endif (traditional syntax)
        self.python_cond_pattern = re.compile(
            r'\{if\s+([^:]+?):\s*\}((?:[^{}]|(?:(?!\{endif\}).)*?)*)\{endif\}', 
            re.DOTALL
        )
        # NEW: Pattern for simple if without endif (actual format used in test)
        self.python_cond_simple_no_endif = re.compile(
            r'\{if\s+([^:]+?):\s*\}((?:[^{}]|(?:(?!\}).)*?)*)\}', 
            re.DOTALL
        )
        # Pattern for Python try-catch with nested support
        self.python_try_pattern = re.compile(
            r'\{try:(.*?)\}\{except\s*([^:]*?):\s*\}((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\{endtry\}', 
            re.DOTALL
        )
        
    def safe_eval(self, expr: str, context: Dict[str, Any]) -> Any:
        """
        Safely evaluate expressions with dangerous attribute blocking
        """
        # Prevent access to dangerous private attributes and methods
        dangerous_patterns = [
            '__', 'eval', 'exec', 'compile', 'open', 'file', 'input', 
            'globals', 'locals', 'vars', 'dir', 'getattr', 'setattr', 'delattr',
            'hasattr', 'isinstance', 'issubclass', 'callable', '__import__',
            '__subclasses__', '__bases__', '__mro__', '__class__', '__dict__'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in expr:
                raise ValueError(f"Dangerous attribute access blocked: {pattern}")
        
        
        
        # Enhanced safe environment with more Python functions
        self.safe_globals = {
            '__builtins__': {
                # Built-in types and functions
                'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
                'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                'range': range, 'enumerate': enumerate, 'zip': zip,
                'map': map, 'filter': filter, 'sum': sum, 'max': max, 'min': min,
                'abs': abs, 'round': round, 'sorted': sorted, 'reversed': reversed,
                'any': any, 'all': all,
                # String and object methods
                'getattr': getattr, 'hasattr': hasattr, 'setattr': setattr,
                'delattr': delattr, 'isinstance': isinstance, 'type': type,
                # Math functions
                'pow': pow, 'divmod': divmod,
            }
        }

        return eval(expr, self.safe_globals, context)
    
    def execute_python_logic(self, logic_code: str, context: Dict[str, Any]) -> str:
        """
        Execute real Python code and return the result
        If the code defines a 'result' variable, that's returned.
        Otherwise, if it's a single expression, its value is returned.
        """
        try:
            # Add context variables
            safe_locals = context.copy()
            
            # If it's a single line and looks like an expression, try eval first
            if '\n' not in logic_code.strip() and '=' not in logic_code:
                try:
                    return str(eval(logic_code, self.safe_globals, safe_locals))
                except:
                    pass  # Fall back to exec
            
            # Execute the code
            exec(logic_code, self.safe_globals, safe_locals)
            
            # Return the result if defined
            if 'result' in safe_locals:
                return str(safe_locals['result'])
            
            # If it's an assignment, return the assigned value
            if '=' in logic_code:
                var_name = logic_code.split('=')[0].strip()
                if var_name in safe_locals:
                    return str(safe_locals[var_name])
            
            return ''
        except Exception as e:
            return f'{{python error: {str(e)[:100]}}}'
    
    def process_for_loop(self, loop_expr: str, context: Dict[str, Any]) -> str:
        """
        Enhanced for loop processing with support for multiple assignment variables
        Examples:
        - {for item in items: ...}
        - {for i, item in enumerate(items): ...}
        - {for key, value in dict.items(): ...}
        """
        try:
            match = self.python_loop_pattern.match(loop_expr)
            if not match:
                return loop_expr
            
            vars_part, iterable_part, template_part = match.groups()
            
            # Parse variables (support multiple assignment)
            vars_list = [v.strip() for v in vars_part.split(',')]
            
            # Evaluate the iterable
            safe_locals = context.copy()
            iterable = self.safe_eval(iterable_part, safe_locals)
            
            # Generate output for each item
            result_parts = []
            for item in iterable:
                # Handle multiple assignment
                if len(vars_list) == 1:
                    # Single variable assignment
                    safe_locals[vars_list[0]] = item
                else:
                    # Multiple variable assignment (e.g., enumerate, dict.items())
                    if hasattr(item, '__iter__') and not isinstance(item, str):
                        item_parts = list(item)
                        if len(item_parts) == len(vars_list):
                            for i, var_name in enumerate(vars_list):
                                safe_locals[var_name] = item_parts[i]
                        else:
                            # Fallback: assign the whole item to the first variable
                            safe_locals[vars_list[0]] = item
                    else:
                        # Fallback: assign the whole item to the first variable
                        safe_locals[vars_list[0]] = item
                
                # Process the template part with the new context
                processed_template = self._process_template(template_part, safe_locals)
                result_parts.append(processed_template)
            
            return ''.join(result_parts)
        except Exception as e:
            return f'{{for loop error: {str(e)[:100]}}}'
    
    def _process_template(self, template: str, context: Dict[str, Any]) -> str:
        """Process template string with nested expressions"""
        # Process nested expressions recursively
        import re
        
        # Find all expressions in the template
        expr_pattern = re.compile(r'\{([^{}]+)\}')
        
        def replace_expr(match):
            expr = match.group(1).strip()
            if expr.startswith('for ') or expr.startswith('if ') or expr.startswith('python:'):
                # Handle nested logic blocks
                return self.process_python_logic(f'{{{expr}}}', context)
            else:
                # Handle simple expressions
                try:
                    return str(self.safe_eval(expr, context))
                except:
                    return match.group(0)
        
        return expr_pattern.sub(replace_expr, template)
    
    def process_python_loops(self, loop_code: str, context: Dict[str, Any]) -> str:
        """
        Process Python for loops inside PSX
        Example: {for i, user in enumerate(users):<UserCard name={user.name} index={i} />}
        """
        try:
            match = self.python_loop_pattern.search(loop_code)
            if not match:
                return loop_code
            
            loop_vars = match.group(1).strip()
            iterable_expr = match.group(2).strip()
            template_code = match.group(3).strip()
            
            # Evaluate the iterable expression
            safe_globals = {
                '__builtins__': {
                    'enumerate': enumerate, 'zip': zip, 'range': range, 'len': len,
                    'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                    'map': map, 'filter': filter, 'sum': sum, 'max': max, 'min': min,
                }
            }
            safe_locals = context.copy()
            
            iterable = self.safe_eval(iterable_expr, safe_locals)
            result_parts = []
            
            # We need to execute the loop dynamically to handle any number of loop variables
            # We'll use a small exec block to do the heavy lifting
            for item in iterable:
                loop_context = context.copy()
                
                # Assign loop variables
                if "," in loop_vars:
                    # Multi-variable assignment: for i, x in ...
                    vars_list = [v.strip() for v in loop_vars.split(",")]
                    for i, v in enumerate(vars_list):
                        loop_context[v] = item[i]
                else:
                    # Single variable assignment: for x in ...
                    loop_context[loop_vars] = item
                
                # Process the template with current item
                processed = self._process_template(template_code, loop_context)
                result_parts.append(processed)
            
            return ''.join(result_parts)
            
        except Exception as e:
            return f"<!-- Loop Error: {str(e)} -->"
    
    def process_python_conditionals(self, cond_code: str, context: Dict[str, Any]) -> str:
        """
        Process Python if statements inside PSX
        Supports both {if condition: content} and {if condition: content}{else: content} syntax
        Handles both single-line and multi-line formats
        """
        try:
            # Handle if-else single line pattern first (most specific)
            match = self.python_cond_else_single_pattern.search(cond_code)
            
            if match:
                condition = match.group(1).strip()
                true_content = match.group(2).strip()
                false_content = match.group(3).strip()
                
                # Evaluate condition using enhanced safe environment
                condition_result = self.safe_eval(condition, context)
                
                if condition_result:
                    return self._process_template(true_content, context)
                else:
                    return self._process_template(false_content, context)
            
            # Handle if-else multi-line pattern
            match = self.python_cond_else_pattern.search(cond_code)
            
            if match:
                condition = match.group(1).strip()
                true_content = match.group(2).strip()
                false_content = match.group(3).strip()
                
                # Evaluate condition using enhanced safe environment
                condition_result = self.safe_eval(condition, context)
                
                if condition_result:
                    return self._process_template(true_content, context)
                else:
                    return self._process_template(false_content, context)
            
            # Handle simple if pattern (without endif) - both single and multi-line
            match = self.python_cond_simple_pattern.search(cond_code)
            if match:
                condition = match.group(1).strip()
                content = match.group(2).strip()
                
                # Evaluate condition using enhanced safe environment
                condition_result = self.safe_eval(condition, context)
                
                if condition_result:
                    return self._process_template(content, context)
                else:
                    return ''
            
            # Handle traditional if pattern (with endif)
            match = self.python_cond_pattern.search(cond_code)
            if match:
                condition = match.group(1).strip()
                content = match.group(2).strip()
                
                # Evaluate condition using enhanced safe environment
                condition_result = self.safe_eval(condition, context)
                
                if condition_result:
                    return self._process_template(content, context)
                else:
                    return ''
                
        except Exception as e:
            return f"<!-- Conditional Error: {str(e)} -->"
    
    def process_python_try_catch(self, try_code: str, context: Dict[str, Any]) -> str:
        """
        Process Python try-catch blocks inside PSX
        Example: {try:risky_operation()}{except:handle_error()}<Error />}
        """
        try:
            match = self.python_try_pattern.search(try_code)
            if not match:
                return try_code
            
            try_block = match.group(1).strip()
            except_var = match.group(2).strip()
            except_content = match.group(3).strip()
            
            # Try to execute the try block using enhanced safe environment
            try:
                result = self.safe_eval(try_block, context)
                return str(result) if result else ''
                
            except Exception as e:
                # Handle the exception
                error_context = context.copy()
                error_context[except_var] = e
                return self._process_template(except_content, error_context)
                
        except Exception as e:
            return f"<!-- Try-Catch Error: {str(e)} -->"
    
    def _process_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Process a template string with context variables using enhanced safe environment
        """
        # Replace simple variable references
        def replace_var(match):
            var_name = match.group(1)
            return str(context.get(var_name, f"{{var {var_name}}}"))
        
        # Replace {variable} patterns (simple variables only)
        template = re.sub(r'\{(\w+)\}', replace_var, template)
        
        # Replace {expression} patterns (complex expressions)
        def replace_expr(match):
            expr = match.group(1)
            try:
                # Use the enhanced safe environment
                result = self.safe_eval(expr, context)
                return str(result)
            except Exception as e:
                return f"{{expr error: {expr}}}"
        
        # Use a more specific pattern to avoid replacing already processed variables
        template = re.sub(r'\{([^{}\s][^{}]*)\}', replace_expr, template)
        
        return template
    
    def process_python_logic_in_psx(self, psx_content: str, context: Dict[str, Any]) -> str:
        """
        Main method to process all Python logic in PSX content
        This is the revolutionary feature!
        """
        result = psx_content
        
        # Process Python logic blocks
        result = self.python_logic_pattern.sub(
            lambda m: self.execute_python_logic(m.group(1), context),
            result
        )
        
        # Process Python loops (using enhanced method)
        result = self.python_loop_pattern.sub(
            lambda m: self.process_for_loop(m.group(0), context),
            result
        )
        
        # Process Python conditionals
        result = self.python_cond_pattern.sub(
            lambda m: self.process_python_conditionals(m.group(0), context),
            result
        )
        
        # Process Python try-catch
        result = self.python_try_pattern.sub(
            lambda m: self.process_python_try_catch(m.group(0), context),
            result
        )
        
        # Process Python expressions
        result = self.python_expr_pattern.sub(
            lambda m: str(self.safe_eval(m.group(1), context)),
            result
        )
        
        return result


# Global Python Logic Engine
_python_logic_engine = PSXPythonLogicEngine()


def process_python_logic(psx_content: str, context: Dict[str, Any]) -> str:
    """
    Process Python logic in PSX content
    """
    return _python_logic_engine.process_python_logic_in_psx(psx_content, context)


# Revolutionary PSX Features
def psx_for_loop(iterable: List[Any], template_func: Callable) -> str:
    """
    Revolutionary for loop directly in PSX
    Usage: {for user in users:<UserCard name={user.name} />}
    """
    result_parts = []
    for item in iterable:
        result_parts.append(str(template_func(item)))
    return ''.join(result_parts)


def psx_if_condition(condition: bool, true_content: Any, false_content: Any = None) -> Any:
    """
    Revolutionary if condition directly in PSX
    Usage: {if user.is_admin:<AdminPanel />}
    """
    return true_content if condition else false_content


def psx_try_catch(try_func: Callable, except_func: Callable) -> Any:
    """
    Revolutionary try-catch directly in PSX
    Usage: {try:risky_operation()}{except:error:<Error />}
    """
    try:
        return try_func()
    except Exception as e:
        return except_func(e)


# PSX Template Engine for advanced features
class PSXTemplateEngine:
    """
    Advanced template engine for PSX with full Python support
    """
    
    @staticmethod
    def render_template(template_str: str, context: Dict[str, Any]) -> str:
        """Render template with Python logic"""
        return process_python_logic(template_str, context)
    
    @staticmethod
    def create_component(template_str: str) -> Callable:
        """Create a component from template string"""
        def component_func(**props):
            context = props.copy()
            return process_python_logic(template_str, context)
        return component_func


# Export all revolutionary features
__all__ = [
    'PSXPythonLogicEngine', 'process_python_logic',
    'psx_for_loop', 'psx_if_condition', 'psx_try_catch',
    'PSXTemplateEngine'
]
