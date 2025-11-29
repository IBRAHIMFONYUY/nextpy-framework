# NextPy Complete Guide

Comprehensive documentation for all NextPy features, with examples for each.

## Table of Contents

1. [Getting Started](#getting-started)
2. [File-Based Routing](#file-based-routing)
3. [Pages & Components](#pages--components)
4. [Data Fetching](#data-fetching)
5. [API Routes](#api-routes)
6. [Built-in Components](#built-in-components)
7. [Images & Media](#images--media)
8. [Layouts & Nesting](#layouts--nesting)
9. [SEO & Meta Tags](#seo--meta-tags)
10. [Environment Variables](#environment-variables)
11. [Error Handling](#error-handling)
12. [Middleware](#middleware)
13. [Static Generation](#static-generation)
14. [Redirects & Rewrites](#redirects--rewrites)
15. [Forms & Validation](#forms--validation)
16. [Authentication](#authentication)
17. [Deployment](#deployment)

---

## Getting Started

### Installation

```bash
# Via pip
pip install nextpy-framework

# Or from source
git clone https://github.com/nextpy/nextpy-framework.git
cd nextpy-framework
pip install -e .
```

### Create Your First Project

```bash
nextpy create my-blog
cd my-blog
nextpy dev
```

Visit `http://localhost:5000` - your app is running with hot reload!

### Project Structure

```
my-blog/
├── pages/                    # Routes & API endpoints
│   ├── index.py             # Home page (/)
│   ├── about.py             # About page (/about)
│   ├── blog/
│   │   ├── index.py         # Blog listing (/blog)
│   │   └── [slug].py        # Dynamic posts (/blog/:slug)
│   └── api/
│       ├── posts.py         # GET /api/posts
│       └── health.py        # GET /api/health
├── templates/               # Jinja2 templates
│   ├── _base.html          # Root layout
│   ├── components/         # Reusable components
│   │   ├── button.html
│   │   ├── card.html
│   │   └── image.html
│   └── *.html              # Page templates
├── public/                 # Static files
│   ├── css/
│   ├── js/
│   └── images/
├── main.py                 # Entry point
└── requirements.txt        # Dependencies
```

---

## File-Based Routing

### Basic Routes

Create Python files in `pages/` - they automatically become routes:

| File | Route |
|------|-------|
| `pages/index.py` | `/` |
| `pages/about.py` | `/about` |
| `pages/contact.py` | `/contact` |
| `pages/blog/index.py` | `/blog` |
| `pages/blog/news.py` | `/blog/news` |

### Dynamic Routes

Use brackets `[param]` for dynamic segments:

```python
# pages/blog/[slug].py
def get_template():
    return "blog/post.html"

async def get_server_side_props(context):
    slug = context["params"]["slug"]
    post = await fetch_post(slug)
    return {"props": {"post": post}}
```

Access at `/blog/hello-world`, `/blog/my-first-post`, etc.

### Catch-All Routes

Use `[...params]` to catch multiple segments:

```python
# pages/docs/[...path].py
async def get_server_side_props(context):
    path = context["params"]["path"]  # List of segments
    # path = ["guides", "setup", "installation"]
```

### Optional Routes

Make segments optional with double brackets:

```python
# pages/[[lang]].py
# Matches: /, /en, /fr, /es
```

---

## Pages & Components

### Creating a Page

```python
# pages/products.py

def get_template():
    """Return template filename"""
    return "products.html"

async def get_server_side_props(context):
    """Fetch data per request (SSR)"""
    products = await fetch_products()
    return {
        "props": {
            "products": products,
            "title": "Products",
        }
    }
```

```html
<!-- templates/products.html -->
{% extends "_base.html" %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="container">
    <h1>{{ title }}</h1>
    <div class="grid">
        {% for product in products %}
            <div class="card">
                <h3>{{ product.name }}</h3>
                <p>${{ product.price }}</p>
            </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
```

---

## Data Fetching

### Server-Side Rendering (SSR)

Fetch on every request:

```python
# pages/index.py
async def get_server_side_props(context):
    data = await fetch_latest_data()
    return {"props": {"data": data}}
```

**When to use**: Real-time data, user-specific content, frequent updates

### Static Site Generation (SSG)

Fetch once at build time:

```python
# pages/blog/[slug].py
async def get_static_props(context):
    slug = context["params"]["slug"]
    post = await fetch_post(slug)
    return {"props": {"post": post}}

async def get_static_paths():
    """Define which paths to pre-render"""
    posts = await fetch_all_posts()
    return {
        "paths": [
            {"params": {"slug": post.slug}}
            for post in posts
        ]
    }
```

**When to use**: Blog posts, product pages, documentation

### Incremental Static Regeneration (ISR)

Revalidate SSG at intervals:

```python
async def get_static_props(context):
    data = await fetch_data()
    return {
        "props": {"data": data},
        "revalidate": 3600  # Revalidate every hour
    }
```

### Context Object

Access request info in data fetching:

```python
async def get_server_side_props(context):
    # context["params"] - Dynamic route params
    # context["query"] - Query string params
    # context["headers"] - HTTP headers
    # context["cookies"] - Cookies
    slug = context["params"]["slug"]
    page = context["query"].get("page", "1")
    return {"props": {"slug": slug, "page": page}}
```

---

## API Routes

### Basic API Routes

```python
# pages/api/users.py

async def get(request):
    """GET /api/users"""
    users = await fetch_users()
    return {"users": users}

async def post(request):
    """POST /api/users"""
    data = await request.json()
    user = await create_user(data)
    return {"created": True, "user": user}

async def put(request):
    """PUT /api/users"""
    data = await request.json()
    result = await update_user(data)
    return {"updated": result}

async def delete(request):
    """DELETE /api/users"""
    await delete_user()
    return {"deleted": True}
```

### Dynamic API Routes

```python
# pages/api/posts/[id].py

async def get(request):
    post_id = request.path_params["id"]
    post = await fetch_post(post_id)
    return {"post": post}

async def put(request):
    post_id = request.path_params["id"]
    data = await request.json()
    await update_post(post_id, data)
    return {"updated": True}
```

### File Uploads

```python
# pages/api/upload.py
from fastapi import UploadFile, File

async def post(request):
    file: UploadFile = await request.form()["file"]
    contents = await file.read()
    # Process file...
    return {"filename": file.filename, "size": len(contents)}
```

### Error Responses

```python
# pages/api/secure.py
from fastapi import HTTPException

async def get(request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"data": "secret"}
```

---

## Built-in Components

### Button Component

```html
{% from "components/button.html" import button %}

<!-- Variants: primary, secondary, outline, ghost, danger -->
{{ button("Click Me", "/action", "primary") }}
{{ button("Learn More", "/about", "outline") }}

<!-- Sizes: sm, md, lg -->
{{ button("Small", "/", "primary", "sm") }}
{{ button("Large", "/", "primary", "lg") }}

<!-- With icons -->
{{ button("Submit", "#", "primary", "md", "✓") }}
```

### Card Component

```html
{% from "components/card.html" import card %}

{{ card(
    title="Product Name",
    content="Description here",
    image="/images/product.jpg",
    link="/products/123",
    variant="default"  # or "featured"
) }}
```

### Form Components

```html
{% from "components/form.html" import input, textarea, select %}

<form method="POST" action="/api/contact">
    {{ input("name", "Full Name", "text", "John Doe", required=True) }}
    {{ input("email", "Email", "email", "", required=True) }}
    {{ select("topic", "Topic", [
        {"value": "", "label": "Select..."},
        {"value": "sales", "label": "Sales Inquiry"},
        {"value": "support", "label": "Support"},
    ], required=True) }}
    {{ textarea("message", "Message", "Your message...", required=True) }}
    {{ button("Send", "#", "primary") }}
</form>
```

### Alert Component

```html
{% from "components/alert.html" import alert %}

{{ alert("Operation successful!", "success") }}
{{ alert("Please review this", "warning") }}
{{ alert("An error occurred", "error", dismissible=True) }}
{{ alert("For your information", "info") }}
```

### Image Component (Optimized)

```html
{% from "components/image.html" import image %}

<!-- Auto-optimized, lazy-loaded, responsive -->
{{ image(
    src="/images/hero.jpg",
    alt="Hero image",
    width=1200,
    height=600,
    quality=85
) }}
```

### Link Component (with Prefetch)

```html
{% from "components/link.html" import link %}

<!-- HTMX-powered, prefetches on hover -->
{{ link("About Us", "/about") }}
{{ link("Blog", "/blog", class="nav-link") }}

<!-- External links -->
{{ link("GitHub", "https://github.com", external=True) }}
```

---

## Images & Media

### Image Optimization

```html
{% from "components/image.html" import image %}

{{ image(
    src="/images/photo.jpg",
    alt="Photo",
    width=800,
    height=600,
    quality=85,           # 1-100
    lazy=True,            # Lazy load
    responsive=True,      # Responsive sizes
) }}
```

### Background Images

```html
<div style="background-image: url('/images/bg.jpg'); background-size: cover;">
    Content here
</div>
```

### Video Embedding

```html
<video width="640" height="360" controls>
    <source src="/videos/demo.mp4" type="video/mp4">
    Your browser doesn't support HTML5 video.
</video>
```

---

## Layouts & Nesting

### Base Layout

```html
<!-- templates/_base.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{% block title %}My Site{% endblock %}</title>
</head>
<body>
    <nav>Navigation here</nav>
    {% block content %}{% endblock %}
    <footer>Footer here</footer>
</body>
</html>
```

### Nested Layouts

```html
<!-- templates/_blog-layout.html -->
{% extends "_base.html" %}

{% block content %}
<div class="blog-wrapper">
    <aside class="sidebar">
        <!-- Blog navigation -->
    </aside>
    <main>
        {% block blog_content %}{% endblock %}
    </main>
</div>
{% endblock %}
```

### Using Nested Layout

```html
<!-- templates/blog/post.html -->
{% extends "_blog-layout.html" %}

{% block blog_content %}
<article>
    <h1>{{ title }}</h1>
    <p>{{ content }}</p>
</article>
{% endblock %}
```

### Multiple Layout Levels

```
_base.html (root)
  ├── _dashboard-layout.html
  │   └── dashboard/profile.html
  ├── _blog-layout.html
  │   └── blog/post.html
  └── _docs-layout.html
      └── docs/guide.html
```

---

## SEO & Meta Tags

### Using SEO Component

```python
# pages/blog/[slug].py
async def get_server_side_props(context):
    post = await fetch_post(context["params"]["slug"])
    return {
        "props": {
            "title": post.title,
            "description": post.excerpt,
            "image": post.featured_image,
            "url": f"/blog/{post.slug}",
            "og_type": "article",
        }
    }
```

```html
<!-- templates/blog/post.html -->
{% from "components/head.html" import seo %}

{% block head %}
    {{ seo(
        title=title,
        description=description,
        image=image,
        url=url,
        og_type="article",
        keywords="python, web, framework"
    ) }}
{% endblock %}
```

### Manual Meta Tags

```html
<head>
    <meta name="description" content="{{ description }}">
    <meta name="keywords" content="python, web">
    <meta property="og:title" content="{{ title }}">
    <meta property="og:description" content="{{ description }}">
    <meta property="og:image" content="{{ image }}">
    <meta property="og:type" content="website">
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:title" content="{{ title }}">
    <meta property="twitter:description" content="{{ description }}">
    <meta property="twitter:image" content="{{ image }}">
</head>
```

### Canonical URLs

```html
<link rel="canonical" href="https://example.com{{ canonical_url }}" />
```

---

## Environment Variables

### Define Variables

```bash
# .env file
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-secret-key
DEBUG=false
API_KEY=abc123
```

### Access in Python

```python
# pages/api/users.py
import os

async def get(request):
    db_url = os.getenv("DATABASE_URL")
    secret = os.getenv("SECRET_KEY")
    # Use variables...
    return {"success": True}
```

### Access in Templates

```html
<!-- Environment variables are passed as props -->
<p>App Version: {{ app_version }}</p>
```

### Type-Safe Environment Variables

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Error Handling

### 404 Pages

```python
# pages/_404.py
def get_template():
    return "_404.html"

async def get_server_side_props(context):
    return {"props": {}}
```

```html
<!-- templates/_404.html -->
{% extends "_base.html" %}
{% block content %}
<div class="text-center py-20">
    <h1 class="text-4xl font-bold">404</h1>
    <p>Page not found</p>
    <a href="/">Back to home</a>
</div>
{% endblock %}
```

### Error Pages

```python
# pages/_error.py
def get_template():
    return "_error.html"

async def get_server_side_props(context):
    error = context.get("error", {})
    return {
        "props": {
            "status": error.get("status", 500),
            "message": error.get("message", "Something went wrong"),
        }
    }
```

### Exception Handling

```python
# pages/data.py
async def get_server_side_props(context):
    try:
        data = await fetch_data()
        return {"props": {"data": data}}
    except Exception as e:
        return {
            "redirect": "/error",
            "props": {}
        }
```

---

## Middleware

### Custom Middleware

```python
# middleware.py
async def request_middleware(request):
    """Run before request"""
    request.state.user_id = request.headers.get("X-User-ID")

async def response_middleware(request, response):
    """Run after response"""
    response.headers["X-Custom-Header"] = "value"
    return response
```

### Register Middleware

```python
# main.py
from nextpy.server.app import create_app
from middleware import request_middleware, response_middleware

app = create_app()
app.middleware("http")(request_middleware)
app.middleware("http")(response_middleware)
```

### Authentication Middleware

```python
# middleware.py
async def auth_middleware(request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        request.state.user = None
    else:
        request.state.user = await verify_token(token)

# Usage in pages
async def get_server_side_props(context):
    user = context.get("state", {}).get("user")
    if not user:
        return {"redirect": "/login"}
    return {"props": {"user": user}}
```

---

## Static Generation

### Building for Production

```bash
nextpy build
```

Creates static HTML files in `out/` directory.

### Deployment

```bash
# Start production server
nextpy start

# With multiple workers
nextpy start --workers 4
```

---

## Redirects & Rewrites

### Redirect in Page

```python
# pages/old-page.py
async def get_server_side_props(context):
    return {
        "redirect": {
            "destination": "/new-page",
            "permanent": True,  # 301 vs 302
        }
    }
```

### Redirect in API

```python
# pages/api/login.py
from fastapi.responses import RedirectResponse

async def post(request):
    # ... verify credentials ...
    return RedirectResponse(url="/dashboard", status_code=303)
```

---

## Forms & Validation

### HTML Form

```html
<form action="/api/contact" method="POST" enctype="multipart/form-data">
    <input type="text" name="name" required>
    <input type="email" name="email" required>
    <textarea name="message"></textarea>
    <input type="file" name="attachment">
    <button type="submit">Send</button>
</form>
```

### Form Validation

```python
# pages/api/contact.py
from pydantic import BaseModel, EmailStr

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str

async def post(request):
    data = await request.json()
    try:
        form = ContactForm(**data)
        # Process form...
        return {"success": True}
    except ValueError as e:
        return {"error": str(e)}, 400
```

---

## Authentication

### Session-Based Auth

```python
# pages/api/login.py
async def post(request):
    data = await request.json()
    user = await verify_credentials(data["email"], data["password"])
    if user:
        request.session["user_id"] = user.id
        return {"success": True}
    return {"error": "Invalid credentials"}, 401
```

### Protected Routes

```python
# pages/dashboard.py
async def get_server_side_props(context):
    user_id = context.get("session", {}).get("user_id")
    if not user_id:
        return {"redirect": "/login"}
    
    user = await fetch_user(user_id)
    return {"props": {"user": user}}
```

### JWT Tokens

```python
# utils/jwt.py
import jwt
from datetime import datetime, timedelta

def create_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, "SECRET_KEY", algorithm="HS256")

def verify_token(token):
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        return payload["user_id"]
    except:
        return None
```

---

## Deployment

### Deploy to Heroku

```bash
git push heroku main
```

### Deploy to Vercel

```bash
vercel
```

### Deploy to VPS

```bash
# SSH into server
ssh user@server.com

# Install Python & dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Docker Deployment

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup for Production

```bash
export DEBUG=false
export DATABASE_URL=your-db-url
export SECRET_KEY=your-secret
nextpy build
nextpy start
```

---

## Tips & Best Practices

### Performance

- ✅ Use SSG for static content
- ✅ Use image optimization component
- ✅ Enable HTMX prefetch on navigation
- ✅ Cache API responses
- ✅ Minimize template complexity

### Security

- ✅ Validate all form inputs
- ✅ Use environment variables for secrets
- ✅ Enable CSRF protection
- ✅ Sanitize user input
- ✅ Use HTTPS in production

### Code Organization

- ✅ Keep pages simple (use get_server_side_props for logic)
- ✅ Extract business logic to utils/
- ✅ Reuse components via templates
- ✅ Use type hints (Pydantic)
- ✅ Structure by feature, not by type

---

## Troubleshooting

### Hot Reload Not Working

```bash
# Make sure watchdog is installed
pip install watchdog

# Restart dev server
nextpy dev --reload
```

### Port Already in Use

```bash
nextpy dev --port 3000
```

### Template Not Found

Check `templates/` directory and ensure template filename matches `get_template()` return value.

### Import Errors

Ensure pages directory is in Python path:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

---

## API Reference

### Context Object

```python
context = {
    "params": {...},      # Dynamic route params
    "query": {...},       # Query string params
    "headers": {...},     # HTTP headers
    "cookies": {...},     # Cookies
    "session": {...},     # Session data
    "state": {...},       # Request state
}
```

### Return Values

```python
# Successful render
{"props": {...}}

# Redirect
{"redirect": {"destination": "/path", "permanent": True}}

# Revalidate (SSG only)
{"props": {...}, "revalidate": 3600}

# Not found
{"notFound": True}
```

---

## Community & Support

- GitHub: https://github.com/nextpy/nextpy-framework
- Documentation: https://nextpy.dev
- Discord: https://discord.gg/nextpy
- Issues: https://github.com/nextpy/nextpy-framework/issues
