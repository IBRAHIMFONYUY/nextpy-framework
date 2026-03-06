"""
Sitemap page for SEO - generates XML sitemap for Google
"""

def get_template():
    return "sitemap_xml.xml"


async def get_server_side_props(context):
    """Generate sitemap with all important pages"""
    import os
    from datetime import datetime
    
    # Get base URL from environment or use default
    base_url = os.getenv("FRONTEND_URL", "https://nextpy-framework.onrender.com")
    
    # Define all pages with their priorities and update frequencies
    pages = [
        {
            "loc": f"{base_url}/",
            "priority": "1.0",
            "changefreq": "daily",
            "lastmod": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "loc": f"{base_url}/documentation",
            "priority": "0.9",
            "changefreq": "weekly",
            "lastmod": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "loc": f"{base_url}/examples",
            "priority": "0.8",
            "changefreq": "weekly",
            "lastmod": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "loc": f"{base_url}/features",
            "priority": "0.8",
            "changefreq": "weekly",
            "lastmod": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "loc": f"{base_url}/about",
            "priority": "0.7",
            "changefreq": "monthly",
            "lastmod": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "loc": f"{base_url}/blog",
            "priority": "0.7",
            "changefreq": "weekly",
            "lastmod": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "loc": f"{base_url}/blog/getting-started",
            "priority": "0.6",
            "changefreq": "monthly",
            "lastmod": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "loc": f"{base_url}/blog/database-guide",
            "priority": "0.6",
            "changefreq": "monthly",
            "lastmod": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "loc": f"{base_url}/db_example",
            "priority": "0.5",
            "changefreq": "monthly",
            "lastmod": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "loc": f"{base_url}/hooks-demo",
            "priority": "0.5",
            "changefreq": "monthly",
            "lastmod": datetime.now().strftime("%Y-%m-%d")
        }
    ]
    
    return {
        "props": {
            "pages": pages,
            "base_url": base_url
        }
    }
