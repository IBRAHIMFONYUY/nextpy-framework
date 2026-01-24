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
        click.echo(click.style("  - Watchdog: Not Available (install: pip install watchdog)", fg="yellow"))
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
        click.echo(click.style(f"  💡 Check the error message above for more details", fg="yellow"))
        # Clean up partial creation
        
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
    
    click.echo(f"  🏷️  Version: 2.4.2")
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
        <div className="max-w-4xl px-4 py-12 mx-auto">
            <h1 className="mb-6 text-4xl font-bold text-gray-900">{{title}}</h1>
            <p className="text-lg text-gray-600">
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
        <div className="{name.lower()}-component " + className>
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
    """Create a complete NextPy project structure with all integrations"""
    dirs = [
        "pages",
        "pages/api",
        "pages/blog",
        "pages/api/users",
        "components",
        "components/ui",
        "components/layout",
        "templates",
        "public",
        "public/css",
        "public/js", 
        "public/images",
        "styles",
        "models",
        "utils",
        "hooks",
        "middleware",
        "tests",
        "docs",
        ".vscode"
    ]
    
    for dir_path in dirs:
        (project_dir / dir_path).mkdir(parents=True, exist_ok=True)
        click.echo(f"  Created: {dir_path}/")
        
    # Create styles.css with Tailwind directives
    (project_dir / "styles.css").write_text('''/* NextPy Styles */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom styles */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

.debug-icon {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #3b82f6;
    color: white;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: bold;
    z-index: 9999;
    cursor: pointer;
    transition: all 0.3s ease;
}

.debug-icon:hover {
    background: #2563eb;
    transform: scale(1.05);
}
''')
    click.echo("  Created: styles.css")
    
    # Create tailwind.config.js with Python support
    (project_dir / "tailwind.config.js").write_text('''module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx,py}',
    './components/**/*.{js,ts,jsx,tsx,mdx,py}',
    './templates/**/*.{html,htm}',
    './app/**/*.{js,ts,jsx,tsx,mdx,py}',
  ],
  theme: {
    extend: {
      colors: {
        blue: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        red: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
        green: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        purple: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#a855f7',
          600: '#9333ea',
          700: '#7c3aed',
          800: '#6b21a8',
          900: '#581c87',
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/postcss'),
  ],
};''')
    click.echo("  Created: tailwind.config.js")
    
    # Create postcss.config.js with new Tailwind plugin
    (project_dir / "postcss.config.js").write_text('''module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
};''')
    click.echo("  Created: postcss.config.js")
    
    # Create package.json with Node.js dependencies
    (project_dir / "package.json").write_text('''{
  "name": "nextpy-app",
  "version": "1.0.0",
  "description": "A NextPy application with True JSX and Tailwind CSS",
  "main": "index.js",
  "scripts": {
    "dev": "nextpy dev",
    "build": "nextpy build",
    "start": "nextpy start"
  },
  "keywords": ["python", "nextpy", "jsx", "tailwind"],
  "author": "",
  "license": "MIT",
  "devDependencies": {
    "autoprefixer": "^10.4.22",
    "postcss": "^8.5.6",
    "tailwindcss": "^4.1.17"
  },
  "dependencies": {
    "@tailwindcss/postcss": "^4.1.18",
    "postcss-cli": "^11.0.1"
  }
}''')
    click.echo("  Created: package.json")
        
    # Create interactive homepage with advanced features
    (project_dir / "pages" / "index.py").write_text('''"""Interactive Homepage with True JSX"""

def Home(props=None):
    props = props or {}
    title = props.get("title", "Welcome to NextPy!")
    message = props.get("message", "Build amazing web apps with Python and True JSX")
    
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600">
            {/* Navigation */}
            <nav className="bg-white border-b border-white bg-opacity-10 backdrop-blur-md border-opacity-20">
                <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <div className="flex items-center">
                            <h1 className="text-xl font-bold text-white">NextPy</h1>
                        </div>
                        <div className="flex space-x-4">
                            <a href="/about" className="px-3 py-2 text-sm font-medium text-white transition-colors rounded-md hover:text-blue-200">
                                About
                            </a>
                            <a href="/features" className="px-3 py-2 text-sm font-medium text-white transition-colors rounded-md hover:text-blue-200">
                                Features
                            </a>
                            <a href="/docs" className="px-3 py-2 text-sm font-medium text-white transition-colors rounded-md hover:text-blue-200">
                                Docs
                            </a>
                        </div>
                    </div>
                </div>
            </nav>
            
            {/* Hero Section */}
            <div className="relative overflow-hidden">
                <div className="mx-auto max-w-7xl">
                    <div className="relative z-10 pb-8 bg-transparent sm:pb-16 md:pb-20 lg:pb-28 xl:pb-32">
                        <main className="mx-auto mt-10 max-w-7xl sm:mt-12 sm:px-6 lg:mt-16 lg:px-8 xl:mt-20">
                            <div className="text-center">
                                <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl md:text-6xl">
                                    <span className="block xl:inline">Build amazing web apps with</span>
                                    <span className="block text-blue-200 xl:inline">Python and True JSX</span>
                                </h1>
                                <p className="max-w-lg mx-auto mt-6 text-xl text-blue-100 sm:text-2xl">
                                    {message}
                                </p>
                                <div className="flex justify-center mt-10">
                                    <a href="/getting-started" className="inline-flex items-center justify-center px-8 py-3 text-base font-medium text-blue-600 transition-all duration-300 transform bg-white border border-transparent rounded-md hover:bg-blue-50 md:py-4 md:text-lg md:px-10 hover:scale-105">
                                        Get Started
                                    </a>
                                    <a href="https://github.com/nextpy/nextpy" className="inline-flex items-center justify-center px-8 py-3 ml-4 text-base font-medium text-white transition-all duration-300 transform bg-blue-500 border border-transparent rounded-md hover:bg-blue-600 md:py-4 md:text-lg md:px-10 hover:scale-105">
                                        GitHub
                                    </a>
                                </div>
                            </div>
                        </main>
                    </div>
                </div>
                
                {/* Background decoration */}
                <div className="absolute inset-0 -z-10">
                    <div className="absolute top-0 transform -translate-x-1/2 left-1/2 blur-3xl opacity-20">
                        <div className="rounded-full aspect-square w-96 h-96 bg-gradient-to-r from-blue-400 to-purple-600"></div>
                    </div>
                    <div className="absolute top-0 transform translate-x-1/2 right-1/2 blur-3xl opacity-20">
                        <div className="rounded-full aspect-square w-96 h-96 bg-gradient-to-r from-purple-400 to-pink-600"></div>
                    </div>
                </div>
            </div>
            
            {/* Features Section */}
            <div className="py-12 bg-white">
                <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
                    <div className="lg:text-center">
                        <h2 className="text-base font-semibold tracking-wide text-blue-600 uppercase">
                            Features
                        </h2>
                        <p className="mt-2 text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                            Everything you need to build amazing apps
                        </p>
                    </div>
                    
                    <div className="mt-10">
                        <div className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10 lg:grid-cols-3">
                            {/* Feature 1 */}
                            <div className="relative">
                                <div className="absolute flex items-center justify-center w-12 h-12 text-white bg-blue-500 rounded-md">
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7m0 0v7l9-11h-7z" />
                                    </svg>
                                </div>
                                <p className="ml-16 text-lg font-medium leading-6 text-gray-900">
                                    True JSX Components
                                </p>
                                <p className="mt-2 ml-16 text-base text-gray-500">
                                    Write React-like components directly in Python with full JSX support.
                                </p>
                                <a href="/jsx-demo" className="mt-4 ml-16 text-base font-medium text-blue-600 hover:text-blue-500">
                                    Learn more →
                                </a>
                            </div>
                            
                            {/* Feature 2 */}
                            <div className="relative">
                                <div className="absolute flex items-center justify-center w-12 h-12 text-white bg-purple-500 rounded-md">
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
                                    </svg>
                                </div>
                                <p className="ml-16 text-lg font-medium leading-6 text-gray-900">
                                    Tailwind CSS Integration
                                </p>
                                <p className="mt-2 ml-16 text-base text-gray-500">
                                    Built-in Tailwind CSS v4 with PostCSS compilation and utility classes.
                                </p>
                                <a href="/tailwind-demo" className="mt-4 ml-16 text-base font-medium text-blue-600 hover:text-blue-500">
                                    Learn more →
                                </a>
                            </div>
                            
                            {/* Feature 3 */}
                            <div className="relative">
                                <div className="absolute flex items-center justify-center w-12 h-12 text-white bg-green-500 rounded-md">
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 2 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <p className="ml-16 text-lg font-medium leading-6 text-gray-900">
                                    File-based Routing
                                </p>
                                <p className="mt-2 ml-16 text-base text-gray-500">
                                    Automatic route discovery with support for dynamic routes and API endpoints.
                                </p>
                                <a href="/routing-demo" className="mt-4 ml-16 text-base font-medium text-blue-600 hover:text-blue-500">
                                    Learn more →
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Interactive Demo Section */}
            <div className="py-12 bg-gray-50">
                <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
                    <div className="text-center">
                        <h2 className="text-3xl font-extrabold text-gray-900">
                            Try It Yourself
                        </h2>
                        <p className="max-w-2xl mt-4 text-xl text-gray-500">
                            Interactive demos showing NextPy capabilities
                        </p>
                    </div>
                    
                    <div className="grid grid-cols-1 gap-8 mt-12 sm:grid-cols-2 lg:grid-cols-3">
                        {/* Interactive Counter */}
                        <div className="p-6 bg-white rounded-lg shadow-lg">
                            <h3 className="text-lg font-medium text-gray-900">Live Counter</h3>
                            <p className="mt-2 text-sm text-gray-500">Interactive state management demo</p>
                            <div className="mt-4">
                                <button className="px-4 py-2 text-white transition-colors bg-blue-500 rounded hover:bg-blue-600">
                                    Click me!
                                </button>
                                <span className="ml-4 text-lg font-semibold">Count: 0</span>
                            </div>
                        </div>
                        
                        {/* Form Demo */}
                        <div className="p-6 bg-white rounded-lg shadow-lg">
                            <h3 className="text-lg font-medium text-gray-900">Form Handling</h3>
                            <p className="mt-2 text-sm text-gray-500">Server-side form processing</p>
                            <div className="mt-4">
                                <input type="text" placeholder="Type something..." className="w-full px-3 py-2 border border-gray-300 rounded-md" />
                                <button className="w-full px-4 py-2 mt-2 text-white transition-colors bg-green-500 rounded hover:bg-green-600">
                                    Submit
                                </button>
                            </div>
                        </div>
                        
                        {/* API Demo */}
                        <div className="p-6 bg-white rounded-lg shadow-lg">
                            <h3 className="text-lg font-medium text-gray-900">API Integration</h3>
                            <p className="mt-2 text-sm text-gray-500">RESTful API endpoints</p>
                            <div className="mt-4">
                                <button className="w-full px-4 py-2 text-white transition-colors bg-purple-500 rounded hover:bg-purple-600">
                                    Call API
                                </button>
                                <div className="mt-2 text-xs text-gray-600">Response will appear here</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Footer */}
            <footer className="bg-gray-900">
                <div className="px-4 py-12 mx-auto max-w-7xl sm:px-6 lg:px-8">
                    <div className="flex flex-col items-center space-y-4">
                        <p className="text-base text-center text-gray-400">
                            Built with ❤️ using NextPy Framework
                        </p>
                        <div className="flex space-x-6">
                            <a href="/about" className="text-gray-400 hover:text-gray-300">About</a>
                            <a href="/docs" className="text-gray-400 hover:text-gray-300">Documentation</a>
                            <a href="https://github.com/nextpy/nextpy" className="text-gray-400 hover:text-gray-300">GitHub</a>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    )

def getServerSideProps(context):
    return {
        "props": {
            "title": "Welcome to NextPy!",
            "message": "Build amazing web apps with Python and True JSX"
        }
    }

default = Home
''')
    click.echo("  Created: pages/index.py (interactive homepage)")
    
    # Create enhanced about page with interactive features
    (project_dir / "pages" / "about.py").write_text('''"""Enhanced About page with True JSX"""

def About(props=None):
    """About page component with interactive features"""
    props = props or {}
    
    title = props.get("title", "About NextPy")
    description = props.get("description", "The Python web framework that brings React-like development to Python")
    
    return (
        <div className="min-h-screen bg-gray-50">
            {/* Hero Section */}
            <div className="text-white bg-gradient-to-r from-blue-600 to-purple-600">
                <div className="px-4 py-16 mx-auto max-w-7xl sm:py-24 sm:px-6 lg:px-8">
                    <div className="text-center">
                        <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-6xl">
                            {title}
                        </h1>
                        <p className="max-w-2xl mx-auto mt-6 text-xl text-blue-100">
                            {description}
                        </p>
                        <div className="flex justify-center mt-10 space-x-4">
                            <a href="/features" className="inline-flex items-center justify-center px-8 py-3 text-base font-medium text-blue-600 bg-white border border-transparent rounded-md hover:bg-blue-50 md:py-4 md:text-lg md:px-10">
                                Explore Features
                            </a>
                            <a href="/getting-started" className="inline-flex items-center justify-center px-8 py-3 text-base font-medium text-white bg-blue-500 border border-transparent rounded-md hover:bg-blue-600 md:py-4 md:text-lg md:px-10">
                                Get Started
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Features Grid */}
            <div className="py-12 bg-white">
                <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
                    <div className="lg:text-center">
                        <h2 className="text-base font-semibold tracking-wide text-blue-600 uppercase">
                            Why Choose NextPy?
                        </h2>
                        <p className="mt-2 text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                            Everything you need to build modern web applications
                        </p>
                    </div>
                    
                    <div className="mt-10">
                        <div className="gap-8 space-y-10 md:space-y-0 md:grid md:grid-cols-2 lg:grid-cols-3">
                            {/* Feature 1 */}
                            <div className="relative">
                                <div className="absolute flex items-center justify-center w-12 h-12 text-white bg-blue-500 rounded-md">
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7m0 0v7l9-11h-7z" />
                                    </svg>
                                </div>
                                <h3 className="ml-16 text-lg font-medium leading-6 text-gray-900">True JSX Support</h3>
                                <p className="mt-2 ml-16 text-base text-gray-500">
                                    Write React-like components with JSX syntax directly in Python. No transpilation needed.
                                </p>
                            </div>
                            
                            {/* Feature 2 */}
                            <div className="relative">
                                <div className="absolute flex items-center justify-center w-12 h-12 text-white bg-purple-500 rounded-md">
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
                                    </svg>
                                </div>
                                <h3 className="ml-16 text-lg font-medium leading-6 text-gray-900">File-based Routing</h3>
                                <p className="mt-2 ml-16 text-base text-gray-500">
                                    Automatic route discovery with support for dynamic routes and API endpoints.
                                </p>
                            </div>
                            
                            {/* Feature 3 */}
                            <div className="relative">
                                <div className="absolute flex items-center justify-center w-12 h-12 text-white bg-green-500 rounded-md">
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 2 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <h3 className="ml-16 text-lg font-medium leading-6 text-gray-900">Tailwind CSS Integration</h3>
                                <p className="mt-2 ml-16 text-base text-gray-500">
                                    Built-in Tailwind CSS v4 with PostCSS compilation and utility classes.
                                </p>
                            </div>
                            
                            {/* Feature 4 */}
                            <div className="relative">
                                <div className="absolute flex items-center justify-center w-12 h-12 text-white bg-red-500 rounded-md">
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7m0 0v7l9-11h-7z" />
                                    </svg>
                                </div>
                                <h3 className="ml-16 text-lg font-medium leading-6 text-gray-900">Server-side Rendering</h3>
                                <p className="mt-2 ml-16 text-base text-gray-500">
                                    Fast initial page loads with server-side rendering and data fetching.
                                </p>
                            </div>
                            
                            {/* Feature 5 */}
                            <div className="relative">
                                <div className="absolute flex items-center justify-center w-12 h-12 text-white bg-yellow-500 rounded-md">
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 00-1.065 2.572c1.756.426 1.756 2.924 0 3.35-1.756a1.724 1.724 0 00-1.066-2.573c1.756-.426 1.756-2.924 0-3.35 1.756a1.724 1.724 0 00-2.573-1.066c-1.756.426-1.756-2.924 0-3.35 1.756A1.724 1.724 0 006.573 2.572C3.31 7.76 1.574 8.686 4.317 8.686a1.724 1.724 0 00-1.066-2.572c1.756-.426 1.756-2.924 0-3.35 1.756a1.724 1.724 0 00-2.573-1.066c-1.756.426-1.756-2.924 0-3.35 1.756A1.724 1.724 0 001.066 2.572c1.756.426 1.756 2.924 0 3.35-1.756a1.724 1.724 0 002.573 1.066z" />
                                    </svg>
                                </div>
                                <h3 className="ml-16 text-lg font-medium leading-6 text-gray-900">Hot Reload Development</h3>
                                <p className="mt-2 ml-16 text-base text-gray-500">
                                    Instant hot reload when saving files with Watchdog integration.
                                </p>
                            </div>
                            
                            {/* Feature 6 */}
                            <div className="relative">
                                <div className="absolute flex items-center justify-center w-12 h-12 text-white bg-indigo-500 rounded-md">
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                </div>
                                <h3 className="ml-16 text-lg font-medium leading-6 text-gray-900">API Routes</h3>
                                <p className="mt-2 ml-16 text-base text-gray-500">
                                    Built-in FastAPI support for creating RESTful API endpoints.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Interactive Demo Section */}
            <div className="py-12 bg-gray-50">
                <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
                    <div className="text-center">
                        <h2 className="text-3xl font-extrabold text-gray-900">
                            See It In Action
                        </h2>
                        <p className="max-w-2xl mt-4 text-xl text-gray-500">
                            Try these interactive demos to experience NextPy capabilities
                        </p>
                    </div>
                    
                    <div className="grid grid-cols-1 gap-8 mt-12 sm:grid-cols-2 lg:grid-cols-3">
                        {/* JSX Demo */}
                        <div className="p-6 transition-shadow bg-white rounded-lg shadow-lg hover:shadow-xl">
                            <div className="text-center">
                                <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 text-white bg-blue-500 rounded-md">
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7m0 0v7l9-11h-7z" />
                                    </svg>
                                </div>
                                <h3 className="mb-2 text-lg font-medium text-gray-900">JSX Components</h3>
                                <p className="mb-4 text-sm text-gray-500">Interactive component demo</p>
                                <button onclick="alert('Hello from JSX!')" className="w-full px-4 py-2 text-white transition-colors bg-blue-500 rounded hover:bg-blue-600">
                                    Try JSX Demo
                                </button>
                            </div>
                            
                        {/* Tailwind Demo */}
                        <div className="p-6 transition-shadow bg-white rounded-lg shadow-lg hover:shadow-xl">
                            <div className="text-center">
                                <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 text-white bg-purple-500 rounded-md">
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
                                    </svg>
                                </div>
                                <h3 className="mb-2 text-lg font-medium text-gray-900">Tailwind CSS</h3>
                                <p className="mb-4 text-sm text-gray-500">Beautiful styling with utility classes</p>
                                <button className="w-full px-4 py-2 text-white transition-colors bg-purple-500 rounded hover:bg-purple-600">
                                    Try Tailwind Demo
                                </button>
                            </div>
                            
                        {/* API Demo */}
                        <div className="p-6 transition-shadow bg-white rounded-lg shadow-lg hover:shadow-xl">
                            <div className="text-center">
                                <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 text-white bg-green-500 rounded-md">
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 2 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <h3 className="mb-2 text-lg font-medium text-gray-900">API Integration</h3>
                                <p className="mb-4 text-sm text-gray-500">RESTful API endpoints</p>
                                <button className="w-full px-4 py-2 text-white transition-colors bg-green-500 rounded hover:bg-green-600">
                                    Try API Demo
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Stats Section */}
            <div className="bg-blue-600">
                <div className="px-4 py-12 mx-auto max-w-7xl sm:px-6 lg:px-8">
                    <div className="grid grid-cols-2 gap-8 lg:grid-cols-4">
                        <div className="text-center">
                            <div className="text-3xl font-extrabold text-white">10x</div>
                            <div className="mt-2 text-lg text-blue-200">Faster Development</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl font-extrabold text-white">100%</div>
                            <div className="mt-2 text-lg text-blue-200">Python Compatible</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl font-extrabold text-white">JSX</div>
                            <div className="mt-2 text-lg text-blue-200">Modern Syntax</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl font-extrabold text-white">∞</div>
                            <div className="mt-2 text-lg text-blue-200">Infinite Possibilities</div>
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Footer */}
            <footer className="bg-gray-900">
                <div className="px-4 py-8 mx-auto max-w-7xl sm:px-6 lg:px-8">
                    <div className="flex flex-col items-center space-y-4">
                        <p className="text-base text-center text-gray-400">
                            Built with ❤️ using NextPy Framework
                        </p>
                        <div className="flex space-x-6">
                            <a href="/" className="text-gray-400 hover:text-gray-300">Home</a>
                            <a href="/features" className="text-gray-400 hover:text-gray-300">Features</a>
                            <a href="/docs" className="text-gray-400 hover:text-gray-300">Documentation</a>
                            <a href="https://github.com/nextpy/nextpy" className="text-gray-400 hover:text-gray-300">GitHub</a>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    )

def getServerSideProps(context):
    return {
        "props": {
            "title": "About NextPy",
            "description": "The Python web framework that brings React-like development to Python"
        }
    }

default = About
''')
    click.echo("  Created: pages/about.py (enhanced interactive page)")
    
    # Create interactive demo pages
    (project_dir / "pages" / "interactive.py").write_text('''"""Interactive Demo Page"""

def InteractiveDemo(props=None):
    """Interactive demo showcasing NextPy capabilities"""
    return (
        <div className="min-h-screen py-12 bg-gradient-to-br from-indigo-50 to-purple-100">
            <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
                <h1 className="mb-12 text-4xl font-extrabold text-center text-gray-900">
                    Interactive NextPy Demos
                </h1>
                
                <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
                    {/* Counter Demo */}
                    <div className="p-6 bg-white shadow-lg rounded-xl">
                        <h2 className="mb-4 text-2xl font-bold text-gray-900">Live Counter</h2>
                        <div className="text-center">
                            <div className="mb-4 text-6xl font-bold text-blue-600" id="counter">0</div>
                            <div className="space-x-4">
                                <button onclick="updateCounter(-1)" className="px-6 py-3 text-white transition-colors bg-red-500 rounded-lg hover:bg-red-600">
                                    -
                                </button>
                                <button onclick="updateCounter(1)" className="px-6 py-3 text-white transition-colors bg-green-500 rounded-lg hover:bg-green-600">
                                    +
                                </button>
                                <button onclick="resetCounter()" className="px-6 py-3 text-white transition-colors bg-gray-500 rounded-lg hover:bg-gray-600">
                                    Reset
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    {/* Todo List Demo */}
                    <div className="p-6 bg-white shadow-lg rounded-xl">
                        <h2 className="mb-4 text-2xl font-bold text-gray-900">Todo List</h2>
                        <div className="space-y-4">
                            <div className="flex space-x-2">
                                <input type="text" id="todoInput" placeholder="Add a new todo..." className="flex-1 px-4 py-2 border border-gray-300 rounded-lg" />
                                <button onclick="addTodo()" className="px-6 py-2 text-white transition-colors bg-blue-500 rounded-lg hover:bg-blue-600">
                                    Add
                                </button>
                            </div>
                            <ul id="todoList" className="space-y-2">
                                {/* Todos will be added here dynamically */}
                            </ul>
                        </div>
                    </div>
                    
                    {/* Color Picker Demo */}
                    <div className="p-6 bg-white shadow-lg rounded-xl">
                        <h2 className="mb-4 text-2xl font-bold text-gray-900">Color Picker</h2>
                        <div className="space-y-4">
                            <input type="color" id="colorPicker" className="w-full h-20 rounded-lg cursor-pointer" />
                            <div id="colorDisplay" className="p-4 font-mono text-lg text-center bg-gray-100 rounded-lg">
                                Selected: #3B82F6
                            </div>
                        </div>
                    </div>
                    
                    {/* Form Validation Demo */}
                    <div className="p-6 bg-white shadow-lg rounded-xl">
                        <h2 className="mb-4 text-2xl font-bold text-gray-900">Form Validation</h2>
                        <form onsubmit="validateForm(event)" className="space-y-4">
                            <div>
                                <label className="block mb-2 text-sm font-medium text-gray-700">Email</label>
                                <input type="email" id="email" required className="w-full px-4 py-2 border border-gray-300 rounded-lg" placeholder="you@example.com" />
                            </div>
                            <div>
                                <label className="block mb-2 text-sm font-medium text-gray-700">Password</label>
                                <input type="password" id="password" required minlength="6" className="w-full px-4 py-2 border border-gray-300 rounded-lg" placeholder="•••••••••" />
                            </div>
                            <button type="submit" className="w-full px-6 py-3 text-white transition-colors bg-blue-500 rounded-lg hover:bg-blue-600">
                                Validate & Submit
                            </button>
                        </form>
                        <div id="validationResult" className="hidden p-4 mt-4 rounded-lg">
                            {/* Validation results will appear here */}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )

def getServerSideProps(context):
    return {"props": {}}

default = InteractiveDemo
''')
    click.echo("  Created: pages/interactive.py (interactive demos)")
    
    # Create features page
    (project_dir / "pages" / "features.py").write_text('''"""Features Page"""

def Features(props=None):
    """Comprehensive features showcase"""
    return (
        <div className="min-h-screen bg-gray-50">
            <div className="px-4 py-16 mx-auto max-w-7xl sm:px-6 lg:px-8">
                <div className="mb-16 text-center">
                    <h1 className="text-4xl font-extrabold text-gray-900">
                        NextPy Features
                    </h1>
                    <p className="mt-4 text-xl text-gray-600">
                        Everything you need to build modern web applications
                    </p>
                </div>
                
                <div className="grid grid-cols-1 gap-12 md:grid-cols-2">
                    <div className="space-y-12">
                        {/* Core Features */}
                        <div>
                            <h2 className="mb-6 text-2xl font-bold text-gray-900">Core Features</h2>
                            <div className="space-y-6">
                                <div className="flex items-start space-x-4">
                                    <div className="flex-shrink-0 w-6 h-6 text-green-500">
                                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                        </svg>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium text-gray-900">True JSX Components</h3>
                                        <p className="mt-2 text-gray-600">Write React-like components with JSX syntax directly in Python</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-4">
                                    <div className="flex-shrink-0 w-6 h-6 text-blue-500">
                                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
                                        </svg>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium text-gray-900">File-based Routing</h3>
                                        <p className="mt-2 text-gray-600">Automatic route discovery with dynamic routes support</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-4">
                                    <div className="flex-shrink-0 w-6 h-6 text-purple-500">
                                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 2 9 9 0 0118 0z" />
                                        </svg>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium text-gray-900">Tailwind CSS Integration</h3>
                                        <p className="mt-2 text-gray-600">Built-in Tailwind CSS v4 with PostCSS compilation</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        {/* Development Features */}
                        <div>
                            <h2 className="mb-6 text-2xl font-bold text-gray-900">Development Experience</h2>
                            <div className="space-y-6">
                                <div className="flex items-start space-x-4">
                                    <div className="flex-shrink-0 w-6 h-6 text-red-500">
                                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v16h16V4H4z" />
                                        </svg>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium text-gray-900">Hot Reload</h3>
                                        <p className="mt-2 text-gray-600">Instant hot reload when saving files with Watchdog</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-4">
                                    <div className="flex-shrink-0 w-6 h-6 text-yellow-500">
                                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.75 5H6.25v13l4.5 4.5z" />
                                        </svg>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium text-gray-900">Debug Mode</h3>
                                        <p className="mt-2 text-gray-600">Comprehensive debugging with detailed error pages</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-4">
                                    <div className="flex-shrink-0 w-6 h-6 text-indigo-500">
                                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                        </svg>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-medium text-gray-900">VS Code Integration</h3>
                                        <p className="mt-2 text-gray-600">Full VS Code support with extensions and IntelliSense</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
    )

def getServerSideProps(context):
    return {"props": {}}

default = Features
''')
    click.echo("  Created: pages/features.py (features showcase)")
    
    # Create getting started guide
    (project_dir / "pages" / "getting-started.py").write_text('''"""Getting Started Guide"""

def GettingStarted(props=None):
    """Comprehensive getting started guide"""
    return (
        <div className="min-h-screen bg-white">
            <div className="max-w-4xl px-4 py-16 mx-auto sm:px-6 lg:px-8">
                <div className="mb-16 text-center">
                    <h1 className="text-4xl font-extrabold text-gray-900">
                        Getting Started with NextPy
                    </h1>
                    <p className="mt-4 text-xl text-gray-600">
                        Your journey to building amazing web apps starts here
                    </p>
                </div>
                
                <div className="space-y-16">
                    {/* Step 1 */}
                    <div className="p-8 rounded-lg bg-blue-50">
                        <div className="flex items-center mb-4">
                            <div className="flex items-center justify-center flex-shrink-0 w-8 h-8 font-bold text-white bg-blue-500 rounded-full">
                                1
                            </div>
                            <h2 className="ml-4 text-2xl font-bold text-gray-900">Installation</h2>
                        </div>
                        <div className="ml-12 space-y-4">
                            <div className="p-4 bg-white border-l-4 border-blue-500 rounded">
                                <h3 className="mb-2 font-semibold text-gray-900">Install NextPy</h3>
                                <code className="block p-2 text-sm bg-gray-100 rounded">pip install nextpy-framework</code>
                            </div>
                            <div className="p-4 bg-white border-l-4 border-blue-500 rounded">
                                <h3 className="mb-2 font-semibold text-gray-900">Create New Project</h3>
                                <code className="block p-2 text-sm bg-gray-100 rounded">nextpy create my-app</code>
                            </div>
                        </div>
                    </div>
                    
                    {/* Step 2 */}
                    <div className="p-8 rounded-lg bg-green-50">
                        <div className="flex items-center mb-4">
                            <div className="flex items-center justify-center flex-shrink-0 w-8 h-8 font-bold text-white bg-green-500 rounded-full">
                                2
                            </div>
                            <h2 className="ml-4 text-2xl font-bold text-gray-900">Project Structure</h2>
                        </div>
                        <div className="ml-12">
                            <div className="p-4 bg-white border-l-4 border-green-500 rounded">
                                <h3 className="mb-2 font-semibold text-gray-900">Navigate to Your Project</h3>
                                <code className="block p-2 text-sm bg-gray-100 rounded">cd my-app</code>
                            </div>
                            <div className="p-4 mt-4 bg-white border-l-4 border-green-500 rounded">
                                <h3 className="mb-2 font-semibold text-gray-900">Project Structure</h3>
                                <pre className="p-4 overflow-x-auto text-sm bg-gray-100 rounded">
{`my-app/
├── pages/           # Your pages and API routes
├── components/      # Reusable components  
├── templates/       # HTML templates
├── public/          # Static assets
├── styles.css        # Tailwind CSS
├── main.py          # Application entry point
└── requirements.txt  # Python dependencies`}</pre>
                            </div>
                        </div>
                    </div>
                    
                    {/* Step 3 */}
                    <div className="p-8 rounded-lg bg-purple-50">
                        <div className="flex items-center mb-4">
                            <div className="flex items-center justify-center flex-shrink-0 w-8 h-8 font-bold text-white bg-purple-500 rounded-full">
                                3
                            </div>
                            <h2 className="ml-4 text-2xl font-bold text-gray-900">Development</h2>
                        </div>
                        <div className="ml-12 space-y-4">
                            <div className="p-4 bg-white border-l-4 border-purple-500 rounded">
                                <h3 className="mb-2 font-semibold text-gray-900">Start Development Server</h3>
                                <code className="block p-2 text-sm bg-gray-100 rounded">nextpy dev</code>
                            </div>
                            <div className="p-4 bg-white border-l-4 border-purple-500 rounded">
                                <h3 className="mb-2 font-semibold text-gray-900">Open Your Browser</h3>
                                <code className="block p-2 text-sm bg-gray-100 rounded">http://localhost:8000</code>
                            </div>
                        </div>
                    </div>
                    
                    {/* Step 4 */}
                    <div className="p-8 rounded-lg bg-yellow-50">
                        <div className="flex items-center mb-4">
                            <div className="flex items-center justify-center flex-shrink-0 w-8 h-8 font-bold text-white bg-yellow-500 rounded-full">
                                4
                            </div>
                            <h2 className="ml-4 text-2xl font-bold text-gray-900">Build Your First Component</h2>
                        </div>
                        <div className="ml-12">
                            <div className="p-4 bg-white border-l-4 border-yellow-500 rounded">
                                <h3 className="mb-2 font-semibold text-gray-900">Create a Component</h3>
                                <p className="mb-2 text-gray-600">Edit pages/index.py to create your first JSX component:</p>
                                <pre className="p-4 overflow-x-auto text-sm text-green-400 bg-gray-900 rounded">
{`def Home(props=None):
    return (
        <div className="flex items-center justify-center min-h-screen bg-blue-500">
            <h1 className="text-3xl font-bold text-white">
                Hello, NextPy!
            </h1>
        </div>
    )

default = Home`}</pre>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
    )

def getServerSideProps(context):
    return {"props": {}}

default = GettingStarted
''')
    click.echo("  Created: pages/getting-started.py (comprehensive guide)")
    (project_dir / "components" / "ui" / "Button.py").write_text('''"""Button component"""

def Button(props = None):
    """Reusable Button component"""
    props = props or {}
    
    variant = props.get("variant", "default")
    children = props.get("children", "Button")
    className = props.get("className", "")
    
    if variant == "primary":
        variant_class = "bg-blue-600 text-white hover:bg-blue-700 transform hover:scale-105 transition-all duration-200"
    elif variant == "secondary":
        variant_class = "bg-gray-200 text-gray-900 hover:bg-gray-300 transform hover:scale-105 transition-all duration-200"
    elif variant == "success":
        variant_class = "bg-green-600 text-white hover:bg-green-700 transform hover:scale-105 transition-all duration-200"
    elif variant == "danger":
        variant_class = "bg-red-600 text-white hover:bg-red-700 transform hover:scale-105 transition-all duration-200"
    else:
        variant_class = "bg-gray-600 text-white hover:bg-gray-700 transform hover:scale-105 transition-all duration-200"
    
    class_attr = f"px-6 py-3 rounded-lg font-medium transition-all duration-200 transform hover:scale-105 {variant_class} {className}"
    
    return (
        <button className={class_attr} 
                id={props.get("id")}
                disabled={props.get("disabled", False)}
                onclick={props.get("onClick", "")}>
            {children}
        </button>
    )

default = Button
''')
    click.echo("  Created: components/ui/Button.py (enhanced interactive)")

    
    # Create a Layout component
    (project_dir / "components" / "layout" / "Layout.py").write_text('''"""Layout component"""

def Layout(props = None):
    """Layout component wrapper"""
    props = props or {}
    
    title = props.get("title", "NextPy App")
    children = props.get("children", "")
    
    return (
        <div className="flex flex-col min-h-screen">
            <header className="bg-white shadow-sm">
                <div className="px-4 py-4 mx-auto max-w-7xl">
                    <div className="flex items-center justify-between">
                        <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
                        <nav className="flex space-x-4">
                            <a href="/" className="text-gray-600 hover:text-gray-900">Home</a>
                            <a href="/about" className="text-gray-600 hover:text-gray-900">About</a>
                        </nav>
                    </div>
                </div>
            </header>
            <main className="flex-1">
                {children}
            </main>
            <footer className="mt-auto bg-gray-100">
                <div className="px-4 py-6 mx-auto text-center text-gray-600 max-w-7xl">
                    <p>&copy; 2025 NextPy Framework. All rights reserved.</p>
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
    
    # Create comprehensive API examples
    (project_dir / "pages" / "api" / "hello.py").write_text('''"""API example - Hello endpoint"""

from fastapi import Request

async def get(request: Request):
    """GET /api/hello"""
    return {"message": "Hello from NextPy API!", "status": "success"}

async def post(request: Request):
    """POST /api/hello"""
    data = await request.json()
    return {"message": "POST request received", "data": data, "status": "success"}
''')
    click.echo("  Created: pages/api/hello.py")
    
    (project_dir / "pages" / "api" / "users" / "index.py").write_text('''"""API example - Users index"""

from fastapi import Request

async def get(request: Request):
    """GET /api/users - List all users"""
    users = [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
    ]
    return {"users": users, "total": len(users)}

async def post(request: Request):
    """POST /api/users - Create new user"""
    data = await request.json()
    # In a real app, you'd save to database
    new_user = {
        "id": 3,
        "name": data.get("name"),
        "email": data.get("email")
    }
    return {"user": new_user, "message": "User created successfully"}
''')
    click.echo("  Created: pages/api/users/index.py")
    
    (project_dir / "pages" / "api" / "users" / "[id].py").write_text('''"""API example - Dynamic user route"""

from fastapi import Request

async def get(request: Request, id: int):
    """GET /api/users/{id} - Get user by ID"""
    users = {
        1: {"id": 1, "name": "John Doe", "email": "john@example.com"},
        2: {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
    }
    
    if id in users:
        return {"user": users[id]}
    else:
        return {"error": "User not found"}, 404

async def put(request: Request, id: int):
    """PUT /api/users/{id} - Update user"""
    data = await request.json()
    return {"message": f"User {id} updated", "data": data}

async def delete(request: Request, id: int):
    """DELETE /api/users/{id} - Delete user"""
    return {"message": f"User {id} deleted successfully"}
''')
    click.echo("  Created: pages/api/users/[id].py")
    
    # Create database models
    (project_dir / "models" / "User.py").write_text('''"""User model example"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
''')
    click.echo("  Created: models/User.py")
    
    # Create utility functions
    (project_dir / "utils" / "helpers.py").write_text('''"""Utility helper functions"""

import hashlib
import secrets
from datetime import datetime

def generate_secret_key(length: int = 32) -> str:
    """Generate a secure secret key"""
    return secrets.token_urlsafe(length)

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def format_date(date: datetime) -> str:
    """Format datetime for display"""
    return date.strftime("%B %d, %Y at %I:%M %p")

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    return text.lower().replace(" ", "-").replace("_", "-")
''')
    click.echo("  Created: utils/helpers.py")
    
    # Create custom hooks
    (project_dir / "hooks" / "use_auth.py").write_text('''"""Authentication hook example"""

def use_auth(request):
    """Example authentication hook"""
    # In a real app, you'd check tokens, sessions, etc.
    auth_header = request.headers.get("authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        # Validate token here
        return {"user": {"id": 1, "name": "Authenticated User"}, "token": token}
    
    return {"user": None, "error": "No authentication provided"}
''')
    click.echo("  Created: hooks/use_auth.py")
    
    # Create middleware example
    (project_dir / "middleware" / "cors.py").write_text('''"""CORS middleware example"""

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware

def add_cors_middleware(app):
    """Add CORS middleware to the app"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
''')
    click.echo("  Created: middleware/cors.py")
    
    # Create test files
    (project_dir / "tests" / "test_api.py").write_text('''"""API tests example"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_hello_api():
    """Test the hello API endpoint"""
    response = client.get("/api/hello")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello from NextPy API!"
    assert data["status"] == "success"

def test_users_api():
    """Test the users API endpoint"""
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert len(data["users"]) == data["total"]
''')
    click.echo("  Created: tests/test_api.py")
    
    # Create documentation
    (project_dir / "docs" / "README.md").write_text('''# Project Documentation

## Overview
This is a NextPy application with True JSX, Tailwind CSS, and comprehensive API support.

## Features
- ✅ True JSX components in Python
- ✅ Tailwind CSS integration
- ✅ File-based routing
- ✅ API routes with FastAPI
- ✅ Database models with SQLAlchemy
- ✅ Authentication hooks
- ✅ CORS middleware
- ✅ Comprehensive testing

## Project Structure
```
├── pages/           # File-based routing
│   ├── api/        # API routes
│   └── *.py        # Page components
├── components/      # Reusable components
├── templates/       # HTML templates
├── models/         # Database models
├── utils/          # Utility functions
├── hooks/          # Custom hooks
├── middleware/     # Custom middleware
├── tests/          # Test files
├── public/         # Static assets
├── styles/         # CSS files
└── docs/           # Documentation
```

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Install Node.js deps: `npm install`
3. Run development server: `nextpy dev`
4. Open http://localhost:8000

## API Endpoints
- `GET /api/hello` - Hello message
- `GET /api/users` - List users
- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user by ID
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
''')
    click.echo("  Created: docs/README.md")
    
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
    
    # Create main.py with Tailwind compilation (for pip-installed NextPy)
    (project_dir / "main.py").write_text('''"""NextPy ASGI Application Entry Point"""

import os
import sys
import subprocess
from pathlib import Path

print(f"DEBUG: Current working directory: {Path.cwd()}")
print(f"DEBUG: sys.path before modification: {sys.path}")

# Compile Tailwind CSS using PostCSS
try:
    print("Compiling Tailwind CSS...")
    # Use PostCSS with new Tailwind plugin
    result = subprocess.run(
        ["./node_modules/.bin/postcss", "styles.css", "-o", "public/tailwind.css"], 
        capture_output=True, 
        text=True,
        check=True
    )
    print("Tailwind CSS compiled successfully.")
    if result.stdout:
        print(f"CSS Output: {result.stdout[:200]}...")
except subprocess.CalledProcessError as e:
    print(f"Error compiling Tailwind CSS: {e}")
    if e.stderr:
        print(f"CSS Error: {e.stderr}")
except FileNotFoundError:
    print("Error: PostCSS not found. Make sure Node.js and Tailwind CSS are installed.")
    print("Install with: npm install postcss-cli @tailwindcss/postcss")

# Import NextPy modules (works when installed via pip)
from nextpy.server.app import create_app
from nextpy.db import init_db
from nextpy.config import settings

# Initialize database
try:
    init_db(settings["database_url"])
    print("Database initialized successfully.")
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")

# Create NextPy app with file-based routing
app = create_app(
    pages_dir="pages",
    templates_dir="templates", 
    public_dir="public",
    out_dir="out",
    debug=settings["debug"],
)

# Note: Routes are automatically loaded from pages/ directory
# - / -> pages/index.py
# - /about -> pages/about.py  
# - /api/* -> pages/api/*.py

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
''')
    click.echo("  Created: main.py (pip-compatible)")
    
    # Create .env file for development
    (project_dir / ".env").write_text('''# NextPy Development Environment
DEVELOPMENT=true
DEBUG=true
NEXTPY_DEBUG=true

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database (if needed)
DATABASE_URL=sqlite:///./app.db

# Secret Key
SECRET_KEY=your-secret-key-here

# NextPy Settings
NEXTPY_DEBUG_ICON=true
NEXTPY_HOT_RELOAD=true
NEXTPY_LOG_LEVEL=info
''')
    click.echo("  Created: .env")
    
    # Install Node.js dependencies
    try:
        import subprocess
        import sys
        
        click.echo(click.style("  📦 Installing Node.js dependencies...", fg="blue"))
        result = subprocess.run(
            ["npm", "install"], 
            cwd=project_dir,
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            click.echo(click.style("  ✅ Node.js dependencies installed", fg="green"))
        else:
            click.echo(click.style("  ⚠️  npm install failed", fg="yellow"))
            click.echo("  💡 Run manually: npm install")
            
    except FileNotFoundError:
        click.echo(click.style("  ⚠️  npm not found", fg="yellow"))
        click.echo("  💡 Install Node.js: https://nodejs.org/")
    except Exception as e:
        click.echo(click.style(f"  ⚠️  Could not install Node.js deps: {e}", fg="yellow"))
    
    # Install Python dependencies
    try:
        click.echo(click.style("  🐍 Installing Python dependencies...", fg="blue"))
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
            cwd=project_dir,
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            click.echo(click.style("  ✅ Python dependencies installed", fg="green"))
        else:
            click.echo(click.style("  ⚠️  pip install failed", fg="yellow"))
            click.echo("  💡 Run manually: pip install -r requirements.txt")
            
    except Exception as e:
        click.echo(click.style(f"  ⚠️  Could not install Python deps: {e}", fg="yellow"))
    try:
        import sys
        import subprocess
        from pathlib import Path
        
        # Check if VS Code is available
        result = subprocess.run([sys.executable, "-c", "import vscode"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            extension_id = "nextpy.nextpy-vscode"
            
            # Check if extension is already installed
            check_cmd = ["code", "--list-extensions", "--show-versions", extension_id]
            check_result = subprocess.run(check_cmd, capture_output=True, text=True)
            
            if extension_id not in check_result.stdout:
                click.echo(click.style("  🔌 Installing NextPy VS Code extension...", fg="blue"))
                
                # Try to install from marketplace
                install_cmd = ["code", "--install-extension", extension_id]
                install_result = subprocess.run(install_cmd, capture_output=True, text=True)
                
                if install_result.returncode == 0:
                    click.echo(click.style("  ✅ NextPy VS Code extension installed!", fg="green"))
                    click.echo(click.style("  📝 Restart VS Code to activate", fg="yellow"))
                else:
                    click.echo(click.style("  ⚠️  Extension installation failed", fg="yellow"))
                    click.echo("  💡 Install manually: code --install-extension nextpy.nextpy-vscode")
            else:
                click.echo(click.style("  ✅ NextPy VS Code extension already installed", fg="green"))
        else:
            click.echo(click.style("  ⚠️  VS Code not available", fg="yellow"))
    except Exception as e:
        click.echo(click.style(f"  ⚠️  Could not install VS Code extension: {e}", fg="yellow"))




if __name__ == "__main__":
    cli()