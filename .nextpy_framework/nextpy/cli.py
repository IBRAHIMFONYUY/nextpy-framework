"""
NextPy CLI - Command-line interface for NextPy projects
Commands: dev, build, start
"""

import os
import sys
import time
import asyncio
import signal
from pathlib import Path
from typing import Optional

import click
import uvicorn

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None


class HotReloadHandler:
    """Handles file system changes for hot reload with enhanced JSX support"""
    
    def __init__(self, reload_callback, debug: bool = False):
        self.reload_callback = reload_callback
        self._debounce_timer = None
        self.debug = debug
        self.last_reload_time = 0
        self.reload_cooldown = 0.5  # 500ms cooldown between reloads
        
        # Enhanced file patterns for better JSX detection
        self.file_patterns = {
            "python": [".py"],
            "jsx": [".py.jsx", ".jsx"],
            "templates": [".html", ".htm", ".jinja2", ".j2"],
            "styles": [".css", ".scss", ".sass", ".less"],
            "scripts": [".js", ".ts", ".mjs", ".cjs"],
            "assets": [".json", ".yaml", ".yml", ".toml", ".ini"],
            "config": [".env", ".env.example", "requirements.txt", "package.json", "tailwind.config.js", "postcss.config.js"]
        }
        
        # Directories to watch
        self.watch_dirs = {
            "pages", "components", "templates", "public", 
            "static", "assets", "styles", "scripts", ".nextpy_framework"
        }
        
        # Files that should always trigger reload
        self.critical_files = {
            "main.py", "app.py", "config.py", "settings.py",
            "requirements.txt", "package.json", "pyproject.toml"
        }
        
    def _should_reload_file(self, file_path: str) -> bool:
        """Determine if a file change should trigger reload"""
        file_path = Path(file_path)
        
        # Always reload critical files
        if file_path.name in self.critical_files:
            return True
            
        # Check if file is in a watched directory
        parent_dirs = [part.name for part in file_path.parents]
        if not any(dir_name in self.watch_dirs for dir_name in parent_dirs):
            # If not in watched directories, check if it's in root
            if len(parent_dirs) == 0 or parent_dirs[-1] == ".":
                return any(file_path.name.endswith(pattern) for patterns in self.file_patterns.values() for pattern in patterns)
            return False
            
        # Check file extension against all patterns
        all_extensions = []
        for patterns in self.file_patterns.values():
            all_extensions.extend(patterns)
            
        return any(file_path.name.endswith(ext) for ext in all_extensions)
        
    def _get_file_type(self, file_path: str) -> str:
        """Categorize file type for logging"""
        file_path = Path(file_path)
        
        for file_type, extensions in self.file_patterns.items():
            if any(file_path.name.endswith(ext) for ext in extensions):
                return file_type
                
        return "unknown"
        
    def _debounce_reload(self, file_path: str = None):
        """Debounce reload calls to prevent excessive reloading"""
        current_time = time.time()
        
        if current_time - self.last_reload_time < self.reload_cooldown:
            return
            
        self.last_reload_time = current_time
        
        if self.debug and file_path:
            file_type = self._get_file_type(file_path)
            click.echo(f"  🔄 Hot reload triggered by {file_type} file: {Path(file_path).name}", dim=True)
            
        self._trigger_reload()
        
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
            
        if self._should_reload_file(event.src_path):
            self._debounce_reload(event.src_path)
            
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory and self._should_reload_file(event.src_path):
            self._debounce_reload(event.src_path)
            
    def on_deleted(self, event):
        """Handle file deletion events"""
        if not event.is_directory and self._should_reload_file(event.src_path):
            self._debounce_reload(event.src_path)
            
    def on_moved(self, event):
        """Handle file move/rename events"""
        if not event.is_directory:
            # Handle both source and destination
            if hasattr(event, 'dest_path') and event.dest_path:
                if self._should_reload_file(event.src_path) or self._should_reload_file(event.dest_path):
                    self._debounce_reload(event.dest_path or event.src_path)
            else:
                if self._should_reload_file(event.src_path):
                    self._debounce_reload(event.src_path)
            
    def _trigger_reload(self):
        """Trigger the reload callback"""
        if self.reload_callback:
            self.reload_callback()
            
    def setup_file_watcher(self, project_dir: str = "."):
        """Setup enhanced file watcher with specific patterns"""
        if not WATCHDOG_AVAILABLE:
            click.echo("  ⚠️  Watchdog not installed. Hot reload disabled.", fg="yellow")
            click.echo("  Install with: pip install watchdog", fg="yellow")
            return None
            
        observer = Observer()
        event_handler = WatchdogHotReloadHandler(self._trigger_reload, debug=self.debug)
        
        # Watch specific directories with recursive monitoring
        for watch_dir in self.watch_dirs:
            dir_path = Path(project_dir) / watch_dir
            if dir_path.exists():
                observer.schedule(event_handler, str(dir_path), recursive=True)
                if self.debug:
                    click.echo(f"  📁 Watching directory: {watch_dir}", dim=True)
                    
        # Also watch root directory for critical files
        root_path = Path(project_dir)
        if root_path.exists():
            observer.schedule(event_handler, str(root_path), recursive=False)
            
        return observer


