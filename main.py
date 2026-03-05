"""
NextPy Application Entry Point
This file serves as the main entry point for Render deployment
"""

import sys
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent / ".nextpy_framework"))

from nextpy.main import app

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
