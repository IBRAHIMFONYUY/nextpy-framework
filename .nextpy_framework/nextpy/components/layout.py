"""
Layout components for NextPy
Provides grid, flex, container, and other layout utilities
"""

from typing import Optional, List, Dict, Any


def Container(
    children: str = "",
    max_width: str = "max-w-6xl",
    padding: str = "px-4 sm:px-6 lg:px-8",
    **kwargs
) -> str:
    """Container component with responsive max-width"""
    classes = f"mx-auto {max_width} {padding}"
    return f'<div class="{classes}">{children}</div>'


def Grid(
    children: str = "",
    columns: int = 3,
    gap: str = "gap-6",
    responsive: bool = True,
    **kwargs
) -> str:
    """Grid layout component"""
    if responsive:
        cols = f"md:grid-cols-{columns}"
        classes = f"grid {cols} {gap}"
    else:
        cols = f"grid-cols-{columns}"
        classes = f"grid {cols} {gap}"
    
    return f'<div class="{classes}">{children}</div>'


def Flex(
    children: str = "",
    direction: str = "row",
    justify: str = "justify-start",
    align: str = "items-start",
    gap: str = "gap-4",
    **kwargs
) -> str:
    """Flex layout component"""
    flex_dir = "flex-col" if direction == "column" else "flex-row"
    classes = f"flex {flex_dir} {justify} {align} {gap}"
    return f'<div class="{classes}">{children}</div>'


def Stack(
    children: str = "",
    direction: str = "vertical",
    spacing: str = "space-y-4",
    **kwargs
) -> str:
    """Stack component (vertical or horizontal)"""
    if direction == "horizontal":
        spacing = spacing.replace("space-y", "space-x")
        classes = f"flex flex-row {spacing}"
    else:
        classes = f"flex flex-col {spacing}"
    
    return f'<div class="{classes}">{children}</div>'


def Section(
    children: str = "",
    title: Optional[str] = None,
    bg_color: str = "bg-white",
    padding: str = "py-16",
    **kwargs
) -> str:
    """Section component with optional title"""
    html = f'<section class="{bg_color} {padding}"><div class="max-w-6xl mx-auto px-4">'
    
    if title:
        html += f'<h2 class="text-3xl font-bold mb-8">{title}</h2>'
    
    html += children + '</div></section>'
    return html


def Row(
    children: str = "",
    gap: str = "gap-4",
    **kwargs
) -> str:
    """Row component (horizontal flex)"""
    return f'<div class="flex flex-row {gap}">{children}</div>'


def Column(
    children: str = "",
    gap: str = "gap-4",
    **kwargs
) -> str:
    """Column component (vertical flex)"""
    return f'<div class="flex flex-col {gap}">{children}</div>'


def AspectRatio(
    children: str = "",
    ratio: str = "16/9",
    **kwargs
) -> str:
    """AspectRatio component"""
    ratio_class = {
        "1/1": "aspect-square",
        "4/3": "aspect-video",
        "16/9": "aspect-video",
        "3/2": "aspect-video",
    }.get(ratio, "aspect-video")
    
    return f'<div class="{ratio_class} overflow-hidden">{children}</div>'


def Spacer(height: str = "h-4", **kwargs) -> str:
    """Spacer component for vertical spacing"""
    return f'<div class="{height}"></div>'


def Divider(
    color: str = "border-gray-200",
    **kwargs
) -> str:
    """Divider/separator component"""
    return f'<hr class="border {color}">'


def Center(
    children: str = "",
    **kwargs
) -> str:
    """Center component"""
    return f'<div class="flex items-center justify-center">{children}</div>'


def Sidebar(
    children: str = "",
    sidebar_content: str = "",
    sidebar_width: str = "w-64",
    **kwargs
) -> str:
    """Sidebar layout component"""
    return f'''
    <div class="flex gap-6">
        <aside class="{sidebar_width} flex-shrink-0">
            {sidebar_content}
        </aside>
        <main class="flex-1">
            {children}
        </main>
    </div>
    '''


def TwoColumn(
    left: str = "",
    right: str = "",
    gap: str = "gap-8",
    **kwargs
) -> str:
    """Two-column layout"""
    return f'''
    <div class="grid grid-cols-2 {gap}">
        <div>{left}</div>
        <div>{right}</div>
    </div>
    '''


def ThreeColumn(
    left: str = "",
    center: str = "",
    right: str = "",
    gap: str = "gap-6",
    **kwargs
) -> str:
    """Three-column layout"""
    return f'''
    <div class="grid grid-cols-3 {gap}">
        <div>{left}</div>
        <div>{center}</div>
        <div>{right}</div>
    </div>
    '''


__all__ = [
    'Container',
    'Grid',
    'Flex',
    'Stack',
    'Section',
    'Row',
    'Column',
    'AspectRatio',
    'Spacer',
    'Divider',
    'Center',
    'Sidebar',
    'TwoColumn',
    'ThreeColumn',
]
