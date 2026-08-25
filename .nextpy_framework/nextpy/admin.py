"""
Small, protected SQLAlchemy admin site for NextPy applications.
Enhanced UI with modern light theme and interactive elements.
"""

import os
from datetime import date, datetime
from decimal import Decimal
from html import escape
from typing import Any, Dict, Iterable, Optional, Type

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import Boolean, Date, DateTime, Float, Integer, Numeric, Text, inspect, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeMeta

from .db import get_session


class AdminSite:
    """Register SQLAlchemy models and expose a small Django-style admin with a modern UI."""

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

    @staticmethod
    def _editable_columns(model: Type[Any]) -> list[Any]:
        """Return fields a user should provide in the create form."""
        return [
            column for column in inspect(model).columns
            if not column.primary_key and column.default is None and column.server_default is None
        ]

    @staticmethod
    def _coerce_value(column: Any, value: Any) -> Any:
        """Convert HTTP form values to the type expected by SQLAlchemy."""
        if value is None or value == "":
            return None
        column_type = column.type
        if isinstance(column_type, Boolean):
            if isinstance(value, bool):
                return value
            normalized = str(value).strip().lower()
            if normalized in {"1", "true", "yes", "on"}:
                return True
            if normalized in {"0", "false", "no", "off", ""}:
                return False
            raise ValueError(f"{column.key} must be true or false")
        if isinstance(column_type, Integer):
            return int(value)
        if isinstance(column_type, (Float, Numeric)):
            return float(value)
        if isinstance(column_type, DateTime):
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if isinstance(column_type, Date):
            return date.fromisoformat(str(value))
        if isinstance(column_type, (Text,)):
            return str(value)
        return value

    # ------------------------------------------------------------------
    # UI Helpers
    # ------------------------------------------------------------------
    def _sidebar_html(self, active_model: Optional[str] = None) -> str:
        """Generate the sidebar with model links and active state."""
        links = []
        for name in sorted(self.models):
            active_class = ' class="active"' if name == active_model else ""
            links.append(
                f'<a href="/admin/{escape(name)}"{active_class}>'
                f'<span class="model-icon">{escape(name[0].upper())}</span>'
                f'<span>{escape(name)}</span>'
                f'</a>'
            )
        return f"""
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <a href="/admin" class="brand">
                    <span class="logo">N</span>
                    <span>{escape(self.title)}</span>
                </a>
                <button class="sidebar-toggle" onclick="toggleSidebar()" aria-label="Toggle navigation">☰</button>
            </div>
            <nav>
                {''.join(links)}
            </nav>
        </aside>
        """

    def _topbar_html(self, page_title: str) -> str:
        """Generate a simple top bar with page title."""
        return f"""
        <header class="topbar">
            <h1>{escape(page_title)}</h1>
        </header>
        """

    def _page(self, heading: str, body: str, active_model: Optional[str] = None) -> str:
        """Wrap content with the full admin layout (sidebar + topbar + body)."""
        return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(heading)} | {escape(self.title)}</title>
    <style>
        :root {{
            --bg: #f8fafc;
            --surface: #ffffff;
            --text: #0f172a;
            --text-secondary: #475569;
            --border: #e2e8f0;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --danger: #dc2626;
            --danger-hover: #b91c1c;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --radius: 0.5rem;
            --transition: all 0.2s ease;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.5;
            display: flex;
            min-height: 100vh;
        }}
        a {{
            color: var(--primary);
            text-decoration: none;
            transition: var(--transition);
        }}
        a:hover {{
            color: var(--primary-hover);
        }}

        /* Sidebar */
        .sidebar {{
            width: 260px;
            background: var(--surface);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            position: fixed;
            top: 0;
            left: 0;
            bottom: 0;
            z-index: 100;
            transition: transform 0.3s ease;
        }}
        .sidebar-header {{
            padding: 1.25rem 1rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .brand {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 600;
            color: var(--text);
        }}
        .brand .logo {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            background: var(--primary);
            color: white;
            border-radius: 8px;
            font-size: 1.2rem;
            font-weight: 700;
        }}
        .sidebar nav {{
            padding: 0.5rem;
            overflow-y: auto;
            flex: 1;
        }}
        .sidebar nav a {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.625rem 0.75rem;
            border-radius: 8px;
            color: var(--text-secondary);
            font-weight: 500;
            margin-bottom: 2px;
        }}
        .sidebar nav a:hover {{
            background: #f1f5f9;
            color: var(--text);
        }}
        .sidebar nav a.active {{
            background: #eff6ff;
            color: var(--primary);
            font-weight: 600;
        }}
        .model-icon {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            border-radius: 6px;
            background: #e2e8f0;
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 600;
            flex-shrink: 0;
        }}
        .sidebar-toggle {{
            display: none;
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text-secondary);
        }}

        /* Main content */
        .main {{
            flex: 1;
            margin-left: 260px;
            padding: 1.5rem 2rem;
            transition: margin-left 0.3s ease;
        }}
        .topbar {{
            margin-bottom: 1.5rem;
        }}
        .topbar h1 {{
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: -0.025em;
        }}

        /* Cards */
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.25rem;
            box-shadow: var(--shadow-sm);
            transition: var(--transition);
        }}
        .card:hover {{
            box-shadow: var(--shadow);
            transform: translateY(-2px);
            border-color: #cbd5e1;
        }}
        .card a {{
            display: block;
            color: var(--text);
            font-weight: 600;
            font-size: 1.1rem;
        }}
        .card .model-icon {{
            width: 40px;
            height: 40px;
            font-size: 1.2rem;
            margin-bottom: 0.75rem;
            background: #e0e7ff;
            color: var(--primary);
        }}

        /* Buttons */
        .btn {{
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 500;
            border: 1px solid transparent;
            cursor: pointer;
            transition: var(--transition);
            text-align: center;
            font-size: 0.9rem;
        }}
        .btn-primary {{
            background: var(--primary);
            color: white;
        }}
        .btn-primary:hover {{
            background: var(--primary-hover);
            color: white;
        }}
        .btn-danger {{
            background: var(--danger);
            color: white;
        }}
        .btn-danger:hover {{
            background: var(--danger-hover);
            color: white;
        }}
        .btn-outline {{
            background: transparent;
            border-color: var(--border);
            color: var(--text);
        }}
        .btn-outline:hover {{
            background: #f1f5f9;
        }}

        /* Forms */
        form {{
            margin: 1rem 0;
        }}
        label {{
            display: block;
            margin-bottom: 1rem;
            font-weight: 500;
            color: var(--text-secondary);
        }}
        input, textarea, select {{
            width: 100%;
            padding: 0.5rem 0.75rem;
            margin-top: 0.25rem;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: var(--surface);
            color: var(--text);
            font-size: 0.9rem;
            transition: var(--transition);
        }}
        input:focus, textarea:focus, select:focus {{
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }}
        input[type="checkbox"] {{
            width: auto;
            margin-right: 0.5rem;
        }}
        .form-actions {{
            display: flex;
            gap: 0.5rem;
            margin-top: 1.5rem;
        }}

        /* Tables */
        .table-container {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow-sm);
            overflow: auto;
            margin-top: 1rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}
        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: #f8fafc;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
            position: sticky;
            top: 0;
        }}
        tr:hover td {{
            background: #f8fafc;
        }}
        .actions-cell {{
            white-space: nowrap;
        }}
        .actions-cell a {{
            margin-right: 0.5rem;
        }}

        /* Search bar */
        .search-form {{
            display: flex;
            gap: 0.5rem;
            margin: 1rem 0;
        }}
        .search-form input {{
            flex: 1;
            margin-top: 0;
        }}

        /* Modal */
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
        }}
        .modal-overlay.active {{
            opacity: 1;
            pointer-events: all;
        }}
        .modal {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: var(--shadow);
            max-width: 400px;
            width: 90%;
            text-align: center;
        }}
        .modal h2 {{
            margin-bottom: 1rem;
        }}
        .modal .form-actions {{
            justify-content: center;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .sidebar {{
                transform: translateX(-100%);
            }}
            .sidebar.open {{
                transform: translateX(0);
            }}
            .sidebar-toggle {{
                display: block;
            }}
            .main {{
                margin-left: 0;
                padding: 1rem;
            }}
            .card-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    {self._sidebar_html(active_model)}
    <div class="main">
        {self._topbar_html(heading)}
        <div class="content">
            {body}
        </div>
    </div>

    <!-- Modal for delete confirmation -->
    <div class="modal-overlay" id="confirm-modal">
        <div class="modal">
            <h2>Confirm Deletion</h2>
            <p>Are you sure you want to delete this record? This action cannot be undone.</p>
            <div class="form-actions">
                <button class="btn btn-outline" onclick="closeModal()">Cancel</button>
                <button class="btn btn-danger" id="confirm-delete-btn">Delete</button>
            </div>
        </div>
    </div>

    <script>
        // Sidebar toggle for mobile
        function toggleSidebar() {{
            document.getElementById('sidebar').classList.toggle('open');
        }}

        // Modal handling for delete confirmation
        let deleteForm = null;
        function confirmDelete(event, form) {{
            event.preventDefault();
            deleteForm = form;
            document.getElementById('confirm-modal').classList.add('active');
        }}
        document.getElementById('confirm-delete-btn').addEventListener('click', function() {{
            if (deleteForm) {{
                deleteForm.submit();
            }}
            closeModal();
        }});
        function closeModal() {{
            document.getElementById('confirm-modal').classList.remove('active');
        }}
        // Close modal if clicking outside
        document.getElementById('confirm-modal').addEventListener('click', function(e) {{
            if (e.target === this) closeModal();
        }});

        // Client-side search filter (optional enhancement)
        document.addEventListener('DOMContentLoaded', function() {{
            const searchInput = document.getElementById('client-search');
            if (searchInput) {{
                searchInput.addEventListener('input', function() {{
                    const filter = this.value.toLowerCase();
                    const rows = document.querySelectorAll('tbody tr');
                    rows.forEach(row => {{
                        const text = row.textContent.toLowerCase();
                        row.style.display = text.includes(filter) ? '' : 'none';
                    }});
                }});
            }}
        }});
    </script>
</body>
</html>"""

    # ------------------------------------------------------------------
    # Route Handlers (mostly unchanged, only HTML strings updated)
    # ------------------------------------------------------------------
    def _dashboard(self) -> str:
        cards = []
        for name in sorted(self.models):
            cards.append(
                f'<div class="card">'
                f'<a href="/admin/{escape(name)}">'
                f'<span class="model-icon">{escape(name[0].upper())}</span>'
                f'{escape(name)}'
                f'</a>'
                f'</div>'
            )
        body = f"""
        <p style="color: var(--text-secondary); margin-bottom: 1rem;">Manage your database records</p>
        <div class="card-grid">
            {''.join(cards) if cards else '<p>No models registered yet.</p>'}
        </div>
        """
        return self._page("Dashboard", body)

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
                "<tr>" + "".join(
                    f'<td>{escape(str(self._serialize(getattr(row, column))))}</td>'
                    for column in columns
                ) + f"""<td class="actions-cell">
                    <a href="/admin/{escape(model_name)}/{row.id}" class="btn btn-outline" style="padding:0.25rem 0.5rem;">View</a>
                    <a href="/admin/{escape(model_name)}/{row.id}/edit" class="btn btn-outline" style="padding:0.25rem 0.5rem;">Edit</a>
                    <form method="post" action="/admin/{escape(model_name)}/{row.id}/delete" style="display:inline;" onsubmit="confirmDelete(event, this)">
                        <button type="submit" class="btn btn-danger" style="padding:0.25rem 0.5rem;">Delete</button>
                    </form>
                </td></tr>"""
                for row in objects
            ) or f'<tr><td colspan="{len(columns) + 1}">No records found</td></tr>'

            body = f"""
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
                <a href="/admin/{escape(model_name)}/new" class="btn btn-primary">+ Add Record</a>
                <form method="get" class="search-form">
                    <input type="text" name="q" placeholder="Search {escape(model_name)}..." value="{escape(query)}" id="client-search">
                    <button type="submit" class="btn btn-outline">Search</button>
                </form>
            </div>
            <div class="table-container">
                <table>
                    <thead><tr>{header}<th>Actions</th></tr></thead>
                    <tbody>{body_rows}</tbody>
                </table>
            </div>
            """
            return self._page(model_name, body, active_model=model_name)

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
            for column in self._editable_columns(model):
                required = " required" if not column.nullable else ""
                column_type = column.type
                if isinstance(column_type, Boolean):
                    control = f'<input type="checkbox" name="{escape(column.key)}" value="true">'
                elif isinstance(column_type, Text):
                    control = f'<textarea name="{escape(column.key)}"{required}></textarea>'
                elif isinstance(column_type, Integer):
                    control = f'<input type="number" name="{escape(column.key)}"{required}>'
                elif isinstance(column_type, (Float, Numeric)):
                    control = f'<input type="number" step="any" name="{escape(column.key)}"{required}>'
                elif isinstance(column_type, DateTime):
                    control = f'<input type="datetime-local" name="{escape(column.key)}"{required}>'
                elif isinstance(column_type, Date):
                    control = f'<input type="date" name="{escape(column.key)}"{required}>'
                else:
                    control = f'<input type="text" name="{escape(column.key)}"{required}>'
                fields.append(f'<label>{escape(column.key)}{control}</label>')
            form = "".join(fields) or "<p>This model has no editable fields.</p>"
            body = f"""
            <div style="max-width:600px;">
                <form method="post">
                    {form}
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Create</button>
                        <a href="/admin/{escape(model_name)}" class="btn btn-outline">Cancel</a>
                    </div>
                </form>
            </div>
            """
            return self._page(f"Add {model_name}", body, active_model=model_name)

        @router.get("/{model_name}/{record_id}", response_class=HTMLResponse)
        async def record_detail(model_name: str, record_id: int, credentials: Optional[HTTPBasicCredentials] = auth):
            self._authenticate(credentials)
            model = self._model(model_name)
            columns = self._columns(model)
            with get_session() as session:
                row = session.get(model, record_id)
            if row is None:
                raise HTTPException(status_code=404, detail="Record not found")
            values = "".join(
                f"<tr><th>{escape(column)}</th><td>{escape(str(self._serialize(getattr(row, column))))}</td></tr>"
                for column in columns
            )
            body = f"""
            <div style="display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:1rem;">
                <a href="/admin/{escape(model_name)}/{record_id}/edit" class="btn btn-primary">Edit</a>
                <form method="post" action="/admin/{escape(model_name)}/{record_id}/delete" style="display:inline;" onsubmit="confirmDelete(event, this)">
                    <button type="submit" class="btn btn-danger">Delete</button>
                </form>
                <a href="/admin/{escape(model_name)}" class="btn btn-outline">Back to list</a>
            </div>
            <div class="table-container">
                <table>{values}</table>
            </div>
            """
            return self._page(f"{model_name} #{record_id}", body, active_model=model_name)

        @router.get("/{model_name}/{record_id}/edit", response_class=HTMLResponse)
        async def edit_record_form(model_name: str, record_id: int, credentials: Optional[HTTPBasicCredentials] = auth):
            self._authenticate(credentials)
            model = self._model(model_name)
            with get_session() as session:
                row = session.get(model, record_id)
            if row is None:
                raise HTTPException(status_code=404, detail="Record not found")
            fields = []
            for column in self._editable_columns(model):
                value = getattr(row, column.key)
                required = " required" if not column.nullable else ""
                if isinstance(column.type, Boolean):
                    checked = " checked" if value else ""
                    control = f'<input type="checkbox" name="{escape(column.key)}" value="true"{checked}>'
                elif isinstance(column.type, Text):
                    control = f'<textarea name="{escape(column.key)}"{required}>{escape(str(value or ""))}</textarea>'
                else:
                    input_type = "number" if isinstance(column.type, (Integer, Float, Numeric)) else "text"
                    control = f'<input type="{input_type}" name="{escape(column.key)}" value="{escape(str(value or ""))}"{required}>'
                fields.append(f'<label>{escape(column.key)}{control}</label>')
            body = f"""
            <div style="max-width:600px;">
                <form method="post">
                    {''.join(fields)}
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Save Changes</button>
                        <a href="/admin/{escape(model_name)}/{record_id}" class="btn btn-outline">Cancel</a>
                    </div>
                </form>
            </div>
            """
            return self._page(f"Edit {model_name} #{record_id}", body, active_model=model_name)

        # Remaining handlers (POST, API endpoints) are unchanged except they don't render HTML.
        # They will still work as before.

        @router.post("/{model_name}/{record_id}/edit", response_class=HTMLResponse)
        async def submit_edit_record(model_name: str, record_id: int, request: Request, credentials: Optional[HTTPBasicCredentials] = auth):
            self._authenticate(credentials)
            model = self._model(model_name)
            form_data = await request.form()
            columns = {column.key: column for column in self._editable_columns(model)}
            try:
                with get_session() as session:
                    row = session.get(model, record_id)
                    if row is None:
                        raise HTTPException(status_code=404, detail="Record not found")
                    for key, column in columns.items():
                        raw_value = form_data.get(key)
                        if isinstance(column.type, Boolean) and raw_value is None:
                            raw_value = False
                        if raw_value is not None:
                            setattr(row, key, self._coerce_value(column, raw_value))
                    session.commit()
            except (ValueError, TypeError) as error:
                raise HTTPException(status_code=400, detail=f"Invalid value: {error}") from error
            except SQLAlchemyError as error:
                raise HTTPException(status_code=400, detail=f"Could not save record: {error}") from error
            return RedirectResponse(url=f"/admin/{model_name}/{record_id}", status_code=303)

        @router.post("/{model_name}/{record_id}/delete")
        async def delete_record_form(model_name: str, record_id: int, credentials: Optional[HTTPBasicCredentials] = auth):
            self._authenticate(credentials)
            model = self._model(model_name)
            with get_session() as session:
                row = session.get(model, record_id)
                if row is None:
                    raise HTTPException(status_code=404, detail="Record not found")
                session.delete(row)
                session.commit()
            return RedirectResponse(url=f"/admin/{model_name}", status_code=303)

        @router.post("/{model_name}/new", response_class=HTMLResponse)
        async def submit_new_record(model_name: str, request: Request, credentials: Optional[HTTPBasicCredentials] = auth):
            self._authenticate(credentials)
            model = self._model(model_name)
            form_data = await request.form()
            columns = {column.key: column for column in inspect(model).columns if not column.primary_key}
            values = {}
            try:
                for key, column in columns.items():
                    raw_value = form_data.get(key)
                    if isinstance(column.type, Boolean) and raw_value is None:
                        raw_value = False
                    if raw_value is not None:
                        values[key] = self._coerce_value(column, raw_value)
                with get_session() as session:
                    row = model(**values)
                    session.add(row)
                    session.commit()
            except (ValueError, TypeError) as error:
                raise HTTPException(status_code=400, detail=f"Invalid value: {error}") from error
            except SQLAlchemyError as error:
                raise HTTPException(status_code=400, detail=f"Could not save record: {error}") from error
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

        # Keep the dashboard route explicit.
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