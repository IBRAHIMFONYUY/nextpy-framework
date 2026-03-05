"""
Example page demonstrating all NextPy hooks
Shows useState, useEffect, useReducer, useContext, useCallback, useMemo, useRef
"""

def get_template():
    return "hooks-demo.html"


async def get_server_side_props(context):
    """Fetch demo data for hooks showcase"""
    return {
        "props": {
            "title": "NextPy Hooks Demo",
            "description": "Complete hooks system working with SSR",
            "examples": [
                {
                    "hook": "useState",
                    "description": "Manage component state",
                    "code": "count, set_count = useState(0)"
                },
                {
                    "hook": "useEffect",
                    "description": "Run side effects after render",
                    "code": "useEffect(fetch_data, [dependency])"
                },
                {
                    "hook": "useReducer",
                    "description": "Complex state management",
                    "code": "state, dispatch = useReducer(reducer, initial)"
                },
                {
                    "hook": "useContext",
                    "description": "Share state across components",
                    "code": "value = useContext(MyContext)"
                },
                {
                    "hook": "useCallback",
                    "description": "Memoized callback function",
                    "code": "callback = useCallback(fn, [deps])"
                },
                {
                    "hook": "useMemo",
                    "description": "Memoized computed value",
                    "code": "value = useMemo(compute, [deps])"
                },
                {
                    "hook": "useRef",
                    "description": "Direct DOM element access",
                    "code": "ref = useRef(None)"
                }
            ]
        }
    }
