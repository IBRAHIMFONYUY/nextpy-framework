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
    for path in Path('.').iterdir():
        if path.is_file() and path.name == "main.py":
            return "main:app"
        elif path.is_dir() and (path / "main.py").exists():
            return f"{path.name}.main:app"
    raise FileNotFoundError("Could not find main.py")

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
    
    project_dir = Path('.')  # Or dynamically find the project folder
    os.chdir(project_dir)

    main_module = find_main_module()
    

    
    if reload:
        uvicorn.run(
            main_module,
            host=host,
            port=port,
            reload=True,
            reload_dirs=["pages", "templates", "nextpy"],
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
<div class="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
    <div class="text-center text-white">
        <h1 class="text-5xl font-bold mb-4">{{ title }}</h1>
        <p class="text-xl">{{ message }}</p>
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
<a href="{{ href }}" class="px-4 py-2 rounded-lg font-semibold transition" style="background: {% if variant == 'primary' %}#3b82f6{% else %}#6b7280{% endif %}; color: white;">
    {{ text }}
</a>
{% endmacro %}
''')
    click.echo("  Created: templates/components/button.html")

    (project_dir / "templates" / "components" / "card.html").write_text('''{% macro card(title="", content="", footer="") %}
<div class="bg-white rounded-lg shadow-md p-6 mb-4">
    {% if title %}<h3 class="font-bold text-lg mb-2">{{ title }}</h3>{% endif %}
    {% if content %}<p class="text-gray-600">{{ content }}</p>{% endif %}
    {% if footer %}<div class="mt-4 text-sm text-gray-500">{{ footer }}</div>{% endif %}
</div>
{% endmacro %}
''')
    click.echo("  Created: templates/components/card.html")

    (project_dir / "templates" / "components" / "modal.html").write_text('''{% macro modal(id="", title="", content="") %}
<div id="{{ id }}" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000;">
    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 24px; border-radius: 8px; min-width: 400px;">
        {% if title %}<h2 class="text-2xl font-bold mb-4">{{ title }}</h2>{% endif %}
        {% if content %}<p class="text-gray-600 mb-6">{{ content }}</p>{% endif %}
        <button onclick="document.getElementById('{{ id }}').style.display = 'none';" class="px-4 py-2 bg-blue-600 text-white rounded">Close</button>
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


if __name__ == "__main__":
    cli()
