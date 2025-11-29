"""
NextPy Renderer - Server-side rendering with Jinja2
Handles template rendering, layouts, and component composition
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, List
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from markupsafe import Markup

from nextpy.components.head import Head
from nextpy.components.link import Link


class Renderer:
    """
    Server-side renderer using Jinja2
    Supports layouts, components, and template inheritance
    """
    
    def __init__(
        self, 
        templates_dir: str = "templates",
        pages_dir: str = "pages",
        public_dir: str = "public"
    ):
        self.templates_dir = Path(templates_dir)
        self.pages_dir = Path(pages_dir)
        self.public_dir = Path(public_dir)
        
        loader = FileSystemLoader([
            str(self.templates_dir),
            str(self.pages_dir),
        ])
        
        self.env = Environment(
            loader=loader,
            autoescape=select_autoescape(["html", "xml"]),
            enable_async=True,
        )
        
        self._register_globals()
        self._register_filters()
        
    def _register_globals(self) -> None:
        """Register global functions and components available in templates"""
        self.env.globals["Head"] = Head
        self.env.globals["Link"] = Link
        self.env.globals["Markup"] = Markup
        
        self.env.globals["range"] = range
        self.env.globals["len"] = len
        self.env.globals["str"] = str
        self.env.globals["int"] = int
        self.env.globals["list"] = list
        self.env.globals["dict"] = dict
        self.env.globals["enumerate"] = enumerate
        
    def _register_filters(self) -> None:
        """Register custom Jinja2 filters"""
        self.env.filters["json"] = self._json_filter
        self.env.filters["date"] = self._date_filter
        self.env.filters["truncate_words"] = self._truncate_words_filter
        
    @staticmethod
    def _json_filter(value: Any) -> str:
        """Convert value to JSON string"""
        import json
        return json.dumps(value)
        
    @staticmethod
    def _date_filter(value: Any, format_str: str = "%Y-%m-%d") -> str:
        """Format a date value"""
        from datetime import datetime
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if hasattr(value, "strftime"):
            return value.strftime(format_str)
        return str(value)
        
    @staticmethod
    def _truncate_words_filter(value: str, num_words: int = 20) -> str:
        """Truncate text to a number of words"""
        words = value.split()
        if len(words) <= num_words:
            return value
        return " ".join(words[:num_words]) + "..."
        
    def render(
        self,
        template_name: str,
        context: Optional[Dict[str, Any]] = None,
        layout: Optional[str] = None,
    ) -> str:
        """
        Render a template with the given context
        
        Args:
            template_name: Name of the template file
            context: Dictionary of variables to pass to template
            layout: Optional layout template to wrap the content
            
        Returns:
            Rendered HTML string
        """
        context = context or {}
        
        context.setdefault("__page__", template_name)
        context.setdefault("__layout__", layout)
        
        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound:
            template_path = self._find_template(template_name)
            if template_path:
                template = self.env.get_template(str(template_path))
            else:
                raise
                
        content = template.render(**context)
        
        if layout:
            try:
                layout_template = self.env.get_template(layout)
                content = layout_template.render(content=Markup(content), **context)
            except TemplateNotFound:
                pass
                
        return content
        
    async def render_async(
        self,
        template_name: str,
        context: Optional[Dict[str, Any]] = None,
        layout: Optional[str] = None,
    ) -> str:
        """Async version of render"""
        context = context or {}
        
        context.setdefault("__page__", template_name)
        context.setdefault("__layout__", layout)
        
        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound:
            template_path = self._find_template(template_name)
            if template_path:
                template = self.env.get_template(str(template_path))
            else:
                raise
                
        content = await template.render_async(**context)
        
        if layout:
            try:
                layout_template = self.env.get_template(layout)
                content = await layout_template.render_async(
                    content=Markup(content), 
                    **context
                )
            except TemplateNotFound:
                pass
                
        return content
        
    def _find_template(self, template_name: str) -> Optional[Path]:
        """Find a template by searching in multiple locations"""
        search_paths = [
            self.templates_dir / template_name,
            self.templates_dir / f"{template_name}.html",
            self.templates_dir / f"{template_name}.jinja2",
        ]
        
        for path in search_paths:
            if path.exists():
                return path.relative_to(self.templates_dir)
                
        return None
        
    def render_component(
        self, 
        component_func: callable,
        props: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Render a Python component function
        Components are functions that return HTML strings
        """
        props = props or {}
        result = component_func(**props)
        
        if isinstance(result, str):
            return result
        elif hasattr(result, "__html__"):
            return result.__html__()
        else:
            return str(result)
            
    def render_page(
        self,
        page_module: Any,
        context: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Render a page module (from pages/ directory)
        
        The page module can have:
        - A template() function returning HTML
        - A Page component class
        - A get_template() function returning template name
        """
        context = context or {}
        params = params or {}
        
        context["params"] = params
        
        if hasattr(page_module, "template"):
            return page_module.template(**context)
            
        if hasattr(page_module, "Page"):
            return self.render_component(page_module.Page, context)
            
        if hasattr(page_module, "get_template"):
            template_name = page_module.get_template()
            return self.render(template_name, context)
            
        page_name = getattr(page_module, "__name__", "page")
        template_name = f"{page_name}.html"
        return self.render(template_name, context)
        
    def get_layout_chain(self, page_path: Path) -> List[str]:
        """
        Get the chain of layouts for a page
        Similar to Next.js app router layouts
        """
        layouts = []
        current = page_path.parent
        
        while current != self.pages_dir.parent:
            layout_file = current / "_layout.html"
            if layout_file.exists():
                layouts.append(str(layout_file.relative_to(self.templates_dir)))
            current = current.parent
            
        layouts.reverse()
        
        if (self.templates_dir / "_base.html").exists():
            layouts.insert(0, "_base.html")
            
        return layouts