if WATCHDOG_AVAILABLE:
    class WatchdogHotReloadHandler(HotReloadHandler, FileSystemEventHandler):
        """Enhanced watchdog handler with better file filtering"""
        pass
else:
    class WatchdogHotReloadHandler(HotReloadHandler):
        """Fallback handler when watchdog is not available"""
        pass

def find_main_module():
    # main.py is always expected at the project root for NextPy projects
    # We ensure the current directory is in sys.path before calling uvicorn.run
    return "main:app"


def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

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
    """Start the development server with enhanced hot reload"""
    click.echo(click.style("\n  NextPy Development Server", fg="cyan", bold=True))
    click.echo(click.style("  ========================\n", fg="cyan"))
    
    # Set debug environment variable
    if debug:
        os.environ["NEXTPY_DEBUG"] = "true"
        os.environ["DEBUG"] = "true"
        os.environ["DEVELOPMENT"] = "true"
    else:
        os.environ.pop("NEXTPY_DEBUG", None)
        os.environ.pop("DEBUG", None)
        os.environ.pop("DEVELOPMENT", None)
    
    _ensure_project_structure()
    
    click.echo(f"  - Mode:     {'Development' if debug else 'Production'}")
    click.echo(f"  - Host:     {host} (accessible at http://localhost:{port})")
    click.echo(f"  - Port:     {port}")
    click.echo(f"  - Reload:   {'Enabled' if reload else 'Disabled'}")
    click.echo(f"  - Debug:    {'Enabled' if debug else 'Disabled'}")
    
    if reload and not WATCHDOG_AVAILABLE:
        click.echo(f"  - Watchdog: Not Available (install: pip install watchdog)", fg="yellow")
    elif reload:
        click.echo(f"  - Watchdog: Available")
    
    if debug:
        click.echo(f"  - Debug Icon: ✅ Auto-enabled")
        click.echo(f"  - Console Capture: ✅ Enabled")
        click.echo(f"  - Performance Monitoring: ✅ Enabled")
        
    click.echo(f"\n  ✨ Server ready at http://0.0.0.0:{port}")
    click.echo(f"  🌐 Open http://localhost:{port} in your browser\n")
    
    project_dir = Path('.')
    os.chdir(project_dir)

    # Ensure the current directory is in sys.path for module discovery
    if str(project_dir.resolve()) not in sys.path:
        sys.path.insert(0, str(project_dir.resolve()))

    main_module = find_main_module()
    
    if reload:
        # Enhanced reload configuration with JSX support
        reload_dirs = [
            "pages", 
            "components", 
            "templates", 
            "public", 
            "static", 
            "styles", 
            "scripts",
            ".nextpy_framework"
        ]
        
        # Filter to only existing directories
        existing_reload_dirs = []
        for reload_dir in reload_dirs:
            dir_path = project_dir / reload_dir
            if dir_path.exists():
                existing_reload_dirs.append(reload_dir)
                if debug:
                    click.echo(click.style(f"  📁 Watching: {reload_dir}/"))
                    
        # Enhanced reload patterns for JSX files
        reload_includes = [
            "*.py", 
            "*.py.jsx", 
            "*.jsx", 
            "*.html", 
            "*.htm", 
            "*.css", 
            "*.scss", 
            "*.sass", 
            "*.less", 
            "*.js", 
            "*.ts", 
            "*.json", 
            "*.yaml", 
            "*.yml",
            "*.env",
            "requirements.txt",
            "package.json",
            "tailwind.config.js",
            "postcss.config.js"
        ]
        
        uvicorn.run(
            main_module,
            host=host,
            port=port,
            reload=True,
            reload_dirs=existing_reload_dirs,
            reload_includes=reload_includes,
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
    """Build the project for production with enhanced feedback"""
    click.echo(click.style("\n  🔨 NextPy Static Build", fg="green", bold=True))
    click.echo(click.style("  ===================\n", fg="green"))
    
    try:
        from nextpy.core.builder import Builder
        
        click.echo(f"  📂 Output directory: {out}/")
        if clean:
            click.echo(f"  🧹 Cleaning output directory...")
        
        click.echo(f"  ⚙️  Initializing builder...")
        builder = Builder(out_dir=out)
        
        click.echo(f"  🏗️  Building static files...")
        
        async def run_build():
            manifest = await builder.build(clean=clean)
            return manifest
            
        manifest = asyncio.run(run_build())
        
        pages_count = len(manifest.get("pages", {}))
        assets_count = len(manifest.get("assets", []))
        total_size = manifest.get("total_size", 0)
        
        click.echo()
        click.echo(click.style(f"  ✅ Build completed successfully!", fg="green", bold=True))
        click.echo(f"  📄 Pages built: {pages_count}")
        click.echo(f"  🎨 Assets processed: {assets_count}")
        click.echo(f"  💾 Total size: {_format_size(total_size)}")
        click.echo(f"  📍 Output: {out}/")
        click.echo()
        click.echo(click.style(f"  🚀 Ready for deployment!", fg="cyan", bold=True))
        click.echo(f"  📖 Serve with: nextpy start --port 5000")
        click.echo()
        
    except Exception as e:
        click.echo(click.style(f"  ❌ Build failed: {str(e)}", fg="red"))
        if "Builder" not in str(e):
            click.echo(click.style(f"  💡 Make sure you're in a NextPy project directory", fg="yellow"))


@cli.command()
@click.option("--port", "-p", default=5000, help="Port to run the server on")
@click.option("--host", "-h", default="0.0.0.0", help="Host to bind to")
def start(port: int, host: str):
    """Start the production server with enhanced feedback"""
    click.echo(click.style("\n  🚀 NextPy Production Server", fg="green", bold=True))
    click.echo(click.style("  ========================\n", fg="green"))
    
    click.echo(f"  🏭 Mode:     Production")
    click.echo(f"  🌐 Host:     {host} (accessible at http://localhost:{port})")
    click.echo(f"  🔌 Port:     {port}")
    click.echo(f"  👥 Workers:   4 (multi-process)")
    click.echo(f"  📝 Logging:  Warning level only")
    
    click.echo(f"\n  ✨ Production server ready at http://0.0.0.0:{port}")
    click.echo(f"  🌐 Open http://localhost:{port} in your browser\n")
    click.echo(click.style(f"  💡 Press Ctrl+C to stop the server", fg="yellow"))
    click.echo()
    
    try:
        os.chdir(Path.cwd())
        
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            workers=4,
            log_level="warning",
        )
        
    except KeyboardInterrupt:
        click.echo(click.style("\n  👋 Server stopped gracefully", fg="cyan"))
    except Exception as e:
        click.echo(click.style(f"\n  ❌ Server error: {str(e)}", fg="red"))
        click.echo(click.style(f"  💡 Make sure you have a main.py file with an app instance", fg="yellow"))


