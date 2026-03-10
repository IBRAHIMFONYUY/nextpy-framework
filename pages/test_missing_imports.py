"""
Test missing imports scenario
"""

@component
def Home(props=None):
    props = props or {}
    # title is not defined anywhere
    return (
        <div class="p-4 bg-red-500 text-white">
            <h1>Test: {title}</h1>
            <p>Missing imports test</p>
        </div>
    )



default = Home
