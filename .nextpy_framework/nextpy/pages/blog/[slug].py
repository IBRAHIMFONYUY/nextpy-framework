"""
Dynamic Blog Post Page - NextPy Demo
Demonstrates dynamic routing with [slug] parameter
"""

POSTS = {
    "getting-started": {
        "title": "Getting Started with NextPy",
        "date": "November 28, 2024",
        "author": "NextPy Team",
        "read_time": 5,
        "content": """
        <p class="lead">Welcome to NextPy! In this guide, we'll walk through creating your first NextPy application.</p>
        
        <h2>Installation</h2>
        <p>First, install NextPy using pip:</p>
        <pre><code>pip install nextpy</code></pre>
        
        <h2>Create a New Project</h2>
        <p>Use the CLI to create a new project:</p>
        <pre><code>nextpy create my-app
cd my-app</code></pre>
        
        <h2>Project Structure</h2>
        <p>NextPy uses a file-based routing system. Your project will have:</p>
        <ul>
            <li><code>pages/</code> - Your page routes</li>
            <li><code>templates/</code> - Jinja2 templates</li>
            <li><code>public/</code> - Static files</li>
        </ul>
        
        <h2>Start Development</h2>
        <p>Run the development server:</p>
        <pre><code>nextpy dev</code></pre>
        
        <p>Your app is now running at <code>http://localhost:5000</code>!</p>
        """
    },
    "file-based-routing": {
        "title": "Understanding File-Based Routing",
        "date": "November 25, 2024",
        "author": "NextPy Team",
        "read_time": 7,
        "content": """
        <p class="lead">NextPy's file-based routing makes it easy to create pages without configuration.</p>
        
        <h2>Basic Routes</h2>
        <p>Files in the <code>pages/</code> directory automatically become routes:</p>
        <ul>
            <li><code>pages/index.py</code> → <code>/</code></li>
            <li><code>pages/about.py</code> → <code>/about</code></li>
            <li><code>pages/blog/index.py</code> → <code>/blog</code></li>
        </ul>
        
        <h2>Dynamic Routes</h2>
        <p>Use brackets for dynamic segments:</p>
        <ul>
            <li><code>pages/blog/[slug].py</code> → <code>/blog/:slug</code></li>
            <li><code>pages/users/[id].py</code> → <code>/users/:id</code></li>
        </ul>
        
        <h2>Catch-All Routes</h2>
        <p>Use spread syntax for catch-all routes:</p>
        <ul>
            <li><code>pages/docs/[...path].py</code> → <code>/docs/*</code></li>
        </ul>
        """
    },
    "data-fetching": {
        "title": "Data Fetching Patterns in NextPy",
        "date": "November 20, 2024",
        "author": "NextPy Team",
        "read_time": 8,
        "content": """
        <p class="lead">Learn about the different data fetching strategies in NextPy.</p>
        
        <h2>Server-Side Rendering (SSR)</h2>
        <p>Use <code>get_server_side_props</code> to fetch data on every request:</p>
        <pre><code>async def get_server_side_props(context):
    data = await fetch_from_api()
    return {"props": {"data": data}}</code></pre>
        
        <h2>Static Site Generation (SSG)</h2>
        <p>Use <code>get_static_props</code> to fetch data at build time:</p>
        <pre><code>async def get_static_props(context):
    data = await fetch_from_cms()
    return {
        "props": {"data": data},
        "revalidate": 60  # ISR
    }</code></pre>
        
        <h2>When to Use Each</h2>
        <ul>
            <li><strong>SSR:</strong> Dynamic content, user-specific data, real-time updates</li>
            <li><strong>SSG:</strong> Marketing pages, blog posts, documentation</li>
        </ul>
        """
    },
    "api-routes": {
        "title": "Building API Routes with FastAPI",
        "date": "November 15, 2024",
        "author": "NextPy Team",
        "read_time": 6,
        "content": """
        <p class="lead">Create powerful API endpoints with NextPy's built-in FastAPI integration.</p>
        
        <h2>Creating an API Route</h2>
        <p>Add files to <code>pages/api/</code>:</p>
        <pre><code># pages/api/posts.py
from pydantic import BaseModel

class Post(BaseModel):
    title: str
    content: str

async def get(request, params):
    return {"posts": [...]}

async def post(request, params):
    data = await request.json()
    return {"created": data}</code></pre>
        
        <h2>Pydantic Validation</h2>
        <p>Use Pydantic models for automatic validation and documentation.</p>
        """
    },
    "htmx-integration": {
        "title": "HTMX Integration for Interactivity",
        "date": "November 10, 2024",
        "author": "NextPy Team",
        "read_time": 5,
        "content": """
        <p class="lead">Add SPA-like interactivity without heavy JavaScript frameworks.</p>
        
        <h2>What is HTMX?</h2>
        <p>HTMX allows you to access modern browser features directly from HTML.</p>
        
        <h2>Using the Link Component</h2>
        <p>NextPy's Link component automatically uses HTMX for navigation:</p>
        <pre><code>&lt;a href="/about" 
   hx-get="/about" 
   hx-target="#main-content" 
   hx-push-url="true"&gt;
    About Us
&lt;/a&gt;</code></pre>
        
        <h2>Benefits</h2>
        <ul>
            <li>No full page reloads</li>
            <li>Maintains scroll position</li>
            <li>Faster navigation</li>
            <li>Minimal JavaScript</li>
        </ul>
        """
    },
    "deployment": {
        "title": "Deploying Your NextPy App",
        "date": "November 5, 2024",
        "author": "NextPy Team",
        "read_time": 6,
        "content": """
        <p class="lead">Deploy your NextPy application to production.</p>
        
        <h2>Build for Production</h2>
        <pre><code>nextpy build</code></pre>
        
        <h2>Start Production Server</h2>
        <pre><code>nextpy start</code></pre>
        
        <h2>Deployment Options</h2>
        <ul>
            <li><strong>Replit:</strong> Deploy directly from your Repl</li>
            <li><strong>Docker:</strong> Use the included Dockerfile</li>
            <li><strong>Vercel:</strong> Coming soon</li>
        </ul>
        """
    },
}


def get_template():
    return "blog/[slug].html"


async def get_static_paths():
    """
    Generate static paths for all blog posts
    Used with SSG to pre-render all blog post pages
    """
    return {
        "paths": [{"params": {"slug": slug}} for slug in POSTS.keys()],
        "fallback": False
    }


async def get_server_side_props(context):
    """Fetch the blog post data"""
    slug = context.params.get("slug", "")
    
    post = POSTS.get(slug)
    
    if not post:
        return {"not_found": True}
    
    return {
        "props": {
            "post": {
                "slug": slug,
                **post
            }
        }
    }
