"""
Components showcase page demonstrating all available NextPy components
"""

def get_template():
    return "components-showcase.html"


async def get_server_side_props(context):
    """Fetch component data"""
    return {
        "props": {
            "title": "Components Showcase",
            "description": "40+ production-ready UI components",
            "categories": [
                {
                    "name": "Forms",
                    "count": 13,
                    "items": ["Input", "TextArea", "Select", "Checkbox", "Radio", "FileInput", "DateInput", "TimeInput", "PasswordInput", "NumberInput", "RangeInput", "ColorInput", "Form"]
                },
                {
                    "name": "Layout",
                    "count": 5,
                    "items": ["Grid", "Flex", "Stack", "Container", "Sidebar"]
                },
                {
                    "name": "Feedback",
                    "count": 4,
                    "items": ["Alert", "Badge", "Progress", "Toast"]
                },
                {
                    "name": "Visual",
                    "count": 7,
                    "items": ["Tabs", "Accordion", "Dropdown", "Modal", "Card", "Breadcrumb", "Pagination"]
                },
                {
                    "name": "Loaders",
                    "count": 4,
                    "items": ["Spinner", "Skeleton", "ProgressBar", "LoadingScreen"]
                },
                {
                    "name": "Utilities",
                    "count": 5,
                    "items": ["Head", "Link", "Image", "HooksProvider", "useContext"]
                }
            ]
        }
    }
