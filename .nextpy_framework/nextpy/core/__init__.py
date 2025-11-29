"""NextPy Core Module - Routing, Rendering, and Data Fetching"""

from nextpy.core.router import Router, Route, DynamicRoute
from nextpy.core.renderer import Renderer
from nextpy.core.data_fetching import (
    get_server_side_props,
    get_static_props,
    get_static_paths,
)
from nextpy.core.builder import Builder

__all__ = [
    "Router",
    "Route",
    "DynamicRoute", 
    "Renderer",
    "get_server_side_props",
    "get_static_props",
    "get_static_paths",
    "Builder",
]
