# NextPy Hooks & State Management Guide

NextPy includes React-like hooks for state management and component logic - all in pure Python!

## Table of Contents

1. [useState](#usestate) - Manage component state
2. [useEffect](#useeffect) - Side effects
3. [useContext](#usecontext) - Context values
4. [useReducer](#usereducer) - Complex state
5. [useCallback](#usecallback) - Memoize callbacks
6. [useMemo](#usememo) - Memoize computations
7. [useRef](#useref) - Mutable references
8. [useGlobalState](#useglobalstate) - Cross-component state
9. [Component Decorator](#component-decorator)

---

## useState

The `useState` hook lets you add state to your components.

### Basic Usage

```python
from nextpy import useState, component

@component
def Counter():
    count, set_count = useState(0)
    
    def increment():
        set_count(count + 1)
    
    return f"<p>Count: {count}</p><button onclick='increment()'>+</button>"
```

### Functional Updates

```python
@component
def Form():
    value, set_value = useState("")
    
    # Using a function to compute new value
    def append_char(char):
        set_value(lambda prev: prev + char)
    
    return f"<input value='{value}' />"
```

---

## useEffect

The `useEffect` hook runs side effects when dependencies change.

### Basic Usage

```python
from nextpy import useEffect, component

@component
def Component():
    useEffect(
        lambda: print("Component mounted or deps changed"),
        []  # Empty deps = run once
    )
    
    return "<p>Hello</p>"
```

### With Dependencies

```python
@component
def DataFetcher():
    data, set_data = useState(None)
    
    def fetch_data():
        print(f"Fetching data...")
        # Simulate async fetch
        set_data("loaded")
    
    useEffect(fetch_data, [])  # Run once on mount
    
    return f"<p>{data}</p>"
```

### Cleanup

```python
@component
def Subscription():
    def subscribe():
        print("Subscribed")
        
        def cleanup():
            print("Unsubscribed")
        
        return cleanup
    
    useEffect(subscribe, [])
    return "<p>Subscribed</p>"
```

---

## useContext

The `useContext` hook provides context values to components.

### Basic Usage

```python
from nextpy import useContext, create_context, component

# Create context
user_context = {"user": "John", "role": "admin"}

@component
def UserProfile():
    context = useContext(user_context)
    user = context.get("user")
    role = context.get("role")
    
    return f"<p>{user} ({role})</p>"
```

---

## useReducer

The `useReducer` hook manages complex state with actions.

### Basic Usage

```python
from nextpy import useReducer, component

def counter_reducer(state, action):
    if action["type"] == "INCREMENT":
        return state + 1
    elif action["type"] == "DECREMENT":
        return state - 1
    elif action["type"] == "RESET":
        return 0
    return state

@component
def Counter():
    count, dispatch = useReducer(counter_reducer, 0)
    
    return f"""
    <p>Count: {count}</p>
    <button onclick='dispatch({{"type": "INCREMENT"}})'>+</button>
    <button onclick='dispatch({{"type": "DECREMENT"}})'>-</button>
    <button onclick='dispatch({{"type": "RESET"}})'>Reset</button>
    """
```

### Complex State

```python
def form_reducer(state, action):
    if action["type"] == "SET_FIELD":
        return {**state, action["name"]: action["value"]}
    elif action["type"] == "RESET":
        return {"name": "", "email": ""}
    return state

@component
def Form():
    form, dispatch = useReducer(
        form_reducer,
        {"name": "", "email": ""}
    )
    
    def handle_change(field, value):
        dispatch({
            "type": "SET_FIELD",
            "name": field,
            "value": value
        })
    
    return f"""
    <input value='{form["name"]}' />
    <input value='{form["email"]}' />
    """
```

---

## useCallback

The `useCallback` hook memoizes callback functions.

### Basic Usage

```python
from nextpy import useCallback, component

@component
def Button():
    def on_click():
        print("Button clicked")
    
    # Memoize callback
    memoized_click = useCallback(on_click, [])
    
    return "<button>Click me</button>"
```

### With Dependencies

```python
@component
def SearchBox():
    query, set_query = useState("")
    
    def on_search(term):
        print(f"Searching: {term}")
    
    # Recreate callback only when query changes
    memoized_search = useCallback(
        lambda: on_search(query),
        [query]
    )
    
    return "<input type='search' />"
```

---

## useMemo

The `useMemo` hook memoizes expensive computations.

### Basic Usage

```python
from nextpy import useMemo, component

@component
def List():
    items = [1, 2, 3, 4, 5]
    
    # Expensive computation
    def compute_sum():
        print("Computing...")
        return sum(items)
    
    total = useMemo(compute_sum, [items])
    
    return f"<p>Total: {total}</p>"
```

### With Dependencies

```python
@component
def Chart():
    data, set_data = useState([1, 2, 3])
    
    def process_data():
        # Expensive processing
        return sorted(data, reverse=True)
    
    sorted_data = useMemo(process_data, [data])
    
    return f"<p>{sorted_data}</p>"
```

---

## useRef

The `useRef` hook creates mutable references.

### Basic Usage

```python
from nextpy import useRef, component

@component
def Timer():
    timer_ref = useRef()
    
    def start_timer():
        timer_ref["current"] = 0
    
    def stop_timer():
        timer_ref["current"] = None
    
    return "<p>Timer running</p>"
```

### Storing Previous Value

```python
@component
def Component():
    value, set_value = useState(0)
    prev_value_ref = useRef()
    
    def update():
        prev_value_ref["current"] = value
        set_value(value + 1)
    
    return f"<p>Current: {value}, Previous: {prev_value_ref.get('current')}</p>"
```

---

## useGlobalState

The `useGlobalState` hook shares state across components.

### Basic Usage

```python
from nextpy import useGlobalState, component

@component
def UserInfo():
    user, set_user = useGlobalState("user", {"name": "John"})
    
    return f"<p>{user['name']}</p>"

@component
def UserEditor():
    user, set_user = useGlobalState("user", {"name": "John"})
    
    def update_name(new_name):
        set_user({**user, "name": new_name})
    
    return "<input type='text' />"
```

---

## Component Decorator

Use the `@component` decorator to enable hooks in your functions.

### Basic Usage

```python
from nextpy import component, useState

@component
def MyComponent():
    count, set_count = useState(0)
    
    def increment():
        set_count(count + 1)
    
    return f"""
    <div>
        <p>Count: {count}</p>
        <button onclick='increment()'>Increment</button>
    </div>
    """
```

---

## Best Practices

### 1. Call hooks at top level

```python
@component
def Good():
    count, set_count = useState(0)  # Top level ✓
    
    def helper():
        # Do not call hooks in nested functions ✗
        pass
    
    return "<p>{count}</p>"
```

### 2. Use unique dependencies

```python
@component
def Good():
    count, set_count = useState(0)
    
    # Specify exact dependencies
    useEffect(
        lambda: print(count),
        [count]  # Specific ✓
    )
```

### 3. Combine related state

```python
@component
def Good():
    # Use reducer for related state
    state, dispatch = useReducer(reducer, initial)
    
    # Instead of multiple useState
    # name, set_name = useState("")
    # email, set_email = useState("")
    # age, set_age = useState(0)
```

---

## Complete Example

```python
from nextpy import component, useState, useEffect, useCallback, useMemo

@component
def TodoApp():
    todos, set_todos = useState([])
    input_value, set_input_value = useState("")
    
    def add_todo():
        if input_value:
            new_todos = [*todos, {"text": input_value, "done": False}]
            set_todos(new_todos)
            set_input_value("")
    
    def toggle_todo(index):
        updated = todos.copy()
        updated[index]["done"] = not updated[index]["done"]
        set_todos(updated)
    
    # Memoized add handler
    handle_add = useCallback(add_todo, [input_value, todos])
    
    # Memoized completed count
    completed = useMemo(
        lambda: sum(1 for t in todos if t.get("done")),
        [todos]
    )
    
    return f"""
    <div>
        <h1>Todo App</h1>
        <p>Completed: {completed}/{len(todos)}</p>
        <input value='{input_value}' />
        <button onclick='handle_add()'>Add</button>
        <ul>
            {''.join(f"<li>{todo['text']}</li>" for todo in todos)}
        </ul>
    </div>
    """
```

---

## API Reference

| Hook | Returns | Purpose |
|------|---------|---------|
| `useState(initial)` | `(value, setter)` | Manage state |
| `useEffect(fn, deps)` | `None` | Run side effects |
| `useContext(ctx)` | `context` | Access context |
| `useReducer(reducer, initial)` | `(state, dispatch)` | Complex state |
| `useCallback(fn, deps)` | `function` | Memoize callback |
| `useMemo(fn, deps)` | `value` | Memoize computation |
| `useRef(initial)` | `{current: value}` | Mutable reference |
| `useGlobalState(key, initial)` | `(value, setter)` | Cross-component state |

---

## Next Steps

- Combine hooks with [form components](/documentation#components) for advanced forms
- Use hooks with [API routes](/documentation#api-routes) for full-stack apps
- Explore [examples](/examples) for real-world patterns
- Read [best practices guide](/blog) for performance optimization
