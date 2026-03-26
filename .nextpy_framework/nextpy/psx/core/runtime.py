"""
PSX Runtime - Unified runtime with production-grade security
Integrates AST nodes, safe evaluation, and logic execution
"""

import ast
import html
from typing import Any, Dict, List, Optional, Union
from .ast_nodes import PSXNode, PSXNodeUnion, ExpressionNode, LogicNode, IfNode, ForNode, WhileNode, TryNode, PSXASTParser
from .evaluator import SafeExpressionEngine


class PSXRuntimeError(Exception):
    """Runtime error with context information"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.context = context or {}


class PSXRuntime:
    """Production-grade PSX runtime with AST integration"""
    
    def __init__(self, context: Dict[str, Any] = None):
        self.context = context or {}
        self.evaluator = SafeExpressionEngine(context)
        self.ast_parser = PSXASTParser()
        
        # Performance: Cache compiled expressions
        self._expression_cache: Dict[str, Any] = {}
    
    def evaluate_expression(self, expression: str) -> Any:
        """Safely evaluate an expression with caching"""
        # Check cache first
        if expression in self._expression_cache:
            return self._expression_cache[expression]
        
        try:
            result = self.evaluator.evaluate(expression)
            # Cache simple expressions
            if self._is_cacheable(expression):
                self._expression_cache[expression] = result
            return result
        except Exception as e:
            raise PSXRuntimeError(f"Expression evaluation failed: {expression}. Error: {e}")
    
    def evaluate_ast_expression(self, expression_node: ExpressionNode) -> Any:
        """Evaluate parsed AST expression node"""
        if expression_node.parsed_expression:
            return self.evaluator._evaluate_node(expression_node.parsed_expression)
        else:
            # Parse and cache if not already parsed
            parsed = self.ast_parser.parse_expression(expression_node.expression)
            expression_node.parsed_expression = parsed
            if parsed:
                return self.evaluator._evaluate_node(parsed)
            else:
                return self.evaluate_expression(expression_node.expression)
    
    def execute_logic(self, node: LogicNode) -> str:
        """Execute a logic block using AST structure"""
        try:
            if isinstance(node, IfNode):
                return self._execute_if(node)
            elif isinstance(node, ForNode):
                return self._execute_for(node)
            elif isinstance(node, WhileNode):
                return self._execute_while(node)
            elif isinstance(node, TryNode):
                return self._execute_try(node)
            else:
                return html.escape(f"[Unknown Logic Type: {node.logic_type}]")
        except Exception as e:
            return html.escape(f"[Logic Error: {e}]")
    
    def _execute_if(self, node: IfNode) -> str:
        """Execute if/elif/else logic block using AST"""
        # Evaluate condition
        if node.parsed_condition:
            condition_result = self.evaluator._evaluate_node(node.parsed_condition)
        else:
            condition_result = self.evaluate_expression(node.condition)
        
        if condition_result:
            return self._render_node_list(node.then_body)
        else:
            # Check elif conditions
            for i, (elif_cond, elif_body) in enumerate(zip(node.elif_conditions, node.elif_bodies)):
                # Check parsed condition first
                if i < len(node.elif_parsed_conditions) and node.elif_parsed_conditions[i]:
                    elif_result = self.evaluator._evaluate_node(node.elif_parsed_conditions[i])
                else:
                    elif_result = self.evaluate_expression(elif_cond)
                
                if elif_result:
                    return self._render_node_list(elif_body)
            
            # Execute else if present
            if node.else_body:
                return self._render_node_list(node.else_body)
            
            return ""
    
    def _execute_for(self, node: ForNode) -> str:
        """Execute for loop logic block using AST"""
        # Evaluate iterable
        if node.parsed_iterable:
            iterable = self.evaluator._evaluate_node(node.parsed_iterable)
        else:
            iterable = self.evaluate_expression(node.iterable)
        
        result_parts = []
        for item in iterable:
            # Create local context with loop variable
            local_context = {**self.context, node.variable: item}
            local_runtime = PSXRuntime(local_context)
            result_parts.append(local_runtime._render_node_list(node.body))
        
        return "".join(result_parts)
    
    def _execute_while(self, node: WhileNode) -> str:
        """Execute while loop logic block using AST"""
        result_parts = []
        local_context = {**self.context}
        local_runtime = PSXRuntime(local_context)
        
        while True:
            # Evaluate condition
            if node.parsed_condition:
                condition_result = local_runtime.evaluator._evaluate_node(node.parsed_condition)
            else:
                condition_result = local_runtime.evaluate_expression(node.condition)
            
            if not condition_result:
                break
            
            result_parts.append(local_runtime._render_node_list(node.body))
        
        return "".join(result_parts)
    
    def _execute_try(self, node: TryNode) -> str:
        """Execute try/except/finally logic block"""
        try:
            # Execute try body
            result = self._render_node_list(node.try_body)
            return result
        except Exception as e:
            # Execute except if present
            if node.except_body:
                local_context = {**self.context}
                if node.except_var:
                    local_context[node.except_var] = e
                local_runtime = PSXRuntime(local_context)
                return local_runtime._render_node_list(node.except_body)
            else:
                return html.escape(f"[Exception: {e}]")
        finally:
            # Execute finally if present
            if node.finally_body:
                local_runtime = PSXRuntime(self.context)
                return local_runtime._render_node_list(node.finally_body)
    
    def _render_node_list(self, nodes: List[PSXNodeUnion]) -> str:
        """Render a list of AST nodes to HTML"""
        result_parts = []
        for node in nodes:
            result_parts.append(self._render_node(node))
        return "".join(result_parts)
    
    def _render_node(self, node: PSXNodeUnion) -> str:
        """Render a single AST node to HTML"""
        if isinstance(node, ExpressionNode):
            result = self.evaluate_ast_expression(node)
            return html.escape(str(result))
        elif isinstance(node, LogicNode):
            return self.execute_logic(node)
        # Add other node types as needed
        else:
            return str(node)
    
    def update_context(self, new_context: Dict[str, Any]):
        """Update runtime context and clear cache"""
        self.context.update(new_context)
        self.evaluator = SafeExpressionEngine(self.context)
        self._expression_cache.clear()
    
    def _is_cacheable(self, expression: str) -> bool:
        """Check if expression is safe to cache"""
        # Don't cache expressions that might change
        dangerous_keywords = ['random', 'time', 'datetime', 'now']
        return not any(keyword in expression.lower() for keyword in dangerous_keywords)


def process_python_logic(psx_str: str, context: Dict[str, Any]) -> str:
    """
    Process Python logic in PSX strings
    Handles {for}, {if}, {python:}, {py:} syntax
    """
    import re
    
    def replace_logic(match):
        logic_str = match.group(1).strip()
        
        # Handle different logic types
        if logic_str.startswith('for '):
            # Simple for loop processing
            try:
                # Extract variable and iterable
                if ' in ' in logic_str:
                    var_part, iter_part = logic_str[4:].split(' in ', 1)
                    var_name = var_part.strip()
                    iter_expr = iter_part.strip()
                    
                    # Evaluate iterable safely
                    engine = SafeExpressionEngine(context)
                    iterable = engine.evaluate(iter_expr)
                    result = []
                    for item in iterable:
                        context[var_name] = item
                        # This is simplified - real implementation would handle nested content
                        result.append(str(item))
                    return ''.join(result)
            except:
                return f'{{for loop error: {logic_str}}}'
                
        elif logic_str.startswith('if '):
            # Simple if processing
            try:
                condition = logic_str[3:].strip()
                engine = SafeExpressionEngine(context)
                if engine.evaluate(condition):
                    return 'true'  # Simplified
                else:
                    return ''
            except:
                return f'{{if error: {logic_str}}}'
                
        elif logic_str.startswith(('python:', 'py:')):
            # Python expression
            try:
                expr = logic_str.split(':', 1)[1].strip()
                engine = SafeExpressionEngine(context)
                return str(engine.evaluate(expr))
            except:
                return f'{{python error: {logic_str}}}'
        
        return match.group(0)
    
    # Replace logic patterns
    return re.sub(r'\{([^}]+)\}', replace_logic, psx_str)


# Global runtime instance
runtime = PSXRuntime()