@cli.command()
@click.argument("name")
def create(name: str):
    """Create a new NextPy project with True JSX support"""
    click.echo(click.style(f"\n  🚀 Creating NextPy project: {name}", fg="cyan", bold=True))
    click.echo(click.style("  " + "=" * (25 + len(name)) + "\n", fg="cyan"))
    
    project_dir = Path(name)
    
    if project_dir.exists():
        click.echo(click.style(f"  ❌ Error: Directory '{name}' already exists", fg="red"))
        click.echo(click.style(f"  💡 Try a different name or remove the existing directory", fg="yellow"))
        return
    
    click.echo(f"  📁 Creating project structure...")
    
    try:
        _create_project_structure(project_dir)
        
        click.echo(click.style(f"  ✅ Project successfully created!", fg="green", bold=True))
        click.echo(f"\n  📍 Location: {project_dir.absolute()}")
        click.echo(f"\n  🎯 Next steps:")
        click.echo(f"    1️⃣  cd {name}")
        click.echo(f"    2️⃣  pip install -r requirements.txt")
        click.echo(f"    3️⃣  nextpy dev")
        click.echo(f"\n  🌐 Your app will be available at: http://localhost:5000")
        click.echo(f"\n  📚 Documentation: https://github.com/IBRAHIMFONYUY/nextpy-framework")
        click.echo()
        
    except Exception as e:
        click.echo(click.style(f"  ❌ Failed to create project: {str(e)}", fg="red"))
        # Clean up partial creation
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir, ignore_errors=True)
        click.echo(click.style(f"  🧹 Cleaned up partial files", fg="yellow"))


