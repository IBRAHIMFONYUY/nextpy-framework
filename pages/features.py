"""
Features Showcase Page
Demonstrates all NextPy capabilities
"""

def get_template():
    return "features.html"


async def get_server_side_props(context):
    """Showcase all features"""
    features = [
        {
            "icon": "📄",
            "title": "File-Based Routing",
            "description": "Create pages by adding Python files to pages/",
            "link": "/documentation"
        },
        {
            "icon": "🚀",
            "title": "Server-Side Rendering",
            "description": "Render pages on the server with get_server_side_props",
            "link": "/documentation"
        },
        {
            "icon": "⚡",
            "title": "Static Generation",
            "description": "Pre-render pages at build time with get_static_props",
            "link": "/documentation"
        },
        {
            "icon": "🗄️",
            "title": "Database Integration",
            "description": "SQLAlchemy ORM with SQLite, PostgreSQL, MySQL",
            "link": "/db_example"
        },
        {
            "icon": "🔧",
            "title": "API Routes",
            "description": "Create REST APIs with FastAPI in pages/api/",
            "link": "/api/health"
        },
        {
            "icon": "🎨",
            "title": "Components",
            "description": "20+ pre-built UI components",
            "link": "/examples"
        },
        {
            "icon": "🔥",
            "title": "Hot Reload",
            "description": "Instant updates as you code",
            "link": "/documentation"
        },
        {
            "icon": "🔐",
            "title": "Environment Variables",
            "description": "Secure configuration via .env",
            "link": "/documentation"
        },
        {
            "icon": "📊",
            "title": "Async & Sync",
            "description": "Write pages with async or sync functions",
            "link": "/documentation"
        },
        {
            "icon": "🛠️",
            "title": "Utilities",
            "description": "Caching, email, file uploads, search",
            "link": "/examples_advanced"
        }
    ]
    
    return {
        "props": {
            "title": "NextPy Features",
            "description": "Everything you need to build modern web apps",
            "features": features
        }
    }
