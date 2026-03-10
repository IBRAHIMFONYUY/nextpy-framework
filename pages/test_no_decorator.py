"""
Test no decorator scenario
"""

def Home(props=None):
    props = props or {}
    title = props.get("title", "Welcome to NextPy")
    return (
        <div class="p-4 bg-green-500 text-white">
            <h1>No Decorator: {title}</h1>
            <p>Just JSX without @component</p>
        </div>
    )



default = Home
