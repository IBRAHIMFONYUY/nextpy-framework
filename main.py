"""
NextPy Application Entry Point
This is the main file that runs the NextPy server
"""

from nextpy.server.app import create_app
from nextpy.db import init_db
from nextpy.config import settings

# Initialize database
try:
    init_db(settings.database_url)
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")

app = create_app(
    pages_dir="pages",
    templates_dir="templates",
    public_dir="public",
    out_dir="out",
    debug=settings.debug,
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True, reload_dirs=["pages", "templates", "nextpy"])
