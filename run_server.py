#!/usr/bin/env python3
"""
Simple server runner for NextPy
"""
import sys
import os
from pathlib import Path

# Add the nextpy framework to Python path
nextpy_path = Path(__file__).parent / ".nextpy_framework"
sys.path.insert(0, str(nextpy_path))

from nextpy.server.app import create_app
import uvicorn

# Create the NextPy app
app = create_app(
    pages_dir="pages",
    templates_dir="templates", 
    public_dir="public",
    out_dir="out",
    debug=True
)

if __name__ == "__main__":
    print("🚀 Starting NextPy server on http://localhost:8000")
    print("📁 PSX Test Page: http://localhost:8000/psx_test")
    uvicorn.run(app, host="0.0.0.0", port=8000)
