"""
Simple hooks demonstration - working example
"""

import sys
from pathlib import Path

# Add the nextpy framework to the path
sys.path.insert(0, str(Path(__file__).parent / ".nextpy_framework"))

# Import hooks directly
from nextpy.hooks import useState, useEffect, useCounter, useToggle
from nextpy.hooks_provider import with_hooks
from nextpy.jsx import div, h1, p, button


@with_hooks
def CounterComponent(props):
    """Simple counter component with hooks"""
    [count, setCount] = useState(0)
    [customCount, increment, decrement] = useCounter(10)
    [toggled, toggle] = useToggle(False)
    
    # Test state updates
    setCount(5)
    increment()
    toggle()
    
    return div({'className': 'counter'},
        h1({}, f"Count: {count}"),
        p({}, f"Custom Counter: {customCount}"),
        p({}, f"Toggled: {toggled}"),
        button({'onClick': lambda: setCount(count + 1)}, "Increment")
    )


def main():
    """Test the hooks"""
    print("=== Simple Hooks Demo ===\n")
    
    # Import the hooks provider
    from nextpy.hooks_provider import hooks_provider
    
    # Render the component
    result = hooks_provider.render_component_with_hooks(CounterComponent, {})
    
    print("Component Result:")
    print(result)
    print("\n🎉 Hooks are working!")
    print("\nUsage:")
    print("from nextpy import useState, useEffect")
    print("@with_hooks")
    print("def MyComponent(props):")
    print("    [count, setCount] = useState(0)")
    print("    return div({}, f'Count: {count}')")


if __name__ == "__main__":
    main()
