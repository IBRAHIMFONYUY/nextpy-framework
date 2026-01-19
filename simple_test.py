"""
Simple test to demonstrate the new JSX-like syntax
"""

import sys
from pathlib import Path

# Add the nextpy framework to the path
sys.path.insert(0, str(Path(__file__).parent / ".nextpy_framework"))

from nextpy.jsx import div, h1, h2, h3, p, span, strong, jsx, render_jsx


def test_jsx_syntax():
    """Test the JSX-like syntax"""
    print("Testing JSX-like syntax...")
    
    # Create a simple JSX element
    element = div({'className': 'container'},
        h1({'style': 'color: blue;'}, 'Hello NextPy!'),
        p({}, 'This is ', strong({}, 'JSX-like'), ' syntax in Python!')
    )
    
    html = render_jsx(element)
    print("Generated HTML:")
    print(html)
    print()


def test_component_function():
    """Test a component function"""
    print("Testing component function...")
    
    def WelcomeCard(props):
        name = props.get('name', 'World')
        message = props.get('message', 'Welcome to NextPy!')
        
        return div({'className': 'card'},
            h3({}, f'Hello {name}!'),
            p({}, message),
            div({'className': 'button'}, 'Click Me')
        )
    
    component = WelcomeCard({'name': 'NextPy Developer', 'message': 'You are awesome!'})
    html = render_jsx(component)
    print("Generated HTML:")
    print(html)
    print()


def test_nextjs_style_page():
    """Test a Next.js-style page component"""
    print("Testing Next.js-style page...")
    
    def HomePage(props):
        title = props.get('title', 'NextPy Home')
        features = props.get('features', [])
        
        return div({'className': 'page'},
            h1({}, title),
            p({}, 'Welcome to NextPy - Next.js for Python!'),
            div({'className': 'features'},
                *[div({'className': 'feature-card'}, 
                    h3({}, f['title']),
                    p({}, f['description'])
                ) for f in features]
            )
        )
    
    page_props = {
        'title': 'NextPy - Next.js for Python',
        'features': [
            {'title': 'JSX Syntax', 'description': 'Write HTML-like components in Python'},
            {'title': 'File-based Routing', 'description': 'Automatic routing like Next.js'},
            {'title': 'Component System', 'description': 'Reusable components with props'}
        ]
    }
    
    html = render_jsx(HomePage(page_props))
    print("Generated HTML:")
    print(html)
    print()


def main():
    """Run all tests"""
    print("=== NextPy JSX Component System Test ===\n")
    
    test_jsx_syntax()
    test_component_function()
    test_nextjs_style_page()
    
    print("=== All tests completed! ===")
    print("\nThe NextPy JSX component system is working!")
    print("You can now write Next.js-style components in Python!")
    print("\nExample syntax:")
    print("def MyComponent(props):")
    print("    return div({'className': 'container'},")
    print("        h1({}, 'Hello World!'),")
    print("        p({}, props.get('message', 'Default message'))")
    print("    )")


if __name__ == "__main__":
    main()
