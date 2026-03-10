"""
PSX Renderer - Rendering utilities for PSX components
"""

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
    
    # Render the result
    if isinstance(result, PSXElement):
        return result.to_html(props)
    elif hasattr(result, 'to_html'):
        return result.to_html(props)
    elif isinstance(result, str):
        return render_psx(result, props)
    else:
        return str(result)
