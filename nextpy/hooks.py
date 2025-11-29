"""
React-like Hooks for NextPy State Management
Implements useState, useEffect, useContext, useReducer, useCallback, useMemo, etc.
"""

from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic, Tuple
from dataclasses import dataclass, field
from functools import wraps
import asyncio

T = TypeVar('T')


@dataclass
class HookState:
    """Manages state for a component"""
    values: Dict[str, Any] = field(default_factory=dict)
    effects: Dict[str, Callable] = field(default_factory=dict)
    effect_dependencies: Dict[str, List] = field(default_factory=dict)
    callbacks: Dict[str, Callable] = field(default_factory=dict)
    callback_dependencies: Dict[str, List] = field(default_factory=dict)


class StateManager:
    """Global state manager for all hooks"""
    
    _instance = None
    _states: Dict[str, HookState] = {}
    _current_component: Optional[str] = None
    _hook_index: Dict[str, int] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def set_component(cls, component_id: Optional[str]):
        """Set current component context"""
        cls._current_component = component_id
        if component_id and component_id not in cls._hook_index:
            cls._hook_index[component_id] = 0
    
    @classmethod
    def get_hook_index(cls) -> int:
        """Get current hook index"""
        if not cls._current_component:
            cls._current_component = "default"
        if cls._current_component not in cls._hook_index:
            cls._hook_index[cls._current_component] = 0
        idx = cls._hook_index[cls._current_component]
        cls._hook_index[cls._current_component] += 1
        return idx
    
    @classmethod
    def reset_hook_index(cls):
        """Reset hook index for next render"""
        if cls._current_component:
            cls._hook_index[cls._current_component] = 0
    
    @classmethod
    def get_state(cls, component_id: str) -> HookState:
        """Get or create state for component"""
        if component_id not in cls._states:
            cls._states[component_id] = HookState()
        return cls._states[component_id]


def useState(initial_value: Any = None) -> Tuple[Any, Callable]:
    """
    React-like useState hook
    Returns (value, setValue) tuple
    
    Usage:
        count, set_count = useState(0)
        set_count(count + 1)
    """
    component_id = StateManager._current_component or "default"
    hook_index = StateManager.get_hook_index()
    state = StateManager.get_state(component_id)
    
    state_key = f"state_{hook_index}"
    
    if state_key not in state.values:
        state.values[state_key] = initial_value
    
    def setter(new_value):
        if callable(new_value):
            state.values[state_key] = new_value(state.values[state_key])
        else:
            state.values[state_key] = new_value
    
    return state.values[state_key], setter


def useEffect(effect: Callable, dependencies: Optional[List] = None) -> None:
    """
    React-like useEffect hook
    Runs effect function when dependencies change
    
    Usage:
        def effect():
            print("Component mounted or deps changed")
            return lambda: print("Cleanup")
        
        useEffect(effect, [count])
    """
    component_id = StateManager._current_component or "default"
    hook_index = StateManager.get_hook_index()
    state = StateManager.get_state(component_id)
    
    effect_key = f"effect_{hook_index}"
    deps_key = f"deps_{hook_index}"
    
    should_run = False
    
    if effect_key not in state.effects:
        should_run = True
    elif dependencies is None:
        should_run = True
    elif state.effect_dependencies.get(deps_key) != dependencies:
        should_run = True
    
    if should_run:
        state.effects[effect_key] = effect
        state.effect_dependencies[deps_key] = dependencies or []
        effect()


