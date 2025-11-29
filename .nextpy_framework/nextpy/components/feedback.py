"""
Feedback components for NextPy
Alert, Toast, Progress, Spinner, Badge, etc.
"""

from typing import Optional


def Alert(
    message: str = "",
    type: str = "info",
    title: Optional[str] = None,
    dismissible: bool = False,
    **kwargs
) -> str:
    """Alert component"""
    colors = {
        "info": "bg-blue-50 border-l-4 border-blue-600 text-blue-900",
        "success": "bg-green-50 border-l-4 border-green-600 text-green-900",
        "warning": "bg-yellow-50 border-l-4 border-yellow-600 text-yellow-900",
        "error": "bg-red-50 border-l-4 border-red-600 text-red-900",
    }
    
    color_class = colors.get(type, colors["info"])
    close_btn = '<button class="ml-auto">×</button>' if dismissible else ""
    title_html = f'<h3 class="font-bold mb-1">{title}</h3>' if title else ""
    
    return f'''<div class="p-4 rounded-lg {color_class} flex items-start gap-3">
        {title_html}
        <p>{message}</p>
        {close_btn}
    </div>'''


def Badge(
    text: str = "",
    color: str = "blue",
    size: str = "md",
    **kwargs
) -> str:
    """Badge component"""
    sizes = {
        "sm": "px-2 py-1 text-xs",
        "md": "px-3 py-1 text-sm",
        "lg": "px-4 py-2 text-base",
    }
    
    colors_class = {
        "blue": "bg-blue-100 text-blue-800",
        "red": "bg-red-100 text-red-800",
        "green": "bg-green-100 text-green-800",
        "yellow": "bg-yellow-100 text-yellow-800",
        "purple": "bg-purple-100 text-purple-800",
        "gray": "bg-gray-100 text-gray-800",
    }
    
    size_class = sizes.get(size, sizes["md"])
    color_class = colors_class.get(color, colors_class["blue"])
    
    return f'<span class="inline-block rounded-full {size_class} {color_class}">{text}</span>'


def Progress(
    value: int = 0,
    max: int = 100,
    show_label: bool = True,
    **kwargs
) -> str:
    """Progress bar component"""
    percentage = (value / max) * 100
    label_html = f'<span class="text-xs font-semibold">{percentage:.0f}%</span>' if show_label else ""
    
    return f'''<div class="flex items-center gap-2">
        <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div class="h-full bg-blue-600" style="width: {percentage}%"></div>
        </div>
        {label_html}
    </div>'''


def Spinner(
    size: str = "md",
    color: str = "blue",
    **kwargs
) -> str:
    """Spinner/loading component"""
    sizes = {
        "sm": "w-4 h-4",
        "md": "w-8 h-8",
        "lg": "w-12 h-12",
    }
    
    colors_class = {
        "blue": "text-blue-600",
        "red": "text-red-600",
        "green": "text-green-600",
        "gray": "text-gray-600",
    }
    
    size_class = sizes.get(size, sizes["md"])
    color_class = colors_class.get(color, colors_class["blue"])
    
    return f'''<svg class="animate-spin {size_class} {color_class}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>'''


def Skeleton(
    width: str = "w-full",
    height: str = "h-4",
    count: int = 1,
    **kwargs
) -> str:
    """Skeleton loader component"""
    skeletons = ""
    for _ in range(count):
        skeletons += f'<div class="bg-gray-200 rounded animate-pulse {width} {height} mb-2"></div>'
    
    return skeletons


def Toast(
    message: str = "",
    type: str = "info",
    duration: int = 3000,
    **kwargs
) -> str:
    """Toast notification component"""
    colors = {
        "info": "bg-blue-600",
        "success": "bg-green-600",
        "warning": "bg-yellow-600",
        "error": "bg-red-600",
    }
    
    color_class = colors.get(type, colors["info"])
    
    return f'''<div class="fixed bottom-4 right-4 {color_class} text-white px-6 py-3 rounded-lg shadow-lg animate-fade-in-up" role="alert">
        {message}
    </div>
    <style>
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .animate-fade-in-up {{ animation: fadeInUp 0.3s ease-in-out; }}
    </style>'''


def Tooltip(
    text: str = "",
    content: str = "",
    position: str = "top",
    **kwargs
) -> str:
    """Tooltip component"""
    positions = {
        "top": "bottom-full mb-2",
        "bottom": "top-full mt-2",
        "left": "right-full mr-2",
        "right": "left-full ml-2",
    }
    
    pos_class = positions.get(position, positions["top"])
    
    return f'''<div class="relative inline-block group">
        <span class="cursor-help underline decoration-dotted">{text}</span>
        <div class="absolute {pos_class} opacity-0 group-hover:opacity-100 transition-opacity bg-gray-900 text-white px-3 py-2 rounded text-sm whitespace-nowrap pointer-events-none">
            {content}
        </div>
    </div>'''


def Loader(
    text: str = "Loading...",
    **kwargs
) -> str:
    """Loader component with text"""
    return f'''<div class="flex flex-col items-center justify-center gap-4">
        {Spinner(size="lg")}
        <p class="text-gray-600 font-semibold">{text}</p>
    </div>'''


def Empty(
    icon: str = "📭",
    title: str = "No data",
    message: str = "Nothing to display",
    **kwargs
) -> str:
    """Empty state component"""
    return f'''<div class="flex flex-col items-center justify-center py-16 text-center">
        <div class="text-5xl mb-4">{icon}</div>
        <h3 class="text-xl font-bold text-gray-900 mb-2">{title}</h3>
        <p class="text-gray-600">{message}</p>
    </div>'''


__all__ = [
    'Alert',
    'Badge',
    'Progress',
    'Spinner',
    'Skeleton',
    'Toast',
    'Tooltip',
    'Loader',
    'Empty',
]
