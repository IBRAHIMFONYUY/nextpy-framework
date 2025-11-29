"""Login page"""

def get_template():
    return "login.html"


async def get_server_side_props(context):
    return {"props": {"title": "Login"}}
