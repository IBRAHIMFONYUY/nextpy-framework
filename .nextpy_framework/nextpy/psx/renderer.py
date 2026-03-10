"""
PSX Renderer - Rendering utilities for PSX components
"""

import inspect
from typing import Any, Dict, Optional
from .parser import PSXElement, render_psx


def render_psx_component(component_func, props: Optional[Dict[str, Any]] = None) -> str:
    """
    Render a PSX component function to HTML
    
    Args:
        component_func: Python function that returns PSX element
        props: Props to pass to the component
        
    Returns:
        Rendered HTML string
    """
    props = props or {}
    
    # Execute the component function
    result = component_func(**props)
    
    # Capture local variables from the component function
    # This is needed for expression evaluation
    context = props.copy()
    
    # Try to get local variables from the component function
    try:
        # Get the frame of the component function execution
        frame = inspect.currentframe()
        if frame and frame.f_back:
            # Get locals from the component function's frame
            component_locals = frame.f_back.f_locals
            # Add component locals to context (excluding internal variables)
            for key, value in component_locals.items():
                if not key.startswith('_') and key not in ['component_func', 'props', 'result']:
                    context[key] = value
    except:
        # If we can't capture locals, just use props
        pass
    
    # Render the result with the captured context
    if isinstance(result, PSXElement):
        return result.to_html(context)
    elif hasattr(result, 'to_html'):
        return result.to_html(context)
    elif isinstance(result, str):
        return render_psx(result, context)
    else:
        return str(result)
