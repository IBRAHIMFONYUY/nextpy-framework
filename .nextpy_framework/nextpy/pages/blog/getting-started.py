"""Getting Started with NextPy - Blog Post"""

def get_template():
    return "blog/post.html"

async def get_server_side_props(context):
    return {
        "props": {
            "title": "Getting Started with NextPy",
            "author": "NextPy Team",
            "date": "November 2025",
            "slug": "getting-started",
            "excerpt": "Learn how to build your first NextPy application in just 5 minutes",
            "content": """
# Getting Started with NextPy

NextPy makes it incredibly easy to build modern web applications with Python. In this guide, we'll walk through creating your first app.

## Installation

Get NextPy running with a single command:

```bash
pip install nextpy-framework
nextpy create my-app
cd my-app
nextpy dev
```

That's it! Your app is running at `http://localhost:5000`.

## Your First Page

Pages are just Python files in the `pages/` directory. Let's create `pages/hello.py`:

```python
def get_template():
    return "hello.html"

async def get_server_side_props(context):
    return {
        "props": {
            "message": "Hello, NextPy!"
        }
    }
```

Then create the template `templates/hello.html`:

```html
{% extends "_base.html" %}

{% block content %}
<div class="max-w-4xl mx-auto py-12">
    <h1>{{ message }}</h1>
    <p>Visit <a href="/hello">/hello</a> to see this page!</p>
</div>
{% endblock %}
```

## File-Based Routing

NextPy automatically creates routes from your file structure:

- `pages/index.py` → `/` (home page)
- `pages/about.py` → `/about`
- `pages/blog/index.py` → `/blog`
- `pages/blog/[slug].py` → `/blog/:slug` (dynamic)
- `pages/api/posts.py` → `/api/posts` (REST API)

## Fetching Data

Use `get_server_side_props` to fetch data per request:

```python
async def get_server_side_props(context):
    posts = await fetch_from_database()
    return {"props": {"posts": posts}}
```

Or use `get_static_props` to pre-render at build time for better performance.

## Adding a Database

NextPy includes SQLAlchemy ORM support. Define a model:

```python
from nextpy.db import Base
from sqlalchemy import Column, String, Integer

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    content = Column(String)
```

Then use it in your pages:

```python
from nextpy.db import get_session, Post

async def get_server_side_props(context):
    session = get_session()
    posts = session.query(Post).all()
    return {"props": {"posts": posts}}
```

## Authentication

NextPy provides built-in JWT authentication:

```python
from nextpy.auth import AuthManager

# Create token
token = AuthManager.create_token(user_id=123)

# Verify token
user_id = AuthManager.verify_token(token)
```

## Next Steps

- Explore the [documentation](/documentation)
- Check out [components](/examples)
- Read more on the [blog](/blog)
- Try the [database example](/db_example)

Happy building! 🚀
"""
        }
    }
