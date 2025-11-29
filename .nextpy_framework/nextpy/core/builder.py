"""
NextPy Builder - Static Site Generation (SSG)
Builds static HTML files to the out/ directory
"""

import os
import shutil
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from nextpy.core.router import Router, Route
from nextpy.core.renderer import Renderer
from nextpy.core.data_fetching import (
    PageContext,
    PropsResult,
    execute_data_fetching,
    get_static_paths_for_route,
)


class Builder:
    """
    Static Site Generator for NextPy
    Builds all pages to static HTML in the out/ directory
    """
    
    def __init__(
        self,
        pages_dir: str = "pages",
        templates_dir: str = "templates",
        public_dir: str = "public",
        out_dir: str = "out",
    ):
        self.pages_dir = Path(pages_dir)
        self.templates_dir = Path(templates_dir)
        self.public_dir = Path(public_dir)
        self.out_dir = Path(out_dir)
        
        self.router = Router(pages_dir, templates_dir)
        self.renderer = Renderer(templates_dir, pages_dir, public_dir)
        
        self.build_manifest: Dict[str, Any] = {
            "version": 1,
            "pages": {},
            "build_time": None,
        }
        
    async def build(self, clean: bool = True) -> Dict[str, Any]:
        """
        Build all pages to static HTML
        
        Args:
            clean: Whether to clean the output directory first
            
        Returns:
            Build manifest with information about built pages
        """
        print("NextPy Build Starting...")
        start_time = datetime.now()
        
        if clean and self.out_dir.exists():
            shutil.rmtree(self.out_dir)
            
        self.out_dir.mkdir(parents=True, exist_ok=True)
        
        self._copy_public_files()
        
        self.router.scan_pages()
        
        await self._build_static_routes()
        
        await self._build_dynamic_routes()
        
        self._create_sitemap()
        
        self.build_manifest["build_time"] = datetime.now().isoformat()
        self._write_manifest()
        
        duration = (datetime.now() - start_time).total_seconds()
        print(f"\nBuild completed in {duration:.2f}s")
        print(f"Output directory: {self.out_dir}")
        
        return self.build_manifest
        
    def _copy_public_files(self) -> None:
        """Copy files from public/ to out/"""
        if not self.public_dir.exists():
            return
            
        for item in self.public_dir.rglob("*"):
            if item.is_file():
                relative = item.relative_to(self.public_dir)
                dest = self.out_dir / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
                
        print(f"Copied public files to {self.out_dir}")
        
    async def _build_static_routes(self) -> None:
        """Build all static (non-dynamic) routes"""
        static_routes = self.router.get_static_routes()
        
        for route in static_routes:
            if route.is_api:
                continue
                
            await self._build_page(route)
            
    async def _build_dynamic_routes(self) -> None:
        """Build dynamic routes using getStaticPaths"""
        dynamic_routes = [r for r in self.router.routes if r.is_dynamic]
        
        for route in dynamic_routes:
            if route.is_api:
                continue
                
            if route.handler:
                module = self._get_module_from_handler(route.handler)
                if module:
                    paths_result = await get_static_paths_for_route(module)
                    
                    for path_config in paths_result.paths:
                        params = path_config.get("params", path_config)
                        await self._build_page(route, params)
                        
    async def _build_page(
        self, 
        route: Route, 
        params: Optional[Dict[str, str]] = None
    ) -> None:
        """Build a single page to static HTML"""
        params = params or {}
        
        path = self._resolve_path(route.path, params)
        
        context = PageContext(
            params=params,
            query={},
        )
        
        try:
            props = {}
            if route.handler:
                module = self._get_module_from_handler(route.handler)
                if module:
                    props = await execute_data_fetching(module, context)
                    
            template_name = self._get_template_for_route(route)
            
            html = await self.renderer.render_async(
                template_name,
                context={**props, "params": params},
            )
            
            output_path = self._get_output_path(path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html)
            
            self.build_manifest["pages"][path] = {
                "file": str(output_path),
                "params": params,
            }
            
            print(f"  Built: {path} -> {output_path}")
            
        except Exception as e:
            print(f"  Error building {path}: {e}")
            
    def _resolve_path(self, route_path: str, params: Dict[str, str]) -> str:
        """Resolve a dynamic route path with actual params"""
        path = route_path
        for key, value in params.items():
            path = path.replace(f"(?P<{key}>[^/]+)", value)
            path = path.replace(f"(?P<{key}>.+)", value)
        return path
        
    def _get_template_for_route(self, route: Route) -> str:
        """Get the template name for a route"""
        relative = route.file_path.relative_to(self.pages_dir)
        template_name = str(relative).replace(".py", ".html")
        
        template_path = self.templates_dir / template_name
        if template_path.exists():
            return template_name
            
        return "_page.html"
        
    def _get_output_path(self, path: str) -> Path:
        """Get the output file path for a URL path"""
        if path == "/":
            return self.out_dir / "index.html"
            
        clean_path = path.strip("/")
        return self.out_dir / clean_path / "index.html"
        
    def _get_module_from_handler(self, handler: Any) -> Optional[Any]:
        """Get the module that contains the handler"""
        if hasattr(handler, "__module__"):
            import sys
            return sys.modules.get(handler.__module__)
        return None
        
    def _create_sitemap(self) -> None:
        """Generate sitemap.xml"""
        pages = self.build_manifest["pages"]
        
        sitemap_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]
        
        for path in pages:
            sitemap_lines.append(f"  <url>")
            sitemap_lines.append(f"    <loc>{path}</loc>")
            sitemap_lines.append(f"    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>")
            sitemap_lines.append(f"  </url>")
            
        sitemap_lines.append("</urlset>")
        
        sitemap_path = self.out_dir / "sitemap.xml"
        sitemap_path.write_text("\n".join(sitemap_lines))
        print(f"  Generated: sitemap.xml")
        
    def _write_manifest(self) -> None:
        """Write the build manifest to the output directory"""
        import json
        manifest_path = self.out_dir / "_nextpy" / "build-manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(self.build_manifest, indent=2))


async def build_project(**kwargs) -> Dict[str, Any]:
    """Convenience function to build the project"""
    builder = Builder(**kwargs)
    return await builder.build()