@cli.command()
def routes():
    """Display all registered routes with detailed information"""
    click.echo(click.style("\n  🛣️  NextPy Routes Overview", fg="cyan", bold=True))
    click.echo(click.style("  =====================\n", fg="cyan"))
    
    try:
        from nextpy.core.router import Router
        
        router = Router()
        router.scan_pages()
        
        page_routes = [r for r in router.routes if not r.is_api]
        api_routes = router.api_routes
        
        click.echo(click.style(f"  📄 Page Routes ({len(page_routes)} total)", fg="blue", bold=True))
        if page_routes:
            for i, route in enumerate(page_routes, 1):
                dynamic = " 🔀" if route.is_dynamic else " 📄"
                file_info = f"({route.file_path})"
                click.echo(f"    {i:2d}. {dynamic} {route.path:<30} {file_info}")
        else:
            click.echo(f"    ℹ️  No page routes found")
        
        click.echo()
        click.echo(click.style(f"  🔌 API Routes ({len(api_routes)} total)", fg="green", bold=True))
        if api_routes:
            for i, route in enumerate(api_routes, 1):
                dynamic = " 🔀" if route.is_dynamic else " 🔌"
                file_info = f"({route.file_path})"
                methods = "[GET, POST, PUT, DELETE]" if hasattr(route, 'handler') else "[GET]"
                click.echo(f"    {i:2d}. {dynamic} {route.path:<30} {methods:<20} {file_info}")
        else:
            click.echo(f"    ℹ️  No API routes found")
        
        click.echo()
        click.echo(click.style(f"  📊 Summary:", fg="yellow", bold=True))
        click.echo(f"    Total Routes: {len(page_routes + api_routes)}")
        click.echo(f"    Dynamic Routes: {len([r for r in page_routes + api_routes if r.is_dynamic])}")
        click.echo(f"    Static Routes: {len([r for r in page_routes + api_routes if not r.is_dynamic])}")
        click.echo()
        
    except Exception as e:
        click.echo(click.style(f"  ❌ Error scanning routes: {str(e)}", fg="red"))


@cli.command()
@click.option("--out", "-o", default="out", help="Output directory for static files")
def export(out: str):
    """Export static files with enhanced feedback"""
    click.echo(click.style("\n  📦 NextPy Export", fg="green", bold=True))
    click.echo(click.style("  =============\n", fg="green"))
    
    try:
        from nextpy.core.builder import Builder
        
        click.echo(f"  📂 Output directory: {out}/")
        click.echo(f"  ⚙️  Initializing exporter...")
        
        builder = Builder(out_dir=out)
        
        click.echo(f"  📤 Exporting static files...")
        
        async def run_export():
            manifest = await builder.export_static()
            return manifest
            
        manifest = asyncio.run(run_export())
        
        files_count = len(manifest.get("files", []))
        total_size = manifest.get("total_size", 0)
        
        click.echo()
        click.echo(click.style(f"  ✅ Export completed successfully!", fg="green", bold=True))
        click.echo(f"  📁 Files exported: {files_count}")
        click.echo(f"  💾 Total size: {_format_size(total_size)}")
        click.echo(f"  📍 Output: {out}/")
        click.echo()
        click.echo(click.style(f"  🚀 Ready for static hosting!", fg="cyan", bold=True))
        click.echo()
        
    except Exception as e:
        click.echo(click.style(f"  ❌ Export failed: {str(e)}", fg="red"))
        click.echo(click.style(f"  💡 Make sure you're in a NextPy project directory", fg="yellow"))


@cli.command()
def version():
    """Show version and system information"""
    click.echo(click.style("\n  📋 NextPy Framework Info", fg="cyan", bold=True))
    click.echo(click.style("  ===================\n", fg="cyan"))
    
    click.echo(f"  🏷️  Version: 2.2.0")
    click.echo(f"  🐍 Python: {sys.version.split()[0]}")
    click.echo(f"  ⚡ Framework: NextPy")
    click.echo(f"  🎨 Architecture: True JSX")
    click.echo(f"  🖥️  Development Server: uvicorn")
    click.echo(f"  🔄 Hot Reload: Available")
    click.echo(f"  📁 Static Files: Available")
    click.echo(f"  🔌 API Routes: Available")
    click.echo(f"  📄 Page Routes: Available")
    click.echo(f"  🧩 Component Routes: Available")
    click.echo(f"  📚 Component Library: Available")
    click.echo(f"  👨‍💻 Developer: Ibrahim Fonyuy")
    click.echo(f"  📜 License: MIT")
    click.echo(f"  🐙 GitHub: https://github.com/IBRAHIMFONYUY/nextpy-framework")
    click.echo(f"  📖 Documentation: https://nextpy.org/docs")
    click.echo(f"  🆘 Support: https://github.com/IBRAHIMFONYUY/nextpy-framework/issues")
    
    click.echo()


