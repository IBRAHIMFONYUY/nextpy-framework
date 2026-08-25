"""Small, protected SQLAlchemy admin site for NextPy applications."""

import os
from datetime import date, datetime
from decimal import Decimal
from html import escape
from typing import Any, Dict, Iterable, Optional, Type

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import inspect, select
from sqlalchemy.orm import DeclarativeMeta

from .db import get_session


class AdminSite:
    """Register SQLAlchemy models and expose a small Django-style admin."""

    def __init__(self, title: str = "NextPy Admin"):
        self.title = title
        self.models: Dict[str, Type[Any]] = {}
        self.security = HTTPBasic(auto_error=False)

    def register(self, model: Type[Any], name: Optional[str] = None) -> Type[Any]:
        """Register a SQLAlchemy declarative model and return it unchanged."""
        if not isinstance(model, DeclarativeMeta):
            raise TypeError("Admin models must be SQLAlchemy declarative models")
        model_name = name or model.__name__.lower()
        self.models[model_name] = model
        return model

    def unregister(self, model_or_name: Any) -> None:
        """Remove a model from the admin registry."""
        name = model_or_name if isinstance(model_or_name, str) else model_or_name.__name__.lower()
        self.models.pop(name, None)

    def _authenticate(self, credentials: Optional[HTTPBasicCredentials]) -> None:
        username = os.getenv("NEXTPY_ADMIN_USERNAME")
        password = os.getenv("NEXTPY_ADMIN_PASSWORD")
        if not username or not password:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Set NEXTPY_ADMIN_USERNAME and NEXTPY_ADMIN_PASSWORD to enable admin access",
            )
        if not credentials or credentials.username != username or credentials.password != password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin authentication required",
                headers={"WWW-Authenticate": "Basic"},
            )

    def _model(self, name: str) -> Type[Any]:
        model = self.models.get(name)
        if model is None:
            raise HTTPException(status_code=404, detail="Unknown admin model")
        return model

    @staticmethod
    def _columns(model: Type[Any]) -> list[str]:
        return [column.key for column in inspect(model).columns]

    @staticmethod
    def _serialize(value: Any) -> Any:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return str(value)
        return value

    def _serialize_row(self, row: Any, columns: Iterable[str]) -> Dict[str, Any]:
        return {column: self._serialize(getattr(row, column)) for column in columns}

    def _dashboard(self) -> str:
        rows = "".join(
            f'<li><a href="/admin/{escape(name)}">{escape(name)}</a></li>'
            for name in sorted(self.models)
        ) or "<li>No models registered</li>"
        return self._page("Dashboard", f"<h1>{escape(self.title)}</h1><ul>{rows}</ul>")

    def _page(self, heading: str, body: str) -> str:
        return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(heading)} | {escape(self.title)}</title>
