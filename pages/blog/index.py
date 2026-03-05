"""
Blog Index Page - NextPy Demo
Demonstrates SSG with getStaticProps
"""

def get_template():
    return "blog/index.html"


async def get_static_props(context):
    """
    Fetch blog posts at build time (SSG)
    Can also be used with SSR by renaming to get_server_side_props
    """
    posts = [
        {
            "slug": "getting-started",
            "title": "Getting Started with NextPy",
            "excerpt": "Learn how to build your first NextPy application with file-based routing and SSR.",
            "date": "November 28, 2024",
            "author": "NextPy Team"
        },
        {
            "slug": "file-based-routing",
            "title": "Understanding File-Based Routing",
            "excerpt": "Deep dive into how NextPy's routing system works and how to create dynamic routes.",
            "date": "November 25, 2024",
            "author": "NextPy Team"
        },
        {
            "slug": "data-fetching",
            "title": "Data Fetching Patterns in NextPy",
            "excerpt": "Explore SSR and SSG data fetching with getServerSideProps and getStaticProps.",
            "date": "November 20, 2024",
            "author": "NextPy Team"
        },
        {
            "slug": "api-routes",
            "title": "Building API Routes with FastAPI",
            "excerpt": "Create powerful API endpoints with full Pydantic validation and type safety.",
            "date": "November 15, 2024",
            "author": "NextPy Team"
        },
        {
            "slug": "htmx-integration",
            "title": "HTMX Integration for Interactivity",
            "excerpt": "Add SPA-like interactivity without heavy JavaScript frameworks using HTMX.",
            "date": "November 10, 2024",
            "author": "NextPy Team"
        },
        {
            "slug": "deployment",
            "title": "Deploying Your NextPy App",
            "excerpt": "Guide to deploying NextPy applications to various hosting platforms.",
            "date": "November 5, 2024",
            "author": "NextPy Team"
        },
    ]
    
    return {
        "props": {
            "title": "Blog",
            "description": "Latest news, tutorials, and updates from the NextPy team.",
            "posts": posts,
        }
    }