@cli.command()
def info():
    """Show comprehensive framework and system information"""
    click.echo(click.style("\n  🖥️  NextPy System Information", fg="cyan", bold=True))
    click.echo(click.style("  ==========================\n", fg="cyan"))
    
    # Framework info
    click.echo(click.style("  📦 Framework Details:", fg="blue", bold=True))
    click.echo(f"    Version: 2.0.0")
    click.echo(f"    Architecture: True JSX")
    click.echo(f"    Python: {sys.version.split()[0]}")
    
    # Feature status
    click.echo(click.style("\n  ⚡ Feature Status:", fg="green", bold=True))
    watchdog_status = "✅ Available" if WATCHDOG_AVAILABLE else "❌ Not Available (pip install watchdog)"
    click.echo(f"    Hot Reload: {watchdog_status}")
    click.echo(f"    Static Files: ✅ Available")
    click.echo(f"    API Routes: ✅ Available")
    click.echo(f"    Page Routes: ✅ Available")
    click.echo(f"    Component Library: ✅ Available")
    
    # Project structure check
    click.echo(click.style("\n  📁 Project Structure:", fg="yellow", bold=True))
    required_dirs = ["pages", "components", "templates", "public"]
    for dir_name in required_dirs:
        status = "✅" if Path(dir_name).exists() else "❌"
        click.echo(f"    {dir_name}/: {status}")
    
    # Available commands
    click.echo(click.style("\n  🛠️  Available Commands:", fg="purple", bold=True))
    commands = [
        ("nextpy dev", "Start development server"),
        ("nextpy build", "Build for production"),
        ("nextpy start", "Start production server"),
        ("nextpy create <name>", "Create new project"),
        ("nextpy generate <type> <name>", "Generate components/pages/APIs"),
        ("nextpy routes", "Show all routes"),
        ("nextpy export", "Export static files"),
        ("nextpy version", "Show version info"),
        ("nextpy info", "Show this information")
    ]
    for cmd, desc in commands:
        click.echo(f"    {cmd:<25} - {desc}")
    
    click.echo()


@cli.command()
@click.argument("type", type=click.Choice(["page", "api", "component"]))
@click.argument("name")
def generate(type: str, name: str):
    """Generate new page, API endpoint, or component"""
    click.echo(click.style(f"\n  Generating {type}: {name}", fg="cyan", bold=True))
    click.echo(click.style("  " + "=" * (20 + len(name) + len(type)) + "\n", fg="cyan"))
    
    if type == "page":
        _generate_page(name)
    elif type == "api":
        _generate_api(name)
    elif type == "component":
        _generate_component(name)
    
    click.echo(click.style(f"\n  {type.title()} '{name}' created successfully!\n", fg="green", bold=True))


@cli.group()
def plugin():
    """Plugin management commands"""
    pass


@plugin.command()
def list():
    """List all available plugins"""
    click.echo(click.style("\n  🔌 NextPy Plugins", fg="cyan", bold=True))
    click.echo(click.style("  ================\n", fg="cyan"))
    
    try:
        from nextpy.plugins import plugin_manager
        
        plugin_info = plugin_manager.get_plugin_info()
        
        click.echo(click.style(f"  📊 Overview:", fg="blue", bold=True))
        click.echo(f"    Total plugins: {plugin_info['total_plugins']}")
        click.echo(f"    Enabled: {plugin_info['enabled_plugins']}")
        click.echo(f"    Disabled: {plugin_info['total_plugins'] - plugin_info['enabled_plugins']}")
        
        click.echo()
        click.echo(click.style(f"  📋 Plugin Details:", fg="green", bold=True))
        
        for plugin in plugin_info['plugins']:
            status = "✅" if plugin['enabled'] else "❌"
            priority = plugin['priority']
            click.echo(f"    {status} {plugin['name']:<15} v{plugin['version']:<8} (Priority: {priority})")
            
            if plugin['dependencies']:
                click.echo(f"        Dependencies: {', '.join(plugin['dependencies'])}")
        
        click.echo()
        
    except ImportError:
        click.echo(click.style("  ❌ Plugin system not available", fg="red"))
        click.echo(click.style("  💡 Install with: pip install nextpy[plugins]", fg="yellow"))
    except Exception as e:
        click.echo(click.style(f"  ❌ Error: {str(e)}", fg="red"))


