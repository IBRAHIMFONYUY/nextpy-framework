"""
NextPy SEO Utilities
Helpers for SEO optimization, structured data, sitemaps
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime


def create_article_schema(
    title: str,
    description: str,
    image: str,
    author: str,
    date_published: datetime,
    date_modified: Optional[datetime] = None,
    url: str = ""
) -> Dict[str, Any]:
    """Create structured data for article"""
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "image": image,
        "author": {
            "@type": "Person",
            "name": author
        },
        "datePublished": date_published.isoformat(),
        "dateModified": (date_modified or date_published).isoformat(),
        "url": url
    }


def create_organization_schema(
    name: str,
    url: str,
    logo: str,
    contact_url: Optional[str] = None
) -> Dict[str, Any]:
    """Create structured data for organization"""
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": name,
        "url": url,
        "logo": logo,
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "Customer Service",
            "url": contact_url
        } if contact_url else None
    }


def generate_sitemap(routes: List[Dict[str, Any]]) -> str:
    """Generate XML sitemap from routes"""
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for route in routes:
        sitemap += "  <url>\n"
        sitemap += f"    <loc>{route.get('url', '')}</loc>\n"
        if route.get('lastmod'):
            sitemap += f"    <lastmod>{route['lastmod']}</lastmod>\n"
        if route.get('priority'):
            sitemap += f"    <priority>{route['priority']}</priority>\n"
        sitemap += "  </url>\n"
    
    sitemap += "</urlset>"
    return sitemap


def generate_robots_txt(sitemap_url: str) -> str:
    """Generate robots.txt content"""
    return f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /_nextpy/

Sitemap: {sitemap_url}
"""
