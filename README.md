# NextPy Framework

A Python web framework inspired by Next.js. Build modern web applications with file-based routing, server-side rendering (SSR), static site generation (SSG), and more.

## Features

- **File-based Routing** - Pages in `pages/` become routes automatically
- **Dynamic Routes** - `[slug].py` creates dynamic URL segments
- **Server-Side Rendering** - `get_server_side_props` fetches data per request
- **Static Site Generation** - `get_static_props` builds pages at compile time
- **API Routes** - Create API endpoints in `pages/api/`
- **HTMX Integration** - SPA-like navigation without heavy JavaScript
- **Jinja2 Templates** - Powerful templating with layout inheritance

## Installation

```bash
pip install nextpy-framework
```

## Quick Start

### 1. Create a new project

```bash
nextpy create my-app
cd my-app
```

### 2. Create a page

```python
# pages/hello.py

def get_template():
    return "hello.html"

async def get_server_side_props(context):
    return {
        "props": {
            "message": "Hello, World!"
        }
    }
```

### 3. Create a template

```html
<!-- templates/hello.html -->
{% extends "_base.html" %}

{% block content %}
<h1>{{ message }}</h1>
{% endblock %}
```

### 4. Run the development server

```bash
nextpy dev
```

Visit `http://localhost:5000/hello` to see your page!

## Project Structure

```
my-app/
├── pages/              # Your pages (file-based routing)
│   ├── index.py        # Home page (/)
│   ├── about.py        # About page (/about)
│   ├── blog/
│   │   ├── index.py    # Blog listing (/blog)
│   │   └── [slug].py   # Dynamic post (/blog/:slug)
│   └── api/
│       └── posts.py    # API route (/api/posts)
├── templates/          # Jinja2 templates
│   ├── _base.html      # Base layout
│   └── index.html      # Page templates
├── public/             # Static files (CSS, JS, images)
└── main.py             # Entry point
```

## Data Fetching

### Server-Side Rendering (SSR)

Fetch data on every request:

```python
async def get_server_side_props(context):
    # Runs on every request
    data = await fetch_from_api()
    return {"props": {"data": data}}
```

### Static Site Generation (SSG)

Fetch data at build time:

```python
async def get_static_props(context):
    # Runs at build time
    data = await fetch_from_api()
    return {"props": {"data": data}}

async def get_static_paths():
    # For dynamic routes - define which paths to pre-render
    return {
        "paths": [
            {"params": {"slug": "post-1"}},
            {"params": {"slug": "post-2"}},
        ]
    }
```

## API Routes

Create API endpoints in `pages/api/`:

```python
# pages/api/users.py

async def get(request):
    return {"users": [...]}

async def post(request):
    data = await request.json()
    return {"created": data}
```

## CLI Commands

```bash
nextpy dev      # Start development server with hot reload
nextpy build    # Generate static files to out/
nextpy start    # Start production server
```

## Tech Stack

- **FastAPI** - High-performance async web framework
- **Jinja2** - Powerful templating engine
- **Pydantic** - Data validation
- **HTMX** - Modern browser features without JavaScript complexity
- **Uvicorn** - Lightning-fast ASGI server

## License

MIT
