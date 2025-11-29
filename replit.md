# NextPy - Python Web Framework

## Overview
NextPy is a Python web framework inspired by Next.js, providing file-based routing, server-side rendering (SSR), static site generation (SSG), and more using FastAPI + Jinja2.

## Project Structure
```
nextpy/                 # Core framework
├── __init__.py         # Package exports
├── cli.py              # CLI tool (nextpy dev/build/start)
├── core/
│   ├── router.py       # File-based routing engine
│   ├── renderer.py     # Jinja2 SSR renderer
│   ├── builder.py      # SSG build system
│   └── data_fetching.py # getServerSideProps/getStaticProps
├── components/
│   ├── head.py         # SEO head component
│   ├── link.py         # Navigation link with HTMX
│   └── image.py        # Optimized image component
└── server/
    ├── app.py          # FastAPI application factory
    └── middleware.py   # Request/response middleware

pages/                  # User pages (file-based routing)
├── index.py            # Homepage (/)
├── about.py            # About page (/about)
├── docs.py             # Documentation (/docs)
├── blog/
│   ├── index.py        # Blog listing (/blog)
│   └── [slug].py       # Dynamic blog post (/blog/:slug)
└── api/
    ├── posts.py        # API route (/api/posts)
    └── health.py       # Health check (/api/health)

templates/              # Jinja2 templates
├── _base.html          # Base layout
├── _page.html          # Generic page template
├── _404.html           # 404 error page
├── _error.html         # Error page
├── index.html          # Homepage template
├── about.html          # About template
├── docs.html           # Documentation template
└── blog/
    ├── index.html      # Blog listing template
    └── [slug].html     # Blog post template

public/                 # Static files
├── css/
├── js/
└── images/

main.py                 # Application entry point
```

## Key Features
1. **File-based Routing**: Pages in `pages/` become routes automatically
2. **Dynamic Routes**: `[slug].py` creates dynamic segments
3. **SSR**: `get_server_side_props` fetches data per request
4. **SSG**: `get_static_props` fetches data at build time
5. **API Routes**: FastAPI endpoints in `pages/api/`
6. **HTMX Integration**: SPA-like navigation without heavy JS
7. **Pydantic Validation**: Type-safe API routes

## CLI Commands
- `nextpy dev` - Start development server with hot reload
- `nextpy build` - Build static files to out/
- `nextpy start` - Start production server

## Development
Run the development server:
```bash
python main.py
```
Or use the CLI:
```bash
python -m nextpy.cli dev
```

## Tech Stack
- FastAPI - Web framework
- Jinja2 - Templating
- Pydantic - Data validation
- HTMX - Client interactivity
- Tailwind CSS - Styling
- Uvicorn - ASGI server
