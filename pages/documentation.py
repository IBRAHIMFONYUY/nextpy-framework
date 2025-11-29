"""
Documentation Page - NextPy Demo
"""

def get_template():
    return "documentation.html"


async def get_server_side_props(context):
    """Fetch documentation data"""
    return {
        "props": {
            "title": "Documentation",
            "description": "Learn how to build with NextPy",
        }
    }
