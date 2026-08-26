"""Persistent todo API with realtime WebSocket broadcasts."""

from datetime import datetime
from typing import Any, Dict

from nextpy.db import Todo, get_session
from nextpy.websocket import manager
from nextpy.auth import AuthManager
from fastapi import HTTPException


def _require_api_auth(request: Any) -> None:
    """Require a bearer token when TODO_API_AUTH is enabled."""
    import os
    if os.getenv("TODO_API_AUTH", "false").lower() not in {"1", "true", "yes", "on"}:
        return
    token = AuthManager.get_token_from_request(request)
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    AuthManager.verify_token(token)


def _as_bool(value: Any) -> bool:
    """Parse JSON and form-style boolean values consistently."""
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _serialize(todo: Todo) -> Dict[str, Any]:
    return {
        "id": todo.id,
        "title": todo.title,
        "completed": todo.completed,
        "created_at": todo.created_at.isoformat() if todo.created_at else None,
        "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
    }


async def _broadcast(action: str, todo: Todo) -> None:
    await manager.publish("todos", {
        "type": "TODO_CHANGED",
        "action": action,
        "todo": _serialize(todo),
    })


async def get(request, params):
    _require_api_auth(request)
    with get_session() as session:
        todos = list(session.query(Todo).order_by(Todo.created_at.desc()).all())
    return {"todos": [_serialize(todo) for todo in todos]}


async def post(request, params):
    _require_api_auth(request)
    data = await request.json()
    title = str(data.get("title", "")).strip()
    if not title:
        return {"error": "title is required"}
    with get_session() as session:
        todo = Todo(title=title, completed=_as_bool(data.get("completed", False)))
        session.add(todo)
        session.commit()
        session.refresh(todo)
        result = _serialize(todo)
    await _broadcast("created", todo)
    return {"todo": result}


async def put(request, params):
    _require_api_auth(request)
    data = await request.json()
    todo_id = data.get("id")
    if todo_id is None:
        return {"error": "id is required"}
    with get_session() as session:
        todo = session.get(Todo, int(todo_id))
        if todo is None:
            return {"error": "todo not found"}
        if "title" in data:
            title = str(data["title"]).strip()
            if not title:
                return {"error": "title cannot be empty"}
            todo.title = title
        if "completed" in data:
            todo.completed = _as_bool(data["completed"])
        todo.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(todo)
        result = _serialize(todo)
    await _broadcast("updated", todo)
    return {"todo": result}


async def delete(request, params):
    _require_api_auth(request)
    data = await request.json()
    todo_id = data.get("id")
    if todo_id is None:
        return {"error": "id is required"}
    with get_session() as session:
        todo = session.get(Todo, int(todo_id))
        if todo is None:
            return {"error": "todo not found"}
        result = {"id": todo.id}
        session.delete(todo)
        session.commit()
    await manager.publish("todos", {"type": "TODO_CHANGED", "action": "deleted", "todo": result})
    return {"deleted": todo_id}