@plugin.command()
@click.argument("name")
@click.option("--enable/--disable", default=True, help="Enable or disable the plugin")
def enable(name: str, enable: bool):
    """Enable or disable a plugin"""
    action = "Enabling" if enable else "Disabling"
    click.echo(click.style(f"\n  {action} plugin: {name}", fg="cyan", bold=True))
    click.echo(click.style("  " + "=" * (20 + len(name)) + "\n", fg="cyan"))
    
    try:
        from nextpy.plugins import plugin_manager
        
        if enable:
            plugin_manager.enable_plugin(name)
            click.echo(click.style(f"  ✅ Plugin '{name}' enabled successfully", fg="green"))
        else:
            plugin_manager.disable_plugin(name)
            click.echo(click.style(f"  ❌ Plugin '{name}' disabled", fg="yellow"))
        
        click.echo()
        
    except ImportError:
        click.echo(click.style("  ❌ Plugin system not available", fg="red"))
    except Exception as e:
        click.echo(click.style(f"  ❌ Error: {str(e)}", fg="red"))


@plugin.command()
@click.argument("name")
@click.option("--config", help="Plugin configuration as JSON string")
def configure(name: str, config: str):
    """Configure a plugin"""
    click.echo(click.style(f"\n  ⚙️  Configuring plugin: {name}", fg="cyan", bold=True))
    click.echo(click.style("  " + "=" * (20 + len(name)) + "\n", fg="cyan"))
    
    try:
        from nextpy.plugins import plugin_manager
        import json
        
        if config:
            try:
                config_dict = json.loads(config)
            except json.JSONDecodeError:
                click.echo(click.style("  ❌ Invalid JSON configuration", fg="red"))
                return
        else:
            config_dict = {}
        
        plugin_manager.configure_plugin(name, config_dict)
        click.echo(click.style(f"  ✅ Plugin '{name}' configured successfully", fg="green"))
        
        if config_dict:
            click.echo(f"  Configuration: {json.dumps(config_dict, indent=2)}")
        
        click.echo()
        
    except ImportError:
        click.echo(click.style("  ❌ Plugin system not available", fg="red"))
    except Exception as e:
        click.echo(click.style(f"  ❌ Error: {str(e)}", fg="red"))


@plugin.command()
@click.argument("file_path", type=click.Path(exists=True))
def load(file_path: str):
    """Load a plugin from file"""
    click.echo(click.style(f"\n  📦 Loading plugin from: {file_path}", fg="cyan", bold=True))
    click.echo(click.style("  " + "=" * (25 + len(file_path)) + "\n", fg="cyan"))
    
    try:
        from nextpy.plugins import plugin_manager
        from pathlib import Path
        
        plugin = plugin_manager.load_plugin_from_file(Path(file_path))
        plugin_manager.register_plugin(plugin)
        
        click.echo(click.style(f"  ✅ Plugin '{plugin.name}' loaded successfully", fg="green"))
        click.echo(f"  Version: {plugin.version}")
        click.echo(f"  Priority: {plugin.priority.value}")
        
        click.echo()
        
    except ImportError:
        click.echo(click.style("  ❌ Plugin system not available", fg="red"))
    except Exception as e:
        click.echo(click.style(f"  ❌ Error: {str(e)}", fg="red"))


def _generate_page(name: str):
    """Generate a new page"""
    page_path = Path(f"pages/{name}.py")
    page_path.parent.mkdir(parents=True, exist_ok=True)
    
    content = f'''"""Generated {name} page"""

def {name.title()}(props = None):
    """{name.title()} page component"""
    props = props or {{}}
    
    title = props.get("title", "{name.title()} Page")
    
    return (
        <div class="max-w-4xl px-4 py-12 mx-auto">
            <h1 class="mb-6 text-4xl font-bold text-gray-900">{{title}}</h1>
            <p class="text-lg text-gray-600">
                This is the {name} page generated by NextPy.
            </p>
        </div>
    )

def getServerSideProps(context):
    return {{
        "props": {{
            "title": "{name.title()} Page"
        }}
    }}

default = {name.title()}
'''
    
    page_path.write_text(content)
    click.echo(f"  Created: {page_path}")


def _generate_api(name: str):
    """Generate a new API endpoint"""
    api_path = Path(f"pages/api/{name}.py")
    api_path.parent.mkdir(parents=True, exist_ok=True)
    
    content = f'''"""Generated {name} API endpoint"""

async def get(request):
    """GET /api/{name}"""
    return {{
        "message": "Hello from {name} API!",
        "endpoint": "/api/{name}",
        "method": "GET"
    }}

async def post(request):
    """POST /api/{name}"""
    body = await request.json()
    return {{
        "message": "POST request received",
        "data": body,
        "endpoint": "/api/{name}",
        "method": "POST"
    }}
'''
    
    api_path.write_text(content)
    click.echo(f"  Created: {api_path}")


