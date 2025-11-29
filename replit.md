# NextPy - Python Web Framework

## Overview
NextPy is a Python web framework inspired by Next.js, providing file-based routing, server-side rendering (SSR), static site generation (SSG), and more using FastAPI + Jinja2.

**Status**: Complete and working

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
├── documentation.py    # Documentation (/documentation)
├── blog/
│   ├── index.py        # Blog listing (/blog)
│   └── [slug].py       # Dynamic blog post (/blog/:slug)
└── api/
    ├── posts.py        # API route (/api/posts)
    └── health.py       # Health check (/api/health)

templates/              # Jinja2 templates
├── _base.html          # Base layout with navigation
├── _page.html          # Generic page template
├── _404.html           # 404 error page
├── _error.html         # Error page
├── index.html          # Homepage template
├── about.html          # About template
├── documentation.html  # Documentation template
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

## Recent Features Added
- ✅ Comprehensive documentation (DOCUMENTATION.md)
- ✅ Image optimization component with lazy loading
- ✅ Link component with HTMX prefetch
- ✅ SEO utilities and structured data helpers
- ✅ Pagination, modal, breadcrumb components
- ✅ Form validation utilities (Pydantic models)
- ✅ Hot reload indicator with visual feedback
- ✅ Debug panel for development errors
- ✅ Advanced examples (ISR, protected routes, file uploads)
- ✅ Middleware support system
- ✅ Static site generation with revalidation

## Complete Feature List

**Core Features:**
- ✅ File-based routing with dynamic `[slug]` and catch-all `[...path]` routes
- ✅ Server-Side Rendering (SSR) with `get_server_side_props`
- ✅ Static Site Generation (SSG) with `get_static_props`
- ✅ Incremental Static Regeneration (ISR) with revalidation
- ✅ API routes with full HTTP methods (GET, POST, PUT, DELETE, PATCH)
- ✅ Sync & Async page functions (both supported!)
- ✅ Database support: SQLite, PostgreSQL, MySQL
- ✅ Environment variables with `.env` file
- ✅ Hot reload with visual indicator
- ✅ Debug panel for errors

**20+ Components:**
- Buttons, Cards, Alerts, Forms, Images, Links
- Pagination, Modal, Breadcrumb, Navigation
- SEO/Head component with structured data
- Navbar with HTMX integration

**Utilities:**
- Email sending (SMTP)
- File upload handling
- Caching with TTL
- Full-text search (simple & fuzzy)
- Form validation (Pydantic models)
- Logging system
- SEO utilities (sitemaps, robots.txt)

**Developer Experience:**
- CLI with commands: dev, build, start, create, routes
- Hot reload with file watching
- Debug panel with stack traces
- Type hints throughout

## Tech Stack
- **FastAPI** - High-performance web framework
- **SQLAlchemy** - ORM with database support
- **Uvicorn** - Lightning-fast ASGI server
- **Jinja2** - Powerful templating with inheritance
- **Pydantic** - Type-safe data validation
- **HTMX** - SPA features without JavaScript
- **Tailwind CSS** - Utility-first styling
- **Click** - CLI framework
- **Watchdog** - File monitoring for hot reload

## Package Architecture
- nextpy/server/app.py - FastAPI application factory
- nextpy/core/router.py - File-based routing engine
- nextpy/core/renderer.py - SSR with Jinja2
- nextpy/core/builder.py - SSG with static generation
- nextpy/core/data_fetching.py - getServerSideProps/getStaticProps
- nextpy/core/sync.py - Sync/Async support
- nextpy/db.py - SQLAlchemy database layer
- nextpy/config.py - Environment configuration
- nextpy/components/ - Python components (image, link, head)
- nextpy/utils/ - Caching, email, search, validators, SEO, logging, file uploads
- templates/components/ - 20+ Jinja2 macro components
- nextpy/cli.py - CLI scaffolding & commands
- pyproject.toml - Package metadata & deps

## Example Pages Included
- Homepage with hero section and feature grid
- Features showcase page
- Blog with dynamic posts
- About page
- Documentation page
- Database example page
- Contact form with email
- Search functionality
- Component examples
