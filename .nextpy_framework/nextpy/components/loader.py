"""
Loader/Spinner Components
Various loading indicators
"""


def spinner(size: str = "md", color: str = "blue") -> str:
    """Generate spinner HTML"""
    sizes = {"sm": "w-4 h-4", "md": "w-8 h-8", "lg": "w-12 h-12"}
    colors = {
        "blue": "border-blue-500",
        "red": "border-red-500",
        "green": "border-green-500",
        "purple": "border-purple-500"
    }
    
    return f'''
    <div class="flex justify-center">
        <div class="{sizes.get(size, sizes['md'])} border-4 border-gray-200 {colors.get(color, colors['blue'])} border-t-transparent rounded-full animate-spin"></div>
    </div>
    '''


def skeleton(lines: int = 3, width: str = "full") -> str:
    """Generate skeleton loader (content placeholder)"""
    skeleton_lines = "\n".join([
        f'<div class="h-4 bg-gray-200 rounded mb-2 animate-pulse"></div>'
        for _ in range(lines)
    ])
    
    return f'''
    <div class="w-{width}">
        {skeleton_lines}
    </div>
    '''


def progress_bar(value: int = 50, max_value: int = 100, color: str = "blue") -> str:
    """Generate progress bar"""
    percentage = (value / max_value) * 100
    colors = {
        "blue": "bg-blue-500",
        "red": "bg-red-500",
        "green": "bg-green-500",
        "purple": "bg-purple-500"
    }
    
    return f'''
    <div class="w-full bg-gray-200 rounded-full h-2">
        <div class="{colors.get(color, colors['blue'])} h-2 rounded-full" style="width: {percentage}%"></div>
    </div>
    <p class="text-sm text-gray-600 mt-1">{value}/{max_value}</p>
    '''


def loading_screen(message: str = "Loading...") -> str:
    """Full screen loading overlay"""
    return f'''
    <div class="fixed inset-0 bg-white bg-opacity-90 flex items-center justify-center z-50">
        <div class="text-center">
            <div class="w-12 h-12 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
            <p class="text-lg text-gray-700">{message}</p>
        </div>
    </div>
    '''
