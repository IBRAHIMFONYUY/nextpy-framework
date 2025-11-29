"""
NextPy Head Component - SEO and meta tag management
Similar to Next.js's next/head
"""

from typing import Any, Dict, List, Optional
from markupsafe import Markup


class Head:
    """
    Head component for managing document head elements
    
    Usage in templates:
        {{ Head(title="My Page", description="Page description") }}
    
    Or in Python:
        head = Head(title="My Page")
        head.add_meta(name="author", content="John Doe")
        print(head.render())
    """
    
    def __init__(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        canonical: Optional[str] = None,
        og_title: Optional[str] = None,
        og_description: Optional[str] = None,
        og_image: Optional[str] = None,
        og_type: str = "website",
        twitter_card: str = "summary_large_image",
        favicon: Optional[str] = None,
        **kwargs: Any,
    ):
        self.title = title
        self.description = description
        self.keywords = keywords or []
        self.canonical = canonical
        self.og_title = og_title or title
        self.og_description = og_description or description
        self.og_image = og_image
        self.og_type = og_type
        self.twitter_card = twitter_card
        self.favicon = favicon
        self.extra_meta: List[Dict[str, str]] = []
        self.extra_links: List[Dict[str, str]] = []
        self.extra_scripts: List[Dict[str, str]] = []
        self.extra_kwargs = kwargs
        
    def add_meta(self, **attrs: str) -> "Head":
        """Add a custom meta tag"""
        self.extra_meta.append(attrs)
        return self
        
    def add_link(self, **attrs: str) -> "Head":
        """Add a custom link tag"""
        self.extra_links.append(attrs)
        return self
        
    def add_script(self, src: Optional[str] = None, **attrs: str) -> "Head":
        """Add a script tag"""
        if src:
            attrs["src"] = src
        self.extra_scripts.append(attrs)
        return self
        
    def render(self) -> str:
        """Render the head elements as HTML"""
        elements = []
        
        if self.title:
            elements.append(f"<title>{self._escape(self.title)}</title>")
            
        elements.append('<meta charset="UTF-8">')
        elements.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        
        if self.description:
            elements.append(
                f'<meta name="description" content="{self._escape(self.description)}">'
            )
            
        if self.keywords:
            keywords_str = ", ".join(self.keywords)
            elements.append(f'<meta name="keywords" content="{self._escape(keywords_str)}">')
            
        if self.canonical:
            elements.append(f'<link rel="canonical" href="{self._escape(self.canonical)}">')
            
        if self.og_title:
            elements.append(f'<meta property="og:title" content="{self._escape(self.og_title)}">')
        if self.og_description:
            elements.append(
                f'<meta property="og:description" content="{self._escape(self.og_description)}">'
            )
        if self.og_image:
            elements.append(f'<meta property="og:image" content="{self._escape(self.og_image)}">')
        if self.og_type:
            elements.append(f'<meta property="og:type" content="{self._escape(self.og_type)}">')
            
        if self.twitter_card:
            elements.append(f'<meta name="twitter:card" content="{self._escape(self.twitter_card)}">')
        if self.og_title:
            elements.append(
                f'<meta name="twitter:title" content="{self._escape(self.og_title)}">'
            )
        if self.og_description:
            elements.append(
                f'<meta name="twitter:description" content="{self._escape(self.og_description)}">'
            )
        if self.og_image:
            elements.append(
                f'<meta name="twitter:image" content="{self._escape(self.og_image)}">'
            )
            
        if self.favicon:
            elements.append(f'<link rel="icon" href="{self._escape(self.favicon)}">')
            
        for meta in self.extra_meta:
            attrs_str = " ".join(f'{k}="{self._escape(v)}"' for k, v in meta.items())
            elements.append(f"<meta {attrs_str}>")
            
        for link in self.extra_links:
            attrs_str = " ".join(f'{k}="{self._escape(v)}"' for k, v in link.items())
            elements.append(f"<link {attrs_str}>")
            
        for script in self.extra_scripts:
            attrs_str = " ".join(f'{k}="{self._escape(v)}"' for k, v in script.items())
            if "src" in script:
                elements.append(f"<script {attrs_str}></script>")
            else:
                content = script.pop("content", "")
                elements.append(f"<script {attrs_str}>{content}</script>")
                
        return "\n    ".join(elements)
        
    def __html__(self) -> str:
        """Make the component work with Jinja2's autoescape"""
        return self.render()
        
    def __str__(self) -> str:
        return self.render()
        
    def __call__(self, **kwargs: Any) -> Markup:
        """Allow calling Head() in templates with additional args"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return Markup(self.render())
        
    @staticmethod
    def _escape(value: str) -> str:
        """Escape HTML special characters"""
        return (
            str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )


def create_head(**kwargs: Any) -> Head:
    """Factory function to create a Head component"""
    return Head(**kwargs)
