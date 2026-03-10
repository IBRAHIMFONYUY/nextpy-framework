"""
PSX Package - Python Syntax eXtension for NextPy
COMPLETE with ALL React hooks, ALL React events, utilities, REVOLUTIONARY PYTHON LOGIC, and OPTIMIZED VIRTUAL DOM!
This makes PSX more powerful than React JSX!
"""

from .preprocessor import compile_psx, compile_psx_file, is_psx_file, PSXCompiler
from .parser import psx, render_psx, PSXElement, PSXParser, fragment, key, process_python_logic
from .renderer import render_psx_component
from .virtual_dom import (
    VNode, NodeType, VDOMDiff, Patch, PatchType, VDOMRenderer, VDOMScheduler,
    create_vnode, create_element, render as vdom_render, update as vdom_update, get_vdom_metrics
)
from .python_logic import (
    PSXPythonLogicEngine, psx_for_loop, psx_if_condition, psx_try_catch, PSXTemplateEngine
)
from .components import (
    # Core Components
    PSXComponent, component, class_component, ChildrenComponent,
    register_component,
    
    # ALL React Hooks (Performance Optimized)
    useState, useEffect, useContext, useReducer, useRef, useMemo, useCallback,
    useImperativeHandle, useLayoutEffect, useDebugValue, useTransition,
    useDeferredValue, useId,
    
    # ALL Custom Hooks (Performance Optimized)
    useCounter, useToggle, useLocalStorage, useFetch, useDebounce, 
    useInterval, usePrevious, useAsync, useMediaQuery, useGeolocation, usePerformance,
    
    # Context API
    create_context, Provider,
    
    # Array Utilities (JavaScript equivalents)
    map_list, filter_list, reduce_list, find_list, some_list, every_list,
    array_length, array_includes, array_join, array_slice, array_push,
    
    # Object Utilities
    object_keys, object_values, object_entries, has_key,
    
    # String Utilities
    string_length, string_upper, string_lower, string_trim, 
    string_split, string_join,
    
    # Math Utilities
    math_max, math_min, math_abs, math_round, math_floor, math_ceil,
    
    # Date Utilities
    date_now, date_format,
    
    # Validation Utilities
    is_string, is_number, is_boolean, is_array, is_object, 
    is_function, is_null, is_undefined,
    
    # Type Conversion Utilities
    to_string, to_number, to_boolean, to_json, from_json,
    
    # Performance Utilities
    performance_now, debounce, throttle,
    
    # Color Utilities
    hex_to_rgb, rgb_to_hex, lighten_color, darken_color,
    
    # URL Utilities
    encode_uri, decode_uri, query_string_to_dict, dict_to_query_string,
    
    # Conditional Rendering
    conditional, and_condition, or_condition, ternary,
    
    # Component Utilities
    fragment, key_value, spread_props, class_names, style_props, merge_refs,
    
    # COMPLETE Event Handlers (ALL React Events)
    EventHandlers,
    # Mouse Events
    create_onclick, create_ondblclick, create_onmousedown, create_onmouseup,
    create_onmouseover, create_onmouseout, create_onmouseenter, create_onmouseleave, create_onmousemove,
    # Form Events
    create_onchange, create_onsubmit, create_onreset, create_onfocus, create_onblur,
    create_oninput, create_oninvalid, create_onselect,
    # Keyboard Events
    create_onkeydown, create_onkeyup, create_onkeypress,
    # Touch Events (Mobile)
    create_ontouchstart, create_ontouchend, create_ontouchmove, create_ontouchcancel,
    # Window/Document Events
    create_onload, create_onunload, create_onresize, create_onscroll,
    # Drag Events
    create_ondrag, create_ondragstart, create_ondragend, create_ondragenter,
    create_ondragleave, create_ondragover, create_ondrop,
    # Media Events
    create_onplay, create_onpause, create_onended, create_onvolumechange,
    create_ontimeupdate, create_onseeking, create_onseeked,
    # Progress Events
    create_onloadstart, create_onprogress, create_onerror, create_onabort,
    # Animation Events
    create_onanimationstart, create_onanimationend, create_onanimationiteration,
    # Transition Events
    create_ontransitionend, create_ontransitionrun, create_ontransitionstart,
    # Wheel Events
    create_onwheel,
    # Clipboard Events
    create_oncopy, create_oncut, create_onpaste,
    # Fullscreen Events
    create_onfullscreenchange, create_onfullscreenerror
)

