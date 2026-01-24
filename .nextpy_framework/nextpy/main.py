"""
NextPy Application Entry Point
This is the main file that runs the NextPy server
"""

import sys
from pathlib import Path
import subprocess

print(f"DEBUG: Current working directory: {Path.cwd()}")
print(f"DEBUG: sys.path before modification: {sys.path}")

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent / ".nextpy_framework"))

print(f"DEBUG: sys.path after modification: {sys.path}")

# Compile Tailwind CSS using PostCSS
try:
    print("Compiling Tailwind CSS...")
    # Use PostCSS with the new Tailwind plugin
    subprocess.run(["./node_modules/.bin/postcss", "styles.css", "-o", "public/tailwind.css"], check=True)
    print("Tailwind CSS compiled successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error compiling Tailwind CSS: {e}")
except FileNotFoundError:
    print("Error: PostCSS not found. Make sure Node.js and Tailwind CSS are installed.")
    print("Install with: npm install postcss-cli @tailwindcss/postcss")


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
