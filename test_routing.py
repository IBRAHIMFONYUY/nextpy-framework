#!/usr/bin/env python3
"""Test routing issue with links"""

import sys
import os
from pathlib import Path

# Add the framework to path
sys.path.insert(0, str(Path(__file__).parent / ".nextpy_framework"))

from nextpy.core.router import Router

def test_routing():
    """Test the routing issue"""
    
    # Create a temporary pages directory
    pages_dir = Path("test_pages")
    pages_dir.mkdir(exist_ok=True)
    
    # Create index page
    (pages_dir / "index.py").write_text('''
def handler():
    return "<h1>Home Page</h1><p><a href='/about'>About Page</a></p>"
''')
    
    # Create about page
    (pages_dir / "about.py").write_text('''
def handler():
    return "<h1>About Page</h1><p><a href='/'>Back Home</a></p>"
''')
    
    # Create router and scan pages
    router = Router(pages_dir=str(pages_dir))
    router.scan_pages()
    
    print("=== ROUTES FOUND ===")
    for route in router.get_all_routes():
        print(f"Route: {route.path} -> {route.file_path}")
        if route.pattern:
            print(f"  Pattern: {route.pattern.pattern}")
        print()
    
    print("=== TESTING ROUTES ===")
    
    # Test route matching
    test_paths = ["/", "/about", "/contact"]
    
    for path in test_paths:
        print(f"\nTesting path: {path}")
        match = router.match(path)
        if match:
            route, params = match
            print(f"  ✅ MATCHED: {route.path} -> {route.file_path}")
            if params:
                print(f"  📋 Params: {params}")
        else:
            print(f"  ❌ NO MATCH")
    
    # Cleanup
    import shutil
    shutil.rmtree(pages_dir)

if __name__ == "__main__":
    test_routing()
