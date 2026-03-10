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
        # Pattern for Python loops
        self.python_loop_pattern = re.compile(r'\{for\s+(\w+)\s+in\s+(\w+):(.*?)\}', re.DOTALL)
        # Pattern for Python conditionals
        self.python_cond_pattern = re.compile(r'\{if\s+(.*?):\s*\}(.*?)\{endif\}', re.DOTALL)
        # Pattern for Python try-catch
        self.python_try_pattern = re.compile(r'\{try:(.*?)\}\{except:(.*?)\}(.*?)\{endtry\}', re.DOTALL)
    
    def execute_python_logic(self, logic_code: str, context: Dict[str, Any]) -> str:
        """
        Execute real Python code and return the HTML result
        This is the revolutionary part!
        """
        try:
            # Create a safe execution environment
            safe_globals = {
                '__builtins__': {
                    'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
                    'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                    'range': range, 'enumerate': enumerate, 'zip': zip,
                    'map': map, 'filter': filter, 'sum': sum, 'max': max, 'min': min,
                    'abs': abs, 'round': round, 'sorted': sorted, 'reversed': reversed,
                    'any': any, 'all': all,
                }
            }
            
            # Add context variables
            safe_locals = context.copy()
            
            # Execute the Python code
            exec(logic_code, safe_globals, safe_locals)
            
            # Capture the result (should be HTML string)
            if 'result' in safe_locals:
                return str(safe_locals['result'])
            else:
                # If no explicit result, try to return the last expression
                return str(logic_code)
                
        except Exception as e:
            return f"<!-- Python Logic Error: {str(e)} -->"
    
    def process_python_loops(self, loop_code: str, context: Dict[str, Any]) -> str:
        """
        Process Python for loops inside PSX
        Example: {for user in users:<UserCard name={user.name} />}
        """
        try:
            match = self.python_loop_pattern.search(loop_code)
            if not match:
                return loop_code
            
            var_name = match.group(1)
            iterable_name = match.group(2)
            template_code = match.group(3).strip()
            
            # Get the iterable from context
            if iterable_name not in context:
                return f"<!-- Loop Error: {iterable_name} not found -->"
            
            iterable = context[iterable_name]
            result_parts = []
            
            # Execute the loop
            for item in iterable:
                loop_context = context.copy()
                loop_context[var_name] = item
                
                # Process the template with current item
                processed = self._process_template(template_code, loop_context)
                result_parts.append(processed)
            
            return ''.join(result_parts)
            
        except Exception as e:
            return f"<!-- Loop Error: {str(e)} -->"
    
    def process_python_conditionals(self, cond_code: str, context: Dict[str, Any]) -> str:
        """
        Process Python if statements inside PSX
        Example: {if user.is_admin:<AdminPanel />}
        """
        try:
            match = self.python_cond_pattern.search(cond_code)
            if not match:
                return cond_code
            
            condition = match.group(1).strip()
            content = match.group(2).strip()
            
            # Evaluate the condition
            safe_globals = {'__builtins__': {}}
            safe_locals = context.copy()
            
            # Evaluate condition
            condition_result = eval(condition, safe_globals, safe_locals)
            
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
            
            # Try to execute the try block
            try:
                safe_globals = {'__builtins__': {}}
                safe_locals = context.copy()
                
                result = eval(try_block, safe_globals, safe_locals)
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
        Process a template string with context variables
        """
        # Replace simple variable references
        def replace_var(match):
            var_name = match.group(1)
            return str(context.get(var_name, f"{{var {var_name}}}"))
        
        # Replace {variable} patterns
        template = re.sub(r'\{(\w+)\}', replace_var, template)
        
        # Replace {expression} patterns
        def replace_expr(match):
            expr = match.group(1)
            try:
                safe_globals = {'__builtins__': {}}
                safe_locals = context.copy()
                result = eval(expr, safe_globals, safe_locals)
                return str(result)
            except:
                return f"{{expr {expr}}}"
        
        template = re.sub(r'\{(.+?)\}', replace_expr, template)
        
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
        
        # Process Python loops
        result = self.python_loop_pattern.sub(
            lambda m: self.process_python_loops(m.group(0), context),
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
            lambda m: str(eval(m.group(1), {"__builtins__": {}}, context)),
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
