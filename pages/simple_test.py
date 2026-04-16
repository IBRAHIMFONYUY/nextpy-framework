"""
Simple test to isolate the issue
"""

@component
def Simple(props=None):
    props = props or {}
    return (
        <div class="p-4 bg-blue-500 text-white">
            <h1>Simple Test</h1>
            <p>Hello {props.get("name", "World")}</p>
        </div>
    )

default = Simple
