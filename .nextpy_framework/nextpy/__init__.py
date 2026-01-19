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
    useCounter,
    useToggle,
    useLocalStorage,
    useFetch,
    useDebounce,
    createContext,
    Provider,
)
from nextpy.security import (
    security_manager,
    sanitize_input,
    safe_html,
    validate_and_sanitize_props,
)
from nextpy.hooks_provider import with_hooks
from nextpy.components import (
    Button, Card, Input, TextArea, Select, Checkbox, Radio, RadioGroup, Form, FormGroup, FileInput,
    NumberInput, DateInput, TimeInput, PasswordInput, RangeInput, ColorInput, SubmitButton,
    Container, Grid, Flex, Stack, Sidebar, MainContent, Section, Article, 
    Header, Footer, Navigation, Center, Spacer, Divider, AspectRatio,
    Badge, Avatar, Icon, Alert, Progress, Skeleton, Tooltip, Chip, 
    Breadcrumb, Table, Code, Blockquote,
    Navbar, Menu, Dropdown, Tabs, Pagination, 
    SearchBar, BreadcrumbNav
)
from nextpy.jsx import (
    div, h1, h2, h3, h4, h5, h6,
    p, span, a, img,
    ul, ol, li,
    form, input, button, textarea, select, option,
    table, thead, tbody, tr, th, td,
    header, footer, main, section, article, nav, aside,
    strong, em, i, b,
    hr, br,
    style, script, meta, link, title,
    jsx
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
    "useCounter",
    "useToggle",
    "useLocalStorage",
    "useFetch",
    "useDebounce",
    "createContext",
    "Provider",
    "with_hooks",
    "security_manager",
    "sanitize_input",
    "safe_html",
    "validate_and_sanitize_props",
    "Button", "Card", "Input", "TextArea", "Select", "Checkbox", "Radio", "RadioGroup", "Form", "FormGroup", "FileInput",
    "NumberInput", "DateInput", "TimeInput", "PasswordInput", "RangeInput", "ColorInput", "SubmitButton",
    "Container", "Grid", "Flex", "Stack", "Sidebar", "MainContent", "Section", "Article", 
    "Header", "Footer", "Navigation", "Center", "Spacer", "Divider", "AspectRatio",
    "Badge", "Avatar", "Icon", "Alert", "Progress", "Skeleton", "Tooltip", "Chip", 
    "Breadcrumb", "Table", "Code", "Blockquote",
    "Navbar", "Menu", "Dropdown", "Tabs", "Pagination", 
    "SearchBar", "BreadcrumbNav",
    "div", "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "span", "a", "img",
    "ul", "ol", "li",
    "form", "input", "button", "textarea", "select", "option",
    "table", "thead", "tbody", "tr", "th", "td",
    "header", "footer", "main", "section", "article", "nav", "aside",
    "strong", "em", "i", "b",
    "hr", "br",
    "style", "script", "meta", "link", "title",
    "jsx",
    "maintainers",
    "main"
]

maintainers = [
    {"name": "NextPy Team", "email": "team@nextpy.dev"}
]

main = "nextpy.server.app:create_app"