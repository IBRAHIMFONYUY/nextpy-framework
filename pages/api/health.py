"""
API Route: /api/health
Health check endpoint
"""

from datetime import datetime


async def get(request, params):
    """
    GET /api/health
    Returns server health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "framework": "NextPy"
    }