# Import all event handlers from EventHandlers class
_event_handlers = EventHandlers()

# Create individual event handler functions
create_onclick = _event_handlers.create_onclick
create_ondblclick = _event_handlers.create_ondblclick
create_onmousedown = _event_handlers.create_onmousedown
create_onmouseup = _event_handlers.create_onmouseup
create_onmouseover = _event_handlers.create_onmouseover
create_onmouseout = _event_handlers.create_onmouseout
create_onmouseenter = _event_handlers.create_onmouseenter
create_onmouseleave = _event_handlers.create_onmouseleave
create_onmousemove = _event_handlers.create_onmousemove
create_onchange = _event_handlers.create_onchange
create_onsubmit = _event_handlers.create_onsubmit
create_onreset = _event_handlers.create_onreset
create_onfocus = _event_handlers.create_onfocus
create_onblur = _event_handlers.create_onblur
create_oninput = _event_handlers.create_oninput
create_oninvalid = _event_handlers.create_oninvalid
create_onselect = _event_handlers.create_onselect
create_onkeydown = _event_handlers.create_onkeydown
create_onkeyup = _event_handlers.create_onkeyup
create_onkeypress = _event_handlers.create_onkeypress
create_ontouchstart = _event_handlers.create_ontouchstart
create_ontouchend = _event_handlers.create_ontouchend
create_ontouchmove = _event_handlers.create_ontouchmove
create_ontouchcancel = _event_handlers.create_ontouchcancel
create_onload = _event_handlers.create_onload
create_onunload = _event_handlers.create_onunload
create_onresize = _event_handlers.create_onresize
create_onscroll = _event_handlers.create_onscroll
create_ondrag = _event_handlers.create_ondrag
create_ondragstart = _event_handlers.create_ondragstart
create_ondragend = _event_handlers.create_ondragend
create_ondragenter = _event_handlers.create_ondragenter
create_ondragleave = _event_handlers.create_ondragleave
create_ondragover = _event_handlers.create_ondragover
create_ondrop = _event_handlers.create_ondrop
create_onplay = _event_handlers.create_onplay
create_onpause = _event_handlers.create_onpause
create_onended = _event_handlers.create_onended
create_onvolumechange = _event_handlers.create_onvolumechange
create_ontimeupdate = _event_handlers.create_ontimeupdate
create_onseeking = _event_handlers.create_onseeking
create_onseeked = _event_handlers.create_onseeked
create_onloadstart = _event_handlers.create_onloadstart
create_onprogress = _event_handlers.create_onprogress
create_onerror = _event_handlers.create_onerror
create_onabort = _event_handlers.create_onabort
create_onanimationstart = _event_handlers.create_onanimationstart
create_onanimationend = _event_handlers.create_onanimationend
create_onanimationiteration = _event_handlers.create_onanimationiteration
create_ontransitionend = _event_handlers.create_ontransitionend
create_ontransitionrun = _event_handlers.create_ontransitionrun
create_ontransitionstart = _event_handlers.create_ontransitionstart
create_onwheel = _event_handlers.create_onwheel
create_oncopy = _event_handlers.create_oncopy
create_oncut = _event_handlers.create_oncut
create_onpaste = _event_handlers.create_onpaste
create_onfullscreenchange = _event_handlers.create_onfullscreenchange
create_onfullscreenerror = _event_handlers.create_onfullscreenerror

# Import custom hooks directly from components
useCounter = useCounter
useToggle = useToggle
useLocalStorage = useLocalStorage
useFetch = useFetch
useDebounce = useDebounce
useInterval = useInterval
usePrevious = usePrevious
useAsync = useAsync
useMediaQuery = useMediaQuery
useGeolocation = useGeolocation
usePerformance = usePerformance