def _generate_component(name: str):
    """Generate a new component"""
    component_path = Path(f"components/{name}.py")
    component_path.parent.mkdir(parents=True, exist_ok=True)
    
    content = f'''"""Generated {name} component"""

def {name.title()}(props = None):
    """{name.title()} component"""
    props = props or {{}}
    
    children = props.get("children", "")
    className = props.get("className", "")
    
    return (
        <div class="{name.lower()}-component " + className>
            {{children}}
        </div>
    )

default = {name.title()}
'''
    
    component_path.write_text(content)
    click.echo(f"  Created: {component_path}")


def _ensure_project_structure():
    """Ensure the basic project structure exists"""
    dirs = ["pages", "pages/api", "templates", "public", "public/css", "public/js"]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)


def _create_project_structure(project_dir: Path):
    """Create a new project structure with True JSX architecture"""
    dirs = [
        "pages",
        "pages/api",
        "components",
        "components/ui",
        "components/layout",
        "pages/blog",
        "pages/api/users",
        "public",
        "public/css",
        "public/js",
        "public/images",
        "models",
    ]
    
    for dir_path in dirs:
        (project_dir / dir_path).mkdir(parents=True, exist_ok=True)
        click.echo(f"  Created: {dir_path}/")
        
    # Create JSX-based homepage with .py extension
    (project_dir / "pages" / "index.py").write_text('''"""Homepage with True JSX"""

def Home(props = None):
    """Homepage component"""
    props = props or {}
    
    title = props.get("title", "Welcome to NextPy")
    message = props.get("message", "Your Python-powered web framework with True JSX")
    
    return (
        <div class="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-500 to-purple-600">
            <div class="text-center text-white">
                <h1 class="mb-4 text-5xl font-bold">{title}</h1>
                <p class="text-xl">{message}</p>
                <a href="https://github.com/nextpy/nextpy-framework" target="_blank" 
                   class="inline-block px-6 py-3 mt-8 font-semibold text-blue-600 transition-all duration-300 transform bg-white rounded-lg shadow-lg hover:bg-gray-100 hover:text-blue-700 hover:scale-105">
                    Explore NextPy Framework
                </a>
            </div>
        </div>
    )

def getServerSideProps(context):
    return {
        "props": {
            "title": "Welcome to NextPy",
            "message": "Your Python-powered web framework with True JSX"
        }
    }

default = Home
''')
    click.echo("  Created: pages/index.py")
    
    # Create about page with True JSX
    (project_dir / "pages" / "about.py").write_text('''"""About page with True JSX"""

def About(props = None):
    """About page component"""
    props = props or {}
    
    title = props.get("title", "About NextPy")
    description = props.get("description", "Learn about the NextPy framework")
    
    return (
        <div class="max-w-4xl px-4 py-12 mx-auto">
            <h1 class="mb-6 text-4xl font-bold text-gray-900">{title}</h1>
            <p class="mb-4 text-lg text-gray-600">{description}</p>
            <p class="text-gray-700">
                NextPy is a Python web framework inspired by Next.js, offering file-based routing, 
                server-side rendering, static site generation, and a modern True JSX component-based architecture.
            </p>
        </div>
    )

def getServerSideProps(context):
    return {
        "props": {
            "title": "About NextPy",
            "description": "Learn about the NextPy framework"
        }
    }

default = About
''')
    click.echo("  Created: pages/about.py")
    
    # Create a reusable Button component
    (project_dir / "components" / "ui" / "Button.py").write_text('''"""Button component"""

def Button(props = None):
    """Reusable Button component"""
    props = props or {}
    
    variant = props.get("variant", "default")
    children = props.get("children", "Button")
    className = props.get("className", "")
    
    if variant == "primary":
        variant_class = "bg-blue-600 text-white hover:bg-blue-700"
    elif variant == "secondary":
        variant_class = "bg-gray-200 text-gray-900 hover:bg-gray-300"
    else:
        variant_class = "bg-gray-600 text-white hover:bg-gray-700"
    
    class_attr = f"px-4 py-2 rounded-lg font-medium transition-colors {variant_class} {className}"
    
    return (
        <button className={class_attr} 
                id={props.get("id")}
                disabled={props.get("disabled", False)}>
            {children}
        </button>
    )

default = Button
''')
    click.echo("  Created: components/ui/Button.py")
    
    # Create a Layout component
    (project_dir / "components" / "layout" / "Layout.py").write_text('''"""Layout component"""

def Layout(props = None):
    """Layout component wrapper"""
    props = props or {}
    
    title = props.get("title", "NextPy App")
    children = props.get("children", "")
    
    return (
        <div class="flex flex-col min-h-screen">
            <header class="bg-white shadow-sm">
                <div class="px-4 py-4 mx-auto max-w-7xl">
                    <div class="flex items-center justify-between">
                        <h1 class="text-2xl font-bold text-gray-900">{title}</h1>
                        <nav class="flex space-x-4">
                            <a href="/" class="text-gray-600 hover:text-gray-900">Home</a>
                            <a href="/about" class="text-gray-600 hover:text-gray-900">About</a>
                        </nav>
                    </div>
                </div>
            </header>
            <main class="flex-1">
                {children}
            </main>
            <footer class="mt-auto bg-gray-100">
                <div class="px-4 py-6 mx-auto text-center text-gray-600 max-w-7xl">
                    <p>© 2025 NextPy Framework. All rights reserved.</p>
                </div>
            </footer>
        </div>
    )

default = Layout
''')
    click.echo("  Created: components/layout/Layout.py")
    
    # Create VS Code configuration for JSX support
    (project_dir / ".vscode").mkdir(exist_ok=True)
    (project_dir / ".vscode" / "settings.json").write_text('''{
  "files.associations": {
    "*.py": "python",
    "*.py.jsx": "python",
    "*.jsx": "javascriptreact"
  },
  "emmet.includeLanguages": {
    "python": "html",
    "javascriptreact": "html",
    "typescriptreact": "html"
  },
  "emmet.triggerExpansionOnTab": true,
  "typescript.preferences.includePackageJsonAutoImports": "on",
  "editor.quickSuggestions": {
    "strings": true
  },
  "editor.suggestSelection": "first",
  "editor.wordBasedSuggestions": true,
  "editor.snippetSuggestions": "top",
  "editor.parameterHints": {
    "enabled": true
  },
  "editor.snippetSuggestions": "top",
  "html.autoClosingTags": true,
  "css.autoClosingTags": true,
  "javascript.autoClosingTags": true,
  "typescript.autoClosingTags": true,
  "editor.autoClosingBrackets": "always",
  "editor.autoClosingQuotes": "always",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "emmet.preferences": {
    "css.property.endWithSemicolon": true,
    "css.value.unit": "rem"
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/node_modules": true,
    "**/out": true,
    "**/.next": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/out": true,
    "**/.next": true,
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true
  },
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": false,
  "python.linting.pylintArgs": [
    "--disable=C0114,C0115,C0116,E1132,E1131,E1130"
  ],
  "python.formatting.provider": "black",
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.rulers": [88],
    "editor.tabSize": 4,
    "editor.insertSpaces": true
  }
}''')
    click.echo("  Created: .vscode/settings.json")
    
    (project_dir / ".vscode" / "extensions.json").write_text('''{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-json",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense",
    "ms-vscode.vscode-html-css-class-completion",
    "ms-vscode.vscode-emmet",
    "ms-vscode.vscode-eslint",
    "dbaeumer.vscode-eslint",
    "ms-vscode.vscode-typescript-next",
    "ritwickdey.liveserver",
    "ms-vscode.vscode-jest",
    "esbenp.prettier-vscode",
    "streetsidesoftware.code-spell-checker",
    "gruntfuggly.todo-tree",
    "ms-vscode.vscode-git-graph",
    "eamodio.gitlens",
    "ms-vscode.vscode-docker",
    "ms-vscode.remote-explorer",
    "ms-vscode-remote.remote-containers",
    "ms-vscode.vscode-remote-wsl",
    "redhat.vscode-yaml",
    "ms-vscode.vscode-markdown",
    "yzhang.markdown-all-in-one",
    "shd101wyy.markdown-preview-enhanced",
    "ms-vscode.vscode-python",
    "kevinrose.vsc-python-indent",
    "ms-python.black-formatter",
    "ms-python.isort",
    "ms-python.flake8",
    "ms-python.mypy-type-checker"
  ]
}''')
    click.echo("  Created: .vscode/extensions.json")
    
    # Create API example
    (project_dir / "pages" / "api" / "hello.py").write_text('''"""API example"""

def get(request):
    """GET /api/hello"""
    return {"message": "Hello from NextPy API!", "status": "success"}

def post(request):
    """POST /api/hello"""
    return {"message": "POST request received", "status": "success"}
''')
    click.echo("  Created: pages/api/hello.py")
    
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




if __name__ == "__main__":
    cli()