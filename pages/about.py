"""
About Page - NextPy Demo
"""

def get_template():
    return "about.html"


async def get_server_side_props(context):
    """Fetch about page data"""
    versions = [
        {
            "number": "1.0.0",
            "date": "2024",
            "description": "Initial release with SSR, SSG, and file-based routing"
        },
        {
            "number": "0.9.0",
            "date": "2024",
            "description": "Beta release with core features"
        },
    ]
    
    return {
        "props": {
            "title": "About NextPy",
            "description": "Learn about the Python web framework that brings Next.js patterns to the Python ecosystem.",
            "versions": versions,
        }
    }