__all__ = [
    # Core PSX
    'compile_psx', 'compile_psx_file', 'is_psx_file', 'PSXCompiler',
    'psx', 'render_psx', 'PSXElement', 'PSXParser',
    'render_psx_component',
    
    # Optimized Virtual DOM
    'VNode', 'NodeType', 'VDOMDiff', 'Patch', 'PatchType', 'VDOMRenderer', 'VDOMScheduler',
    'create_vnode', 'create_element', 'vdom_render', 'vdom_update', 'get_vdom_metrics',
    
    # Revolutionary Python Logic
    'process_python_logic', 'PSXPythonLogicEngine', 'psx_for_loop', 
    'psx_if_condition', 'psx_try_catch', 'PSXTemplateEngine',
    
    # Components System
    'PSXComponent', 'component', 'class_component', 'ChildrenComponent',
    'register_component',
    
    # ALL React Hooks (Performance Optimized)
    'useState', 'useEffect', 'useContext', 'useReducer', 'useRef', 
    'useMemo', 'useCallback', 'useImperativeHandle', 'useLayoutEffect', 
    'useDebugValue', 'useTransition', 'useDeferredValue', 'useId',
    
    # ALL Custom Hooks (Performance Optimized)
    'useCounter', 'useToggle', 'useLocalStorage', 'useFetch', 
    'useDebounce', 'useInterval', 'usePrevious', 'useAsync',
    'useMediaQuery', 'useGeolocation', 'usePerformance',
    
    # Context API
    'create_context', 'Provider',
    
    # Array Utilities
    'map_list', 'filter_list', 'reduce_list', 'find_list', 'some_list', 'every_list',
    'array_length', 'array_includes', 'array_join', 'array_slice', 'array_push',
    
    # Object Utilities
    'object_keys', 'object_values', 'object_entries', 'has_key',
    
    # String Utilities
    'string_length', 'string_upper', 'string_lower', 'string_trim',
    'string_split', 'string_join',
    
    # Math Utilities
    'math_max', 'math_min', 'math_abs', 'math_round', 'math_floor', 'math_ceil',
    
    # Date Utilities
    'date_now', 'date_format',
    
    # Validation Utilities
    'is_string', 'is_number', 'is_boolean', 'is_array', 'is_object',
    'is_function', 'is_null', 'is_undefined',
    
    # Type Conversion Utilities
    'to_string', 'to_number', 'to_boolean', 'to_json', 'from_json',
    
    # Performance Utilities
    'performance_now', 'debounce', 'throttle',
    
    # Color Utilities
    'hex_to_rgb', 'rgb_to_hex', 'lighten_color', 'darken_color',
    
    # URL Utilities
    'encode_uri', 'decode_uri', 'query_string_to_dict', 'dict_to_query_string',
    
    # Conditional Rendering
    'conditional', 'and_condition', 'or_condition', 'ternary',
    
    # Component Utilities
    'fragment', 'key', 'key_value', 'spread_props', 'class_names', 'style_props', 'merge_refs',
    
    # COMPLETE Event Handlers (ALL React Events)
    'EventHandlers',
    # Mouse Events
    'create_onclick', 'create_ondblclick', 'create_onmousedown', 'create_onmouseup',
    'create_onmouseover', 'create_onmouseout', 'create_onmouseenter', 'create_onmouseleave', 'create_onmousemove',
    # Form Events
    'create_onchange', 'create_onsubmit', 'create_onreset', 'create_onfocus', 'create_onblur',
    'create_oninput', 'create_oninvalid', 'create_onselect',
    # Keyboard Events
    'create_onkeydown', 'create_onkeyup', 'create_onkeypress',
    # Touch Events (Mobile)
    'create_ontouchstart', 'create_ontouchend', 'create_ontouchmove', 'create_ontouchcancel',
    # Window/Document Events
    'create_onload', 'create_onunload', 'create_onresize', 'create_onscroll',
    # Drag Events
    'create_ondrag', 'create_ondragstart', 'create_ondragend', 'create_ondragenter',
    'create_ondragleave', 'create_ondragover', 'create_ondrop',
    # Media Events
    'create_onplay', 'create_onpause', 'create_onended', 'create_onvolumechange',
    'create_ontimeupdate', 'create_onseeking', 'create_onseeked',
    # Progress Events
    'create_onloadstart', 'create_onprogress', 'create_onerror', 'create_onabort',
    # Animation Events
    'create_onanimationstart', 'create_onanimationend', 'create_onanimationiteration',
    # Transition Events
    'create_ontransitionend', 'create_ontransitionrun', 'create_ontransitionstart',
    # Wheel Events
    'create_onwheel',
    # Clipboard Events
    'create_oncopy', 'create_oncut', 'create_onpaste',
    # Fullscreen Events
    'create_onfullscreenchange', 'create_onfullscreenerror'
]
