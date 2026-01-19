"""
NextPy CLI - Command-line interface for NextPy projects
Commands: dev, build, start
"""

import os
import sys
import asyncio
import signal
from pathlib import Path
from typing import Optional

import click
import uvicorn
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class HotReloadHandler(FileSystemEventHandler):
    """Handles file system changes for hot reload"""
    
    def __init__(self, reload_callback):
        self.reload_callback = reload_callback
        self._debounce_timer = None
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        extensions = (".py", ".html", ".jinja2", ".css", ".js")
        if isinstance(event.src_path, str) and any(event.src_path.endswith(ext) for ext in extensions):
            self._trigger_reload()
            
    def on_created(self, event):
        if not event.is_directory:
            self._trigger_reload()
            
    def on_deleted(self, event):
        if not event.is_directory:
            self._trigger_reload()
            
    def _trigger_reload(self):
        if self.reload_callback:
            self.reload_callback()

def find_main_module():
    # main.py is always expected at the project root for NextPy projects
    # We ensure the current directory is in sys.path before calling uvicorn.run
    return "main:app"

@click.group()
@click.version_option(version="1.0.0", prog_name="NextPy")
def cli():
    """NextPy - A Python web framework inspired by Next.js"""
    pass


@cli.command()
@click.option("--port", "-p", default=5000, help="Port to run the server on")
@click.option("--host", "-h", default="0.0.0.0", help="Host to bind to")
@click.option("--reload/--no-reload", default=True, help="Enable hot reload")
@click.option("--debug/--no-debug", default=True, help="Enable debug mode")
def dev(port: int, host: str, reload: bool, debug: bool):
    """Start the development server with hot reload"""
    click.echo(click.style("\n  NextPy Development Server", fg="cyan", bold=True))
    click.echo(click.style("  ========================\n", fg="cyan"))
    
    _ensure_project_structure()
    
    click.echo(f"  - Mode:     {'Development' if debug else 'Production'}")
    click.echo(f"  - Host:     {host} (accessible at http://localhost:{port})")
    click.echo(f"  - Port:     {port}")
    click.echo(f"  - Reload:   {'Enabled' if reload else 'Disabled'}")
    click.echo(f"\n  ✨ Server ready at http://0.0.0.0:{port}")
    click.echo(f"  🌐 Open http://localhost:{port} in your browser\n")
    
    project_dir = Path('.')
    os.chdir(project_dir)

    # Ensure the current directory is in sys.path for module discovery
    if str(project_dir.resolve()) not in sys.path:
        sys.path.insert(0, str(project_dir.resolve()))

    main_module = find_main_module()
    
    if reload:
        uvicorn.run(
            main_module,
            host=host,
            port=port,
            reload=True,
            reload_dirs=["pages", "templates", ".nextpy_framework"], # Corrected path
            log_level="info",
        )
    else:
        uvicorn.run(
            main_module,
            host=host,
            port=port,
            log_level="info",
        )


@cli.command()
@click.option("--out", "-o", default="out", help="Output directory for static files")
@click.option("--clean/--no-clean", default=True, help="Clean output directory first")
def build(out: str, clean: bool):
    """Build the project for production (SSG)"""
    click.echo(click.style("\n  NextPy Static Build", fg="green", bold=True))
    click.echo(click.style("  ===================\n", fg="green"))
    
    from nextpy.core.builder import Builder
    
    builder = Builder(out_dir=out)
    
    async def run_build():
        manifest = await builder.build(clean=clean)
        return manifest
        
    manifest = asyncio.run(run_build())
    
    pages_count = len(manifest.get("pages", {}))
    click.echo(f"\n  Built {pages_count} pages")
    click.echo(f"  Output: {out}/")
    click.echo(click.style("\n  Build complete!\n", fg="green", bold=True))


@cli.command()
@click.option("--port", "-p", default=5000, help="Port to run the server on")
@click.option("--host", "-h", default="0.0.0.0", help="Host to bind to")
def start(port: int, host: str):
    """Start the production server"""
    click.echo(click.style("\n  NextPy Production Server", fg="green", bold=True))
    click.echo(click.style("  ========================\n", fg="green"))
    
    click.echo(f"  - Mode:     Production")
    click.echo(f"  - Host:     {host} (accessible at http://localhost:{port})")
    click.echo(f"  - Port:     {port}")
    click.echo(f"\n  ✨ Server ready at http://0.0.0.0:{port}")
    click.echo(f"  🌐 Open http://localhost:{port} in your browser\n")
    
    os.chdir(Path.cwd())
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=4,
        log_level="warning",
    )


@cli.command()
@click.argument("name")
def create(name: str):
    """Create a new NextPy project"""
    click.echo(click.style(f"\n  Creating NextPy project: {name}", fg="cyan", bold=True))
    click.echo(click.style("  " + "=" * (25 + len(name)) + "\n", fg="cyan"))
    
    project_dir = Path(name)
    
    if project_dir.exists():
        click.echo(click.style(f"  Error: Directory '{name}' already exists", fg="red"))
        return
        
    _create_project_structure(project_dir)
    
    click.echo(f"\n  Project created at: {project_dir.absolute()}")
    click.echo(f"\n  Next steps:")
    click.echo(f"    cd {name}")
    click.echo(f"    pip install -r requirements.txt")
    click.echo(f"    nextpy dev")
    click.echo()


