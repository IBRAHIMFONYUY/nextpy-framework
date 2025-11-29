"""
NextPy Image Component - Optimized image handling
Similar to Next.js's next/image with automatic optimization
"""

from typing import Any, List, Optional, Tuple
from pathlib import Path
from markupsafe import Markup


class Image:
    """
    Optimized Image component with automatic sizing and lazy loading
    
    Usage in templates:
        {{ Image("/images/hero.jpg", alt="Hero image", width=800, height=600) }}
    
    Features:
        - Automatic srcset generation for responsive images
        - Lazy loading by default
        - Placeholder blur support
        - Size optimization hints
    """
    
    DEFAULT_SIZES = [640, 750, 828, 1080, 1200, 1920, 2048, 3840]
    DEFAULT_QUALITY = 75
    
    def __init__(
        self,
        src: str,
        alt: str = "",
        width: Optional[int] = None,
        height: Optional[int] = None,
        layout: str = "intrinsic",
        priority: bool = False,
        placeholder: str = "empty",
        blur_data_url: Optional[str] = None,
        quality: int = DEFAULT_QUALITY,
        sizes: Optional[str] = None,
        class_: Optional[str] = None,
        style: Optional[str] = None,
        **kwargs: Any,
    ):
        self.src = src
        self.alt = alt
        self.width = width
        self.height = height
        self.layout = layout
        self.priority = priority
        self.placeholder = placeholder
        self.blur_data_url = blur_data_url
        self.quality = quality
        self.sizes = sizes
        self.class_ = class_
        self.style = style
        self.extra_attrs = kwargs
        
    def render(self) -> str:
        """Render the image as an optimized HTML img tag"""
        attrs = []
        
        if self._is_external_url():
            attrs.append(f'src="{self._escape(self.src)}"')
        else:
            attrs.append(f'src="{self._escape(self._get_optimized_url())}"')
            srcset = self._generate_srcset()
            if srcset:
                attrs.append(f'srcset="{srcset}"')
                
        attrs.append(f'alt="{self._escape(self.alt)}"')
        
        if self.width:
            attrs.append(f'width="{self.width}"')
        if self.height:
            attrs.append(f'height="{self.height}"')
            
        if self.sizes:
            attrs.append(f'sizes="{self._escape(self.sizes)}"')
        elif self.width:
            attrs.append(f'sizes="(max-width: {self.width}px) 100vw, {self.width}px"')
            
        if not self.priority:
            attrs.append('loading="lazy"')
            attrs.append('decoding="async"')
        else:
            attrs.append('fetchpriority="high"')
            
        if self.placeholder == "blur" and self.blur_data_url:
            attrs.append(f'style="background-image: url({self.blur_data_url}); background-size: cover;"')
        elif self.style:
            attrs.append(f'style="{self._escape(self.style)}"')
            
        if self.class_:
            attrs.append(f'class="{self._escape(self.class_)}"')
            
        for key, value in self.extra_attrs.items():
            attr_name = key.replace("_", "-")
            if value is True:
                attrs.append(attr_name)
            elif value is not False and value is not None:
                attrs.append(f'{attr_name}="{self._escape(str(value))}"')
                
        wrapper_style = self._get_wrapper_style()
        img_tag = f"<img {' '.join(attrs)}>"
        
        if wrapper_style:
            return f'<span style="{wrapper_style}">{img_tag}</span>'
        return img_tag
        
    def _is_external_url(self) -> bool:
        """Check if the src is an external URL"""
        return self.src.startswith(("http://", "https://", "//"))
        
    def _get_optimized_url(self) -> str:
        """Get the optimized image URL"""
        return f"/_nextpy/image?url={self.src}&w={self.width or 0}&q={self.quality}"
        
    def _generate_srcset(self) -> str:
        """Generate srcset for responsive images"""
        if self._is_external_url():
            return ""
            
        srcset_parts = []
        max_width = self.width or 1920
        
        for size in self.DEFAULT_SIZES:
            if size <= max_width * 2:
                url = f"/_nextpy/image?url={self.src}&w={size}&q={self.quality}"
                srcset_parts.append(f"{url} {size}w")
                
        return ", ".join(srcset_parts)
        
    def _get_wrapper_style(self) -> str:
        """Get wrapper style based on layout mode"""
        if self.layout == "fill":
            return "display: block; overflow: hidden; position: absolute; inset: 0;"
        elif self.layout == "responsive" and self.width and self.height:
            aspect = (self.height / self.width) * 100
            return f"display: block; overflow: hidden; position: relative; padding-bottom: {aspect:.2f}%;"
        elif self.layout == "intrinsic" and self.width and self.height:
            return f"display: inline-block; max-width: 100%; width: {self.width}px;"
        return ""
        
    def __html__(self) -> str:
        """Make the component work with Jinja2's autoescape"""
        return self.render()
        
    def __str__(self) -> str:
        return self.render()
        
    def __call__(self, **kwargs: Any) -> Markup:
        """Allow calling Image() in templates with arguments"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.extra_attrs[key] = value
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


def image(src: str, alt: str = "", **kwargs: Any) -> Markup:
    """
    Functional helper to create an Image
    
    Usage in templates:
        {{ image("/hero.jpg", "Hero", width=800) }}
    """
    return Markup(Image(src, alt, **kwargs).render())
