"""
Robots.txt page for SEO - generates raw robots.txt for search engines
"""

def get_template():
    return "robots.txt"


async def get_server_side_props(context):
    """Generate robots.txt"""
    import os
    from fastapi.responses import Response
    
    # Get base URL from environment or use default
    base_url = os.getenv("FRONTEND_URL", "https://nextpy-framework.onrender.com")
    
    # Generate robots.txt content
    robots_content = f"""User-agent: *
Allow: /

# Sitemap location
Sitemap: {base_url}/sitemap.xml

# Allow all pages to be crawled
Allow: /
Allow: /documentation
Allow: /examples
Allow: /features
Allow: /about
Allow: /blog
Allow: /db_example
Allow: /hooks-demo

# Block common non-content paths
Disallow: /api/
Disallow: /_nextpy_debug/
Disallow: /static/
Disallow: *.py$
Disallow: *.html$
"""
    
    # Return as raw text response
    return Response(content=robots_content, media_type="text/plain")