def useContext(context_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    React-like useContext hook
    Provides context to component
    
    Usage:
        user_context = {"user": "John", "role": "admin"}
        context = useContext(user_context)
    """
    return context_dict


def useReducer(reducer: Callable, initial_state: Any) -> Tuple[Any, Callable]:
    """
    React-like useReducer hook
    Returns (state, dispatch) tuple
    
    Usage:
        def reducer(state, action):
            if action["type"] == "INCREMENT":
                return state + 1
            return state
        
        count, dispatch = useReducer(reducer, 0)
        dispatch({"type": "INCREMENT"})
    """
    component_id = StateManager._current_component or "default"
    hook_index = StateManager.get_hook_index()
    state = StateManager.get_state(component_id)
    
    state_key = f"reducer_{hook_index}"
    
    if state_key not in state.values:
        state.values[state_key] = initial_state
    
    def dispatch(action):
        current_state = state.values[state_key]
        new_state = reducer(current_state, action)
        state.values[state_key] = new_state
    
    return state.values[state_key], dispatch


def useCallback(callback: Callable, dependencies: Optional[List[Any]] = None) -> Callable:
    """
    React-like useCallback hook
    Memoizes callback function
    
    Usage:
        def on_click():
            print("Clicked")
        
        memoized_click = useCallback(on_click, [])
    """
    component_id = StateManager._current_component or "default"
    hook_index = StateManager.get_hook_index()
    state = StateManager.get_state(component_id)
    
    callback_key = f"callback_{hook_index}"
    deps_key = f"callback_deps_{hook_index}"
    
    if callback_key not in state.callbacks:
        state.callbacks[callback_key] = callback
        state.callback_dependencies[deps_key] = dependencies or []
    elif state.callback_dependencies.get(deps_key) != dependencies:
        state.callbacks[callback_key] = callback
        state.callback_dependencies[deps_key] = dependencies or []
    
    return state.callbacks[callback_key]


def useMemo(compute: Callable, dependencies: Optional[List[Any]] = None) -> Any:
    """
    React-like useMemo hook
    Memoizes expensive computations
    
    Usage:
        expensive_value = useMemo(lambda: compute_value(count), [count])
    """
    component_id = StateManager._current_component or "default"
    hook_index = StateManager.get_hook_index()
    state = StateManager.get_state(component_id)
    
    memo_key = f"memo_{hook_index}"
    deps_key = f"memo_deps_{hook_index}"
    
    if memo_key not in state.values:
        state.values[memo_key] = compute()
        state.effect_dependencies[deps_key] = dependencies or []
    elif state.effect_dependencies.get(deps_key) != dependencies:
        state.values[memo_key] = compute()
        state.effect_dependencies[deps_key] = dependencies or []
    
    return state.values[memo_key]


def useRef(initial_value: Any = None) -> Dict[str, Any]:
    """
    React-like useRef hook
    Returns a mutable ref object
    
    Usage:
        input_ref = useRef()
        input_ref["current"] = some_value
    """
    component_id = StateManager._current_component or "default"
    hook_index = StateManager.get_hook_index()
    state = StateManager.get_state(component_id)
    
    ref_key = f"ref_{hook_index}"
    
    if ref_key not in state.values:
        state.values[ref_key] = {"current": initial_value}
    
    return state.values[ref_key]


class GlobalState(Generic[T]):
    """Global state container for cross-component state"""
    
    _subscribers: Dict[str, List[Callable]] = {}
    _values: Dict[str, Any] = {}
    
    def __init__(self, key: str, initial_value: T):
        self.key = key
        self._values[key] = initial_value
        if key not in self._subscribers:
            self._subscribers[key] = []
    
    def get(self) -> Optional[T]:
        """Get current value"""
        return self._values.get(self.key)
    
    def set(self, value: T) -> None:
        """Set new value and notify subscribers"""
        self._values[self.key] = value
        self._notify_subscribers()
    
    def subscribe(self, callback: Callable) -> Callable:
        """Subscribe to value changes"""
        self._subscribers[self.key].append(callback)
        
        def unsubscribe():
            self._subscribers[self.key].remove(callback)
        
        return unsubscribe
    
    def _notify_subscribers(self) -> None:
        """Notify all subscribers of changes"""
        for callback in self._subscribers.get(self.key, []):
            callback(self._values[self.key])


def create_context(default_value: Any = None) -> Dict[str, Any]:
    """Create a context object"""
    return {
        "value": default_value,
        "consumers": []
    }


def useGlobalState(key: str, initial_value: Any = None) -> Tuple[Any, Callable]:
    """
    Hook to use global state across components
    
    Usage:
        user_state = GlobalState("user", {"name": "John"})
        user, set_user = useGlobalState("user", {"name": "John"})
    """
    if key not in GlobalState._values:
        GlobalState._values[key] = initial_value
        GlobalState._subscribers[key] = []
    
    def setter(value):
        GlobalState._values[key] = value
        for callback in GlobalState._subscribers.get(key, []):
            callback(value)
    
    return GlobalState._values[key], setter


# Component decorator to set component context
def component(func: Callable) -> Callable:
    """
    Decorator to wrap component functions with hook support
    
    Usage:
        @component
        def MyComponent():
            count, set_count = useState(0)
            return f"Count: {count}"
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        component_id = f"{func.__name__}_{id(func)}"
        StateManager.set_component(component_id)
        try:
            result = func(*args, **kwargs)
        finally:
            StateManager.reset_hook_index()
        return result
    
    return wrapper


__all__ = [
    'useState',
    'useEffect',
    'useContext',
    'useReducer',
    'useCallback',
    'useMemo',
    'useRef',
    'GlobalState',
    'create_context',
    'useGlobalState',
    'component',
    'StateManager',
]
