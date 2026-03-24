"""
Documentation Page - NextPy Demo
"""

def get_template():
    return "documentation.html"


async def get_server_side_props(context):
    """Fetch documentation data"""
    items=[
                {
                    'link':'/examples',
                    'title': 'Componets' ,
                    'description': 'Explore 20+ pre-built UI components'
                },
                {
                    'link':'/blog',
                    'title': 'Blog' ,
                    'description': 'Tutorials and best practices'
                },
                {
                    'link':'/hooks-demo',
                    'title': 'Hook Demo' ,
                    'description': 'State Management'
                }
                ]
    return {
        "props": {
            "title": "Documentation",
            "description": "Learn how to build with NextPy",
            'items': items
        }
    }
