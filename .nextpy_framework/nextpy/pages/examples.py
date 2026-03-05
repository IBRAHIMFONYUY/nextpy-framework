"""
Examples Page - Shows all available components
"""

def get_template():
    return "examples.html"


async def get_server_side_props(context):
    return {
        "props": {
            "title": "Component Examples",
            "description": "See all NextPy components in action"
        }
    }