@cli.command()
def routes():
    """Display all registered routes"""
    click.echo(click.style("\n  NextPy Routes", fg="cyan", bold=True))
    click.echo(click.style("  =============\n", fg="cyan"))
    
    from nextpy.core.router import Router
    
    router = Router()
    router.scan_pages()
    
    click.echo("  Page Routes:")
    for route in router.routes:
        dynamic = " (dynamic)" if route.is_dynamic else ""
        click.echo(f"    {route.path}{dynamic} -> {route.file_path}")
        
    click.echo("\n  API Routes:")
    for route in router.api_routes:
        dynamic = " (dynamic)" if route.is_dynamic else ""
        click.echo(f"    {route.path}{dynamic} -> {route.file_path}")
        
    click.echo()


def _ensure_project_structure():
    """Ensure the basic project structure exists"""
    dirs = ["pages", "pages/api", "templates", "public", "public/css", "public/js"]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)


def _create_project_structure(project_dir: Path):
    """Create a new project structure"""
    dirs = [
        "pages",
        "pages/api",
        "pages/blog",
        "pages/api/users",
        "templates",
        "templates/components",
        "public",
        "public/css",
        "public/js",
        "public/images",
        "models",
    ]
    
    for dir_path in dirs:
        (project_dir / dir_path).mkdir(parents=True, exist_ok=True)
        click.echo(f"  Created: {dir_path}/")
        
    (project_dir / "pages" / "index.py").write_text('''"""Homepage"""

def get_template():
    return "index.html"

async def get_server_side_props(context):
    return {
        "props": {
            "title": "Welcome to NextPy",
            "message": "Your Python-powered web framework"
        }
    }
''')
    click.echo("  Created: pages/index.py")
    
    (project_dir / "templates" / "_base.html").write_text('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}NextPy App{% endblock %}</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    {% block head %}{% endblock %}
</head>
<body>
    <div id="main-content">
        {% block content %}{{ content | safe }}{% endblock %}
    </div>
    {% block scripts %}{% endblock %}
</body>
</html>
''')
    click.echo("  Created: templates/_base.html")
    
    (project_dir / "templates" / "index.html").write_text('''{% extends "_base.html" %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-500 to-purple-600">
    <div class="text-center text-white">
        <h1 class="mb-4 text-5xl font-bold">{{ title }}</h1>
        <p class="text-xl">{{ message }}</p>
        <a href="https://github.com/nextpy/nextpy-framework" target="_blank" class="inline-block px-6 py-3 mt-8 font-semibold text-blue-600 transition-all duration-300 transform bg-white rounded-lg shadow-lg hover:bg-gray-100 hover:text-blue-700 hover:scale-105">
            Explore NextPy Framework
        </a>
    </div>
</div>
{% endblock %}
''')
    click.echo("  Created: templates/index.html")
    
    (project_dir / "main.py").write_text('''"""NextPy Application Entry Point"""

from nextpy import create_app

app = create_app(debug=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
''')
    click.echo("  Created: main.py")
    
    (project_dir / "requirements.txt").write_text('''fastapi>=0.100.0
uvicorn>=0.23.0
jinja2>=3.1.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
click>=8.1.0
watchdog>=3.0.0
python-multipart>=0.0.6
pillow>=10.0.0
aiofiles>=23.0.0
httpx>=0.24.0
sqlalchemy>=2.0.0
python-dotenv>=1.0.0
pyjwt>=2.8.0
markdown>=3.0.0 # Added markdown for documentation rendering
''')
    click.echo("  Created: requirements.txt")

    (project_dir / "pages" / "about.py").write_text('''"""About page"""

def get_template():
    return "about.html"

async def get_server_side_props(context):
    return {
        "props": {
            "title": "About NextPy",
            "description": "Learn about the NextPy framework"
        }
    }
''')
    click.echo("  Created: pages/about.py")

    # Add the documentation page and template to new projects
    
    (project_dir / "pages" / "documentation.py").write_text('''"""Framework Documentation Page"""
                                                            
 

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



''')
    click.echo("  Created: pages/documentation.py")

    (project_dir / "templates" / "documentation.html").write_text('''{% extends "_base.html" %}

{% extends "_base.html" %}

{% block content %}
<!-- Header -->
<div class="px-4 py-16 mb-12 bg-gradient-to-br from-blue-50 to-indigo-50">
    <div class="max-w-6xl mx-auto">
        <h1 class="mb-4 text-5xl font-bold text-gray-900">Complete Documentation</h1>
        <p class="text-xl text-gray-600">Learn everything about NextPy with detailed guides and examples</p>
    </div>
</div>

<div class="px-4 pb-16 mx-auto max-w-7xl">
    <div class="grid gap-12 lg:grid-cols-4">
        <!-- Sidebar Navigation -->
        <aside class="lg:col-span-1">
            <nav class="sticky space-y-8 text-sm top-20">
                <div>
                    <h3 class="flex items-center gap-2 mb-4 font-bold text-gray-900">
                        <span class="text-lg">🚀</span> Getting Started
                    </h3>
                    <ul class="space-y-3 text-gray-600">
                        <li><a href="#installation" class="hover:text-blue-600 hover:underline">Installation</a></li>
                        <li><a href="#quickstart" class="hover:text-blue-600 hover:underline">Quick Start</a></li>
                        <li><a href="#project-structure" class="hover:text-blue-600 hover:underline">Project Structure</a></li>
                        <li><a href="#cli-commands" class="hover:text-blue-600 hover:underline">CLI Commands</a></li>
                    </ul>
                </div>

                <div>
                    <h3 class="flex items-center gap-2 mb-4 font-bold text-gray-900">
                        <span class="text-lg">📄</span> Core Concepts
                    </h3>
                    <ul class="space-y-3 text-gray-600">
                        <li><a href="#file-based-routing" class="hover:text-blue-600 hover:underline">File-based Routing</a></li>
                        <li><a href="#pages-rendering" class="hover:text-blue-600 hover:underline">Pages & Rendering</a></li>
                        <li><a href="#data-fetching" class="hover:text-blue-600 hover:underline">Data Fetching (SSR/SSG)</a></li>
                        <li><a href="#api-routes" class="hover:text-blue-600 hover:underline">API Routes</a></li>
                    </ul>
                </div>

                <div>
                    <h3 class="flex items-center gap-2 mb-4 font-bold text-gray-900">
                        <span class="text-lg">🔧</span> Advanced
                    </h3>
                    <ul class="space-y-3 text-gray-600">
                        <li><a href="#database" class="hover:text-blue-600 hover:underline">Database Integration</a></li>
                        <li><a href="#authentication" class="hover:text-blue-600 hover:underline">Authentication</a></li>
                        <li><a href="#components" class="hover:text-blue-600 hover:underline">Components & Templates</a></li>
                        <li><a href="#utilities" class="hover:text-blue-600 hover:underline">Built-in Utilities</a></li>
                    </ul>
                </div>

                <div>
                    <h3 class="flex items-center gap-2 mb-4 font-bold text-gray-900">
                        <span class="text-lg">📚</span> Resources
                    </h3>
                    <ul class="space-y-3 text-gray-600">
                        <li><a href="#deployment" class="hover:text-blue-600 hover:underline">Deployment</a></li>
                        <li><a href="#troubleshooting" class="hover:text-blue-600 hover:underline">Troubleshooting</a></li>
                        <li><a href="#best-practices" class="hover:text-blue-600 hover:underline">Best Practices</a></li>
                    </ul>
                </div>

                <div class="p-4 rounded-lg bg-blue-50">
                    <p class="text-sm text-gray-700"><strong>📖 Full Reference:</strong> <a href="/documentation" class="text-blue-600 hover:underline">See DOCUMENTATION.md</a></p>
                </div>
            </nav>
        </aside>

        <!-- Main Content -->
        <div class="space-y-16 lg:col-span-3">
            <!-- Installation -->
            <section id="installation">
                <h2 class="pb-4 mb-6 text-3xl font-bold text-gray-900 border-b-2 border-blue-200">Installation</h2>
                <p class="mb-6 text-gray-700">Get NextPy running in seconds:</p>
                
                <div class="p-6 mb-6 overflow-x-auto font-mono text-sm text-gray-100 bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl">
                    <code class="text-green-400">$ pip install nextpy-framework</code>
                </div>

                <p class="mb-4 text-gray-700">Or create a new project:</p>
                <div class="p-6 overflow-x-auto font-mono text-sm text-gray-100 bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl">
                    <code class="text-green-400">$ nextpy create my-awesome-app<br/>$ cd my-awesome-app<br/>$ nextpy dev</code>
                </div>

                <p class="p-4 mt-6 text-gray-600 border-l-4 border-green-600 rounded-lg bg-green-50">
                    ✨ Your app is now running at <code class="px-2 py-1 bg-green-100 rounded">http://localhost:5000</code>
                </p>
            </section>

            <!-- Quick Start -->
            <section id="quickstart">
                <h2 class="pb-4 mb-6 text-3xl font-bold text-gray-900 border-b-2 border-blue-200">Quick Start</h2>
                
                <div class="p-6 mb-6 bg-gray-50 rounded-xl">
                    <h3 class="mb-3 text-xl font-bold text-gray-900">1. Create Your First Page</h3>
                    <p class="mb-4 text-gray-700">Create <code class="px-2 py-1 text-sm bg-gray-200 rounded">pages/hello.py</code>:</p>
                    <pre class="p-4 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded-lg"><code>def get_template():
    return "hello.html"

async def get_server_side_props(context):
    return {
        "props": {
            "message": "Hello, NextPy!"
        }
    }</code></pre>
                </div>

                <div class="p-6 mb-6 bg-gray-50 rounded-xl">
                    <h3 class="mb-3 text-xl font-bold text-gray-900">2. Create Template</h3>
                    <p class="mb-4 text-gray-700">Create <code class="px-2 py-1 text-sm bg-gray-200 rounded">templates/hello.html</code>:</p>
                    <pre class="p-4 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded-lg"><code>{% raw %}{% extends "_base.html" %}
{% block content %}
<h1>{{ message }}</h1>
{% endblock %}{% endraw %}</code></pre>
                </div>

                <div class="p-6 border-l-4 border-blue-600 bg-blue-50 rounded-xl">
                    <h3 class="mb-3 text-xl font-bold text-gray-900">✅ Done!</h3>
                    <p class="text-gray-700">Visit <code class="px-2 py-1 bg-blue-100 rounded">http://localhost:5000/hello</code> - changes auto-reload!</p>
                </div>
            </section>

            <!-- Project Structure -->
            <section id="project-structure">
                <h2 class="pb-4 mb-6 text-3xl font-bold text-gray-900 border-b-2 border-blue-200">Project Structure</h2>
                
                <pre class="p-6 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded-xl"><code>my-app/
├── pages/                    # File-based routes
│   ├── index.py             # Homepage (/)
│   ├── about.py             # About page (/about)
│   ├── blog/
│   │   ├── index.py        # Blog listing (/blog)
│   │   └── [slug].py       # Dynamic posts (/blog/:slug)
│   └── api/
│       ├── posts.py        # GET /api/posts
│       └── users/[id].py   # GET /api/users/123
├── templates/              # Jinja2 templates
│   ├── _base.html         # Root layout
│   ├── index.html         # Home template
│   └── components/        # Reusable components
├── models/                 # Database models
├── main.py                # Application entry
├── nextpy.config.py       # Configuration
└── .env                   # Secrets</code></pre>
            </section>

            <!-- CLI Commands -->
            <section id="cli-commands">
                <h2 class="pb-4 mb-6 text-3xl font-bold text-gray-900 border-b-2 border-blue-200">CLI Commands</h2>
                
                <div class="space-y-4">
                    <div class="p-4 bg-white border border-gray-200 rounded-lg">
                        <p class="mb-2 font-mono text-sm text-gray-900"><strong>$ nextpy create my-app</strong></p>
                        <p class="text-sm text-gray-600">Create new NextPy project</p>
                    </div>
                    
                    <div class="p-4 bg-white border border-gray-200 rounded-lg">
                        <p class="mb-2 font-mono text-sm text-gray-900"><strong>$ nextpy dev</strong></p>
                        <p class="text-sm text-gray-600">Start development server with hot reload</p>
                    </div>
                    
                    <div class="p-4 bg-white border border-gray-200 rounded-lg">
                        <p class="mb-2 font-mono text-sm text-gray-900"><strong>$ nextpy build</strong></p>
                        <p class="text-sm text-gray-600">Build static site to out/ directory</p>
                    </div>
                    
                    <div class="p-4 bg-white border border-gray-200 rounded-lg">
                        <p class="mb-2 font-mono text-sm text-gray-900"><strong>$ nextpy start</strong></p>
                        <p class="text-sm text-gray-600">Start production server</p>
                    </div>
                </div>
            </section>

            <!-- File-based Routing -->
            <section id="file-based-routing">
                <h2 class="pb-4 mb-6 text-3xl font-bold text-gray-900 border-b-2 border-blue-200">File-based Routing</h2>
                <p class="mb-6 text-gray-700">Files in pages/ automatically become routes:</p>

                <div class="mb-6 overflow-x-auto">
                    <table class="w-full bg-white shadow-sm rounded-xl">
                        <thead class="bg-gray-100 border-b-2 border-gray-200">
                            <tr>
                                <th class="px-6 py-4 font-bold text-left">File</th>
                                <th class="px-6 py-4 font-bold text-left">Route</th>
                                <th class="px-6 py-4 font-bold text-left">Example</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="border-b hover:bg-gray-50">
                                <td class="px-6 py-4 font-mono text-sm">pages/index.py</td>
                                <td class="px-6 py-4 text-blue-600">/</td>
                                <td class="px-6 py-4 text-sm">Home page</td>
                            </tr>
                            <tr class="border-b hover:bg-gray-50">
                                <td class="px-6 py-4 font-mono text-sm">pages/about.py</td>
                                <td class="px-6 py-4 text-blue-600">/about</td>
                                <td class="px-6 py-4 text-sm">About page</td>
                            </tr>
                            <tr class="border-b hover:bg-gray-50">
                                <td class="px-6 py-4 font-mono text-sm">pages/blog/[slug].py</td>
                                <td class="px-6 py-4 text-blue-600">/blog/:slug</td>
                                <td class="px-6 py-4 text-sm">Dynamic posts</td>
                            </tr>
                            <tr class="border-b hover:bg-gray-50">
                                <td class="px-6 py-4 font-mono text-sm">pages/api/posts.py</td>
                                <td class="px-6 py-4 text-blue-600">/api/posts</td>
                                <td class="px-6 py-4 text-sm">API endpoint</td>
                            </tr>
                            <tr class="hover:bg-gray-50">
                                <td class="px-6 py-4 font-mono text-sm">pages/docs/[...path].py</td>
                                <td class="px-6 py-4 text-blue-600">/docs/*</td>
                                <td class="px-6 py-4 text-sm">Catch-all route</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="p-4 border-l-4 border-blue-600 rounded-lg bg-blue-50">
                    <p class="text-sm text-gray-700"><strong>💡 Tip:</strong> Files starting with _ (underscore) are not routes - they're templates like _base.html</p>
                </div>
            </section>

            <!-- Data Fetching -->
            <section id="data-fetching">
                <h2 class="pb-4 mb-6 text-3xl font-bold text-gray-900 border-b-2 border-blue-200">Data Fetching (SSR/SSG)</h2>
                
                <div class="p-6 mb-6 bg-gray-50 rounded-xl">
                    <h3 class="mb-3 text-xl font-bold text-gray-900">Server-Side Rendering (SSR)</h3>
                    <p class="mb-4 text-gray-700">Fetch data <strong>per request</strong>:</p>
                    <pre class="p-4 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded-lg"><code>async def get_server_side_props(context):
    data = await fetch_from_database()
    return {
        "props": {"data": data},
        "revalidate": 60  # Cache 60 seconds
    }</code></pre>
                </div>

                <div class="p-6 bg-gray-50 rounded-xl">
                    <h3 class="mb-3 text-xl font-bold text-gray-900">Static Generation (SSG)</h3>
                    <p class="mb-4 text-gray-700">Fetch data <strong>at build time</strong>:</p>
                    <pre class="p-4 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded-lg"><code>async def get_static_props():
    posts = await get_all_posts()
    return {
        "props": {"posts": posts},
        "revalidate": 3600  # Regenerate hourly
    }

async def get_static_paths():
    posts = await get_all_posts()
    return ["/blog/" + p.slug for p in posts]</code></pre>
                </div>
            </section>

            <!-- API Routes -->
            <section id="api-routes">
                <h2 class="pb-4 mb-6 text-3xl font-bold text-gray-900 border-b-2 border-blue-200">API Routes</h2>
                
                <p class="mb-6 text-gray-700">Create REST APIs with simple Python functions:</p>

                <div class="p-6 mb-6 bg-gray-50 rounded-xl">
                    <h3 class="mb-3 text-xl font-bold text-gray-900">Basic GET</h3>
                    <pre class="p-4 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded-lg"><code>async def get(request):
    posts = await fetch_posts()
    return {"posts": posts}</code></pre>
                </div>

                <div class="p-6 bg-gray-50 rounded-xl">
                    <h3 class="mb-3 text-xl font-bold text-gray-900">POST with Validation</h3>
                    <pre class="p-4 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded-lg"><code>from pydantic import BaseModel

class CreatePost(BaseModel):
    title: str
    content: str

async def post(request):
    body = await request.json()
    post = CreatePost(**body)
    new_post = await save_post(post)
    return {"id": new_post.id}, 201</code></pre>
                </div>
            </section>

            <!-- Database -->
            <section id="database">
                <h2 class="pb-4 mb-6 text-3xl font-bold text-gray-900 border-b-2 border-blue-200">Database Integration</h2>
                
                <p class="mb-6 text-gray-700">NextPy uses SQLAlchemy ORM with support for SQLite, PostgreSQL, and MySQL.</p>

                <div class="p-6 mb-6 bg-gray-50 rounded-xl">
                    <h3 class="mb-3 font-bold">Define a Model</h3>
                    <pre class="p-4 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded-lg"><code>from nextpy.db import Base
from sqlalchemy import Column, String, Integer

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    content = Column(String)</code></pre>
                </div>

                <div class="p-6 bg-gray-50 rounded-xl">
                    <h3 class="mb-3 font-bold">Query Data</h3>
                    <pre class="p-4 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded-lg"><code>from nextpy.db import Session
from models.post import Post

async def get_server_side_props(context):
    with Session() as session:
        posts = session.query(Post).all()
        return {"props": {"posts": posts}}</code></pre>
                </div>
            </section>

            <!-- Authentication -->
            <section id="authentication">
                <h2 class="pb-4 mb-6 text-3xl font-bold text-gray-900 border-b-2 border-blue-200">Authentication</h2>
                
                <p class="mb-6 text-gray-700">Built-in JWT authentication for secure API endpoints.</p>

                <pre class="p-4 mb-6 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded-lg"><code>from nextpy.auth import AuthManager

# Create token
token = AuthManager.create_token(user_id=123)

# Verify token  
user_id = AuthManager.verify_token(token)</code></pre>

                <p class="p-4 text-gray-600 rounded-lg bg-blue-50">
                    📖 See <strong>AUTHENTICATION.md</strong> for complete guide with login examples
                </p>
            </section>

            <!-- Components -->
            <section id="components">
                <h2 class="pb-4 mb-6 text-3xl font-bold text-gray-900 border-b-2 border-blue-200">Components & Templates</h2>
                
                <div class="p-6 mb-6 bg-gray-50 rounded-xl">
                    <h3 class="mb-3 font-bold">Use Built-in Components</h3>
                    <pre class="p-4 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded-lg"><code>{% raw %}{% from 'components/button.html' import button %}
{{ button('Click me', href='/page', variant='primary') }}

{% from 'components/card.html' import card %}
{{ card(title='Title', content='Content') }}{% endraw %}</code></pre>
                </div>

                <div class="p-6 bg-gray-50 rounded-xl">
                    <h3 class="mb-3 font-bold">Create Custom Components</h3>
                    <pre class="p-4 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded-lg"><code>{% raw %}{% macro custom_card(title) %}
<div class="card">
    <h3>{{ title }}</h3>
    {{ caller() }}
</div>
{% endmacro %}{% endraw %}</code></pre>
                </div>
            </section>

            <!-- Utilities -->
            <section id="utilities">
                <h2 class="pb-4 mb-6 text-3xl font-bold text-gray-900 border-b-2 border-blue-200">Built-in Utilities</h2>
                
                <div class="grid gap-6 md:grid-cols-2">
                    <div class="p-6 bg-white border border-gray-200 rounded-lg">
                        <h3 class="mb-3 font-bold text-gray-900">💾 Caching</h3>
                        <pre class="p-3 overflow-x-auto text-xs text-gray-900 bg-gray-100 rounded"><code>from nextpy.utils.cache import cached

@cached(ttl=3600)
async def fetch_data():
    return await db.get_data()</code></pre>
                    </div>
                    
                    <div class="p-6 bg-white border border-gray-200 rounded-lg">
                        <h3 class="mb-3 font-bold text-gray-900">📧 Email</h3>
                        <pre class="p-3 overflow-x-auto text-xs text-gray-900 bg-gray-100 rounded"><code>from nextpy.utils.email import send_email

await send_email(
    to="user@example.com",
    subject="Hello",
    html="<p>Welcome</p>"
)</code></pre>
                    </div>
                    
                    <div class="p-6 bg-white border border-gray-200 rounded-lg">
                        <h3 class="mb-3 font-bold text-gray-900">📁 File Uploads</h3>
                        <pre class="p-3 overflow-x-auto text-xs text-gray-900 bg-gray-100 rounded"><code>from nextpy.utils.uploads import handle_upload

file_name = await handle_upload(
    file,
    upload_dir="public/uploads"
)</code></pre>
                    </div>
                    
                    <div class="p-6 bg-white border border-gray-200 rounded-lg">
                        <h3 class="mb-3 font-bold text-gray-900">🔍 Search</h3>
                        <pre class="p-3 overflow-x-auto text-xs text-gray-900 bg-gray-100 rounded"><code>from nextpy.utils.search import FuzzySearch

search = FuzzySearch(data)
results = search.search("query")</code></pre>
                    </div>
                </div>
            </section>

            <!-- Deployment -->
            <section id="deployment">
                <h2 class="pb-4 mb-6 text-3xl font-bold text-gray-900 border-b-2 border-blue-200">Deployment</h2>
                
                <div class="p-6 mb-6 bg-gray-50 rounded-xl">
                    <h3 class="mb-3 text-xl font-bold text-gray-900">Build for Production</h3>
                    <pre class="p-4 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded-lg"><code>$ nextpy build
# Creates optimized static files in out/</code></pre>
                </div>

                <div class="p-6 bg-gray-50 rounded-xl">
                    <h3 class="mb-3 text-xl font-bold text-gray-900">Environment Variables</h3>
                    <pre class="p-4 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded-lg"><code>DATABASE_URL=postgresql://user:pass@host/db
DEBUG=False
SECRET_KEY=your-secret-key</code></pre>
                </div>
            </section>

            <!-- Troubleshooting -->
            <section id="troubleshooting">
                <h2 class="pb-4 mb-6 text-3xl font-bold text-gray-900 border-b-2 border-blue-200">Troubleshooting</h2>
                
                <div class="space-y-4">
                    <div class="p-6 border-l-4 border-red-600 rounded-lg bg-red-50">
                        <h3 class="mb-2 font-bold text-gray-900">Hot Reload Not Working</h3>
                        <p class="text-sm text-gray-700">Check if watchdog is installed: <code class="px-2 py-1 bg-red-100 rounded">pip install watchdog</code></p>
                    </div>
                    
                    <div class="p-6 border-l-4 border-red-600 rounded-lg bg-red-50">
                        <h3 class="mb-2 font-bold text-gray-900">Database Connection Error</h3>
                        <p class="text-sm text-gray-700">Verify DATABASE_URL in .env and database server is running</p>
                    </div>
                    
                    <div class="p-6 border-l-4 border-red-600 rounded-lg bg-red-50">
                        <h3 class="mb-2 font-bold text-gray-900">Template Not Found</h3>
                        <p class="text-sm text-gray-700">Check template filename in get_template() and file exists in templates/</p>
                    </div>
                </div>
            </section>

            <!-- Best Practices -->
            <section id="best-practices">
                <h2 class="pb-4 mb-6 text-3xl font-bold text-gray-900 border-b-2 border-blue-200">Best Practices</h2>
                
                <ul class="space-y-3 text-gray-700">
                    <li class="flex gap-3">
                        <span class="font-bold text-green-600">✓</span>
                        <span><strong>Use SSG for static content</strong> - Improves performance significantly</span>
                    </li>
                    <li class="flex gap-3">
                        <span class="font-bold text-green-600">✓</span>
                        <span><strong>Cache expensive operations</strong> - Use @cached decorator</span>
                    </li>
                    <li class="flex gap-3">
                        <span class="font-bold text-green-600">✓</span>
                        <span><strong>Validate all inputs</strong> - Use Pydantic models in APIs</span>
                    </li>
                    <li class="flex gap-3">
                        <span class="font-bold text-green-600">✓</span>
                        <span><strong>Use environment variables</strong> - Never hardcode secrets</span>
                    </li>
                    <li class="flex gap-3">
                        <span class="font-bold text-green-600">✓</span>
                        <span><strong>Create reusable components</strong> - Follow DRY principle</span>
                    </li>
                </ul>
            </section>

            <!-- Next Steps -->
            <div class="p-12 mt-16 border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl">
                <h2 class="mb-6 text-3xl font-bold">Ready to Build?</h2>
                <div class="grid gap-6 md:grid-cols-2">
                    <a href="/examples" class="group">
                        <div class="p-6 transition bg-white rounded-xl hover:shadow-lg">
                            <div class="mb-4 text-4xl">🎨</div>
                            <h3 class="font-bold text-gray-900">Components</h3>
                            <p class="text-sm text-gray-600">Explore 20+ pre-built UI components</p>
                        </div>
                    </a>
                    
                    <a href="/blog" class="group">
                        <div class="p-6 transition bg-white rounded-xl hover:shadow-lg">
                            <div class="mb-4 text-4xl">📚</div>
                            <h3 class="font-bold text-gray-900">Blog</h3>
                            <p class="text-sm text-gray-600">Tutorials and best practices</p>
                        </div>
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

''')
    click.echo("  Created: templates/documentation.html")

    (project_dir / "pages" / "blog" / "index.py").write_text('''"""Blog listing"""

def get_template():
    return "blog/index.html"

async def get_server_side_props(context):
    posts = [
        {"slug": "hello", "title": "Hello World"},
        {"slug": "welcome", "title": "Welcome to NextPy"}
    ]
    return {"props": {"posts": posts}}
''')
    click.echo("  Created: pages/blog/index.py")

    (project_dir / "pages" / "blog" / "[slug].py").write_text('''"""Dynamic blog post"""

def get_template():
    return "blog/post.html"

async def get_server_side_props(context):
    slug = context["params"]["slug"]
    return {
        "props": {
            "slug": slug,
            "title": f"Post: {slug}",
            "content": "Blog post content here"
        }
    }
''')
    click.echo("  Created: pages/blog/[slug].py")

    (project_dir / "pages" / "api" / "posts.py").write_text('''"""API route for posts"""

async def get(request):
    """GET /api/posts"""
    return {"posts": [{"id": 1, "title": "Post 1"}]}

async def post(request):
    """POST /api/posts"""
    body = await request.json()
    return {"id": 2, "title": body.get("title")}, 201
''')
    click.echo("  Created: pages/api/posts.py")

    (project_dir / "pages" / "api" / "users" / "[id].py").write_text('''"""Dynamic API route"""

async def get(request):
    """GET /api/users/:id"""
    user_id = request.path_params["id"]
    return {"id": user_id, "name": f"User {user_id}"}

async def put(request):
    """PUT /api/users/:id"""
    user_id = request.path_params["id"]
    body = await request.json()
    return {"id": user_id, "updated": True}

async def delete(request):
    """DELETE /api/users/:id"""
    user_id = request.path_params["id"]
    return {"deleted": True}, 204
''')
    click.echo("  Created: pages/api/users/[id].py")

    (project_dir / "templates" / "components" / "button.html").write_text('''{% macro button(text, href="", onclick="", variant="primary", disabled=false) %}
<a href="{{ href }}" class="px-4 py-2 font-semibold transition rounded-lg" style="background: {% if variant == 'primary' %}#3b82f6{% else %}#6b7280{% endif %}; color: white;">
    {{ text }}
</a>
{% endmacro %}
''')
    click.echo("  Created: templates/components/button.html")

    (project_dir / "templates" / "components" / "card.html").write_text('''{% macro card(title="", content="", footer="") %}
<div class="p-6 mb-4 bg-white rounded-lg shadow-md">
    {% if title %}<h3 class="mb-2 text-lg font-bold">{{ title }}</h3>{% endif %}
    {% if content %}<p class="text-gray-600">{{ content }}</p>{% endif %}
    {% if footer %}<div class="mt-4 text-sm text-gray-500">{{ footer }}</div>{% endif %}
</div>
{% endmacro %}
''')
    click.echo("  Created: templates/components/card.html")

    (project_dir / "templates" / "components" / "modal.html").write_text('''{% macro modal(id="", title="", content="") %}
<div id="{{ id }}" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000;">
    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 24px; border-radius: 8px; min-width: 400px;">
        {% if title %}<h2 class="mb-4 text-2xl font-bold">{{ title }}</h2>{% endif %}
        {% if content %}<p class="mb-6 text-gray-600">{{ content }}</p>{% endif %}
        <button onclick="document.getElementById('{{ id }}').style.display = 'none';" class="px-4 py-2 text-white bg-blue-600 rounded">Close</button>
    </div>
</div>
{% endmacro %}
''')
    click.echo("  Created: templates/components/modal.html")

    (project_dir / "models" / "user.py").write_text('''"""User database model"""

from nextpy.db import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.name}>"
''')
    click.echo("  Created: models/user.py")

    (project_dir / "nextpy.config.py").write_text('''"""NextPy Configuration"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyNextPyApp"
    debug: bool = True
    database_url: str = "sqlite:///app.db"
    secret_key: str = "your-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"

settings = Settings()
''')
    click.echo("  Created: nextpy.config.py")

    (project_dir / ".env").write_text('''DATABASE_URL=sqlite:///app.db
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
''')
    click.echo("  Created: .env")

    (project_dir / ".gitignore").write_text('''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# Database
*.db
*.sqlite3

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Build output
out/
.nextpy/
''')
    click.echo("  Created: .gitignore")
    
    # Copy DOCUMENTATION.md to the new project
    try:
        current_dir = Path(__file__).parent.parent.parent.parent # Adjust based on actual cli.py location
        doc_path = current_dir / "DOCUMENTATION.md"
        if doc_path.exists():
            (project_dir / "DOCUMENTATION.md").write_text(doc_path.read_text())
            click.echo("  Copied: DOCUMENTATION.md")
        else:
            click.echo(click.style("  Warning: DOCUMENTATION.md not found in framework root. Docs page might be empty.", fg="yellow"))
    except Exception as e:
        click.echo(click.style(f"  Error copying DOCUMENTATION.md: {e}", fg="red"))

    # Update _base.html to use /documentation route
    base_html_path = project_dir / "templates" / "_base.html"
    if base_html_path.exists():
        base_html_content = base_html_path.read_text()
        # Ensure the 'Docs' link correctly points to /documentation
        updated_base_html_content = base_html_content.replace(
            '<a href="/docs" class="font-medium text-gray-600 transition-colors hover:text-blue-600" hx-get="/docs" hx-target="#main-content" hx-push-url="true">Docs</a>',
            '<a href="/documentation" class="font-medium text-gray-600 transition-colors hover:text-blue-600" hx-get="/documentation" hx-target="#main-content" hx-push-url="true">Docs</a>'
        ).replace(
            '<li><a href="/docs" class="transition hover:text-white">Getting Started</a></li>',
            '<li><a href="/documentation" class="transition hover:text-white">Getting Started</a></li>'
        ).replace(
            '<li><a href="/docs" class="transition hover:text-white">API Reference</a></li>',
            '<li><a href="/documentation" class="transition hover:text-white">API Reference</a></li>'
        )
        base_html_path.write_text(updated_base_html_content)
        click.echo("  Updated: templates/_base.html with /documentation link")
    else:
        click.echo(click.style("  Warning: templates/_base.html not found in new project. Could not update documentation link.", fg="yellow"))

    # Update index.html to include a link to the NextPy GitHub repository
    index_html_path = project_dir / "templates" / "index.html"
    if index_html_path.exists():
        index_html_content = index_html_path.read_text()
        # Find the closing tag of the <p> element and insert the new link after it
        insertion_point = index_html_content.find('</p>')
        if insertion_point != -1:
            updated_index_html_content = index_html_content[:insertion_point + 4] + \
                                         '        <a href="https://github.com/nextpy/nextpy-framework" target="_blank" class="inline-block px-6 py-3 mt-8 font-semibold text-blue-600 transition-all duration-300 transform bg-white rounded-lg shadow-lg hover:bg-gray-100 hover:text-blue-700 hover:scale-105">\n            Explore NextPy Framework\n        </a>' + \
                                         index_html_content[insertion_point + 4:]
            index_html_path.write_text(updated_index_html_content)
            click.echo("  Updated: templates/index.html with NextPy Framework link")
        else:
            click.echo(click.style("  Warning: Could not find insertion point in templates/index.html to add NextPy Framework link.", fg="yellow"))
    else:
        click.echo(click.style("  Warning: templates/index.html not found in new project. Could not add NextPy Framework link.", fg="yellow"))


if __name__ == "__main__":
    cli()