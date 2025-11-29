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
        if event.src_path.endswith(extensions):
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
    click.echo(f"  - Host:     {host}")
    click.echo(f"  - Port:     {port}")
    click.echo(f"  - Reload:   {'Enabled' if reload else 'Disabled'}")
    click.echo(f"\n  Ready on http://{host}:{port}\n")
    
    if reload:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,
            reload_dirs=["pages", "templates", "nextpy"],
            log_level="info",
        )
    else:
        uvicorn.run(
            "main:app",
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
    click.echo(f"  - Host:     {host}")
    click.echo(f"  - Port:     {port}")
    click.echo(f"\n  Ready on http://{host}:{port}\n")
    
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
        "templates",
        "public",
        "public/css",
        "public/js",
        "public/images",
        "components",
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
click>=8.1.0
watchdog>=3.0.0
python-multipart>=0.0.6
pillow>=10.0.0
aiofiles>=23.0.0
httpx>=0.24.0
''')
    click.echo("  Created: requirements.txt")


if __name__ == "__main__":
    cli()
