"""
NextPy - A Python web framework inspired by Next.js
File-based routing, SSR, SSG, and more with FastAPI + Jinja2
"""

__version__ = "1.0.1"

from nextpy.core.router import Router, Route, DynamicRoute
from nextpy.core.renderer import Renderer
from nextpy.core.data_fetching import (
    get_server_side_props,
    get_static_props,
    get_static_paths,
)
from nextpy.components.head import Head
from nextpy.components.link import Link
from nextpy.server.app import create_app
from nextpy.hooks import (
    useState,
    useEffect,
    useContext,
    useReducer,
    useCallback,
    useMemo,
    useRef,
    useGlobalState,
    component,
)

__all__ = [
    "Router",
    "Route", 
    "DynamicRoute",
    "Renderer",
    "get_server_side_props",
    "get_static_props",
    "get_static_paths",
    "Head",
    "Link",
    "create_app",
    "useState",
    "useEffect",
    "useContext",
    "useReducer",
    "useCallback",
    "useMemo",
    "useRef",
    "useGlobalState",
    "component",
    "maintainers",
    "main"
]
