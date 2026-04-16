"""
PSX Component Hydration Integration
Integrates hydration engine with PSX component system
"""

import inspect
import json
import re
from typing import Any, Dict, List, Optional, Callable
from .engine import HydrationContext, get_hydration_engine


class ComponentHydrator:
    """Handles component hydration for interactive components"""
    
    def __init__(self):
        self.engine = get_hydration_engine()
        self.component_metadata: Dict[str, Dict[str, Any]] = {}
    
    def extract_component_metadata(self, component_func: Callable) -> Dict[str, Any]:
        """Extract metadata about a component for hydration"""
        metadata = {
            'name': component_func.__name__,
            'state': {},
            'handlers': {},
            'effects': [],
            'bindings': {},
        }
        
        # Try to analyze function source to extract useState calls
        source = None
        try:
            source = inspect.getsource(component_func)
        except (OSError, TypeError):
            # Source not available - this is OK, happens with wrapped functions
            # Continue with empty state/handlers
            return metadata
        
        if source:
            try:
                metadata['state'] = self._extract_state_from_source(source)
                metadata['handlers'] = self._extract_handlers_from_source(source)
                metadata['effects'] = self._extract_effects_from_source(source)
            except Exception:
                # Continue with whatever we have so far
                pass
        
        return metadata
    
    def _extract_state_from_source(self, source: str) -> Dict[str, Any]:
        """Extract initial state values from useState calls"""
        state = {}
        
        # Match useState patterns: [variable, setVariable] = useState(initialValue)
        pattern = r'\[(\w+),\s*set\w+\]\s*=\s*useState\(([^)]+)\)'
        matches = re.findall(pattern, source)
        
        for var_name, initial_value in matches:
            try:
                # Try to safely evaluate initial value
                # Safe evaluation: only allow literals
                safe_initial = self._safe_eval(initial_value.strip())
                if safe_initial is not None:
                    state[var_name] = safe_initial
                else:
                    state[var_name] = initial_value
            except Exception:
                # If can't eval, store as string
                state[var_name] = str(initial_value)
        
        return state
    
    def _safe_eval(self, value_str: str) -> Any:
        """Safely evaluate literal values"""
        value_str = value_str.strip()
        
        # Handle numbers
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass
        
        # Handle strings
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        
        # Handle booleans
        if value_str == 'True':
            return True
        if value_str == 'False':
            return False
        if value_str == 'None':
            return None
        
        # Handle lists/arrays
        if value_str.startswith('[') and value_str.endswith(']'):
            try:
                return eval(value_str)
            except Exception:
                return value_str
        
        # Handle dicts/objects
        if value_str.startswith('{') and value_str.endswith('}'):
            try:
                return eval(value_str)
            except Exception:
                return value_str
        
        return value_str
    
    def _extract_handlers_from_source(self, source: str) -> Dict[str, str]:
        """Extract event handler code from source"""
        handlers = {}
        
        # Match multiple patterns:
        # 1. onclick={lambda e: ...}
        # 2. create_onclick(lambda e: ...)
        # 3. on[event]={...}
        
        # Pattern for inline event handlers: onclick={lambda e: code}
        pattern = r'on\w+\s*=\s*\{?\s*lambda\s+e\s*:\s*([^}]+)\}?'
        matches = re.findall(pattern, source)
        
        for code in matches:
            # Generate a unique handler name
            handler_name = f'handler_{len(handlers)}'
            handlers[handler_name] = code.strip()
        
        # Pattern for create_onclick style: create_onclick(lambda e: ...)
        pattern2 = r'create_on\w+\s*\(\s*lambda\s+e\s*:\s*([^)]+)\)'
        matches2 = re.findall(pattern2, source)
        
        for code in matches2:
            handler_name = f'handler_{len(handlers)}'
            handlers[handler_name] = code.strip()
        
        return handlers
    
    def _extract_effects_from_source(self, source: str) -> List[Dict[str, Any]]:
        """Extract useEffect calls from source"""
        effects = []
        
        # Match useEffect patterns
        pattern = r'useEffect\s*\(\s*([^,]+)\s*,\s*(\[[^\]]*\])\s*\)'
        matches = re.findall(pattern, source)
        
        for func_name, deps in matches:
            effects.append({
                'function': func_name.strip(),
                'dependencies': deps,
            })
        
        return effects
    
    def register_component(self, component_func: Callable, props: Dict[str, Any]) -> str:
        """Register a component for hydration"""
        metadata = self.extract_component_metadata(component_func)
        
        component_data = {
            'name': metadata['name'],
            'state': metadata['state'],
            'handlers': metadata['handlers'],
            'effects': metadata['effects'],
            'props': props or {},
        }
        
        component_id = self.engine.register_component(component_data)
        return component_id
    
    def generate_hydration_script(self) -> str:
        """Generate complete hydration script"""
        return self.engine.generate_hydration_script()
    
    def wrap_component_html(self, component_id: str, html: str, 
                          state: Dict[str, Any]) -> str:
        """Wrap component HTML with hydration data"""
        return self.engine.generate_html_wrapper(component_id, html, state)


# Global component hydrator instance
_component_hydrator = ComponentHydrator()


def get_component_hydrator() -> ComponentHydrator:
    """Get the global component hydrator"""
    return _component_hydrator


def hydrate_component(component_func: Callable, props: Dict[str, Any], 
                     html: str) -> tuple[str, str]:
    """
    Hydrate a component with interactivity
    
    Returns: (hydrated_html, hydration_script)
    """
    hydrator = get_component_hydrator()
    component_id = hydrator.register_component(component_func, props)
    
    # Extract state from metadata
    metadata = hydrator.extract_component_metadata(component_func)
    state = metadata['state']
    
    # Wrap HTML with hydration data
    hydrated_html = hydrator.wrap_component_html(component_id, html, state)
    
    # Generate hydration script
    hydration_script = hydrator.generate_hydration_script()
    
    return hydrated_html, hydration_script
