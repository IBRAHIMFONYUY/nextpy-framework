"""
Contact Page with Form
Example of form handling and validation
"""

def get_template():
    return "contact.html"


async def get_server_side_props(context):
    return {
        "props": {
            "title": "Contact Us",
            "description": "Get in touch with NextPy team"
        }
    }
