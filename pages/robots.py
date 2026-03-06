"""
Robots.txt page for SEO - tells search engines how to crawl the site
"""

def get_template():
    return "robots.txt"


async def get_server_side_props(context):
    """Generate robots.txt"""
    import os
    
    # Get base URL from environment or use default
    base_url = os.getenv("FRONTEND_URL", "https://nextpy-framework.onrender.com")
    
    return {
        "props": {
            "base_url": base_url
        }
    }
