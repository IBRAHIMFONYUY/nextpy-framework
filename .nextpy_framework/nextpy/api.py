"""Helpers for calling APIs from NextPy server-side code."""

import json
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen

from fastapi import APIRouter


# Native FastAPI surface for application code.  It is mounted automatically by
# create_app(), so users do not need to reach into the framework internals.
api = APIRouter(prefix="/api")


def fetch_api(
    url: str,
    method: str = "GET",
    data: Any = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 10,
) -> Any:
    """Call a JSON API and return its decoded response.

    This is intended for ``getServerSideProps`` and other server-only code.
    Page API routes can still use FastAPI's ``Request`` directly.
    """
    request_headers = {"Accept": "application/json", **(headers or {})}
    body = data
    if isinstance(data, (dict, list)):
        body = json.dumps(data).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")
    request = Request(url, data=body, headers=request_headers, method=method.upper())
    with urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else None


__all__ = ["api", "fetch_api"]