<style>body{{font:16px system-ui;margin:2rem;max-width:1100px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:.5rem;text-align:left}}a{{color:#0645ad}}form{{display:grid;gap:.6rem;max-width:600px}}input,textarea{{padding:.5rem}}button{{padding:.5rem .8rem;cursor:pointer}}</style>
</head><body><nav><a href="/admin">Admin</a></nav>{body}</body></html>"""

    def router(self, prefix: str = "/admin") -> APIRouter:
        """Create the FastAPI router used by :meth:`mount`."""
        router = APIRouter(prefix=prefix)
        auth = Depends(self.security)

        @router.get("", response_class=HTMLResponse)
        @router.get("/", response_class=HTMLResponse)
        async def dashboard(credentials: Optional[HTTPBasicCredentials] = auth):
            self._authenticate(credentials)
            return self._dashboard()

        @router.get("/{model_name}", response_class=HTMLResponse)
        async def model_list(model_name: str, request: Request, credentials: Optional[HTTPBasicCredentials] = auth):
            self._authenticate(credentials)
            model = self._model(model_name)
            columns = self._columns(model)
            query = request.query_params.get("q", "").strip()
            limit = min(max(int(request.query_params.get("limit", "50")), 1), 200)
            with get_session() as session:
                statement = select(model).limit(limit)
                objects = list(session.scalars(statement))
                if query:
                    objects = [row for row in objects if query.lower() in str(self._serialize_row(row, columns)).lower()]
            header = "".join(f"<th>{escape(column)}</th>" for column in columns)
            body_rows = "".join(
                "<tr>" + "".join(f"<td>{escape(str(self._serialize(getattr(row, column))))}</td>" for column in columns) + "</tr>"
                for row in objects
            ) or f'<tr><td colspan="{len(columns) or 1}">No records</td></tr>'
            return self._page(model_name, f"<h1>{escape(model_name)}</h1><p><a href=\"/admin/{escape(model_name)}/new\">Add record</a></p><form method=\"get\"><input name=\"q\" placeholder=\"Search\" value=\"{escape(query)}\"><button>Search</button></form><table><tr>{header}</tr>{body_rows}</table>")

        @router.get("/{model_name}/records")
        async def records(model_name: str, request: Request, credentials: Optional[HTTPBasicCredentials] = auth):
            self._authenticate(credentials)
            model = self._model(model_name)
            columns = self._columns(model)
            limit = min(max(int(request.query_params.get("limit", "100")), 1), 500)
            with get_session() as session:
                rows = list(session.scalars(select(model).limit(limit)))
            return [self._serialize_row(row, columns) for row in rows]

        @router.get("/{model_name}/new", response_class=HTMLResponse)
        async def new_record_form(model_name: str, credentials: Optional[HTTPBasicCredentials] = auth):
            self._authenticate(credentials)
            model = self._model(model_name)
            fields = []
            for column in inspect(model).columns:
                if column.primary_key:
                    continue
                input_type = "number" if str(column.type).upper().startswith(("INT", "NUM", "DEC", "FLOAT")) else "text"
                if "TEXT" in str(column.type).upper():
                    control = f'<textarea name="{escape(column.key)}" required>{""}</textarea>'
                else:
                    control = f'<input type="{input_type}" name="{escape(column.key)}" required>'
                fields.append(f'<label>{escape(column.key)}{control}</label>')
            form = "".join(fields) or "<p>This model has no editable fields.</p>"
            body = f'<h1>Add {escape(model_name)}</h1><form method="post">{form}<button type="submit">Create</button></form>'
            return self._page(f"Add {model_name}", body)

        @router.post("/{model_name}/new", response_class=HTMLResponse)
        async def submit_new_record(model_name: str, request: Request, credentials: Optional[HTTPBasicCredentials] = auth):
            self._authenticate(credentials)
            model = self._model(model_name)
            form_data = await request.form()
            columns = {column.key: column for column in inspect(model).columns if not column.primary_key}
            values = {key: value for key, value in form_data.items() if key in columns}
            with get_session() as session:
                row = model(**values)
                session.add(row)
                session.commit()
            return RedirectResponse(url=f"/admin/{model_name}", status_code=303)

        @router.post("/{model_name}/records")
        async def create_record(model_name: str, request: Request, credentials: Optional[HTTPBasicCredentials] = auth):
            self._authenticate(credentials)
            model = self._model(model_name)
            data = await request.json()
            columns = set(self._columns(model))
            values = {key: value for key, value in data.items() if key in columns and key != "id"}
            with get_session() as session:
                row = model(**values)
                session.add(row)
                session.commit()
                session.refresh(row)
                return self._serialize_row(row, self._columns(model))

        @router.put("/{model_name}/records/{record_id}")
        async def update_record(model_name: str, record_id: int, request: Request, credentials: Optional[HTTPBasicCredentials] = auth):
            self._authenticate(credentials)
            model = self._model(model_name)
            data = await request.json()
            columns = set(self._columns(model))
            with get_session() as session:
                row = session.get(model, record_id)
                if row is None:
                    raise HTTPException(status_code=404, detail="Record not found")
                for key, value in data.items():
                    if key in columns and key != "id":
                        setattr(row, key, value)
                session.commit()
                session.refresh(row)
                return self._serialize_row(row, self._columns(model))

        @router.delete("/{model_name}/records/{record_id}")
        async def delete_record(model_name: str, record_id: int, credentials: Optional[HTTPBasicCredentials] = auth):
            self._authenticate(credentials)
            model = self._model(model_name)
            with get_session() as session:
                row = session.get(model, record_id)
                if row is None:
                    raise HTTPException(status_code=404, detail="Record not found")
                session.delete(row)
                session.commit()
            return {"deleted": record_id}

        return router

    def mount(self, app: Any, prefix: str = "/admin") -> Any:
        """Mount the admin router on a FastAPI application."""
        normalized_prefix = "/" + prefix.strip("/")
        app.include_router(self.router(normalized_prefix))

        # Keep the dashboard route explicit. This also protects against
        # framework/version differences where an empty APIRouter path with a
        # prefix is normalized as only the trailing-slash variant.
        registered_paths = {getattr(route, "path", "") for route in app.routes}
        if normalized_prefix not in registered_paths:
            auth = Depends(self.security)

            async def explicit_dashboard(credentials: Optional[HTTPBasicCredentials] = auth):
                self._authenticate(credentials)
                return HTMLResponse(self._dashboard())

            app.add_api_route(
                normalized_prefix,
                explicit_dashboard,
                methods=["GET"],
                response_class=HTMLResponse,
                name="nextpy_admin_dashboard",
            )
        return app


admin = AdminSite()


def register(model: Type[Any], name: Optional[str] = None) -> Type[Any]:
    """Register a model on the default admin site."""
    return admin.register(model, name)
