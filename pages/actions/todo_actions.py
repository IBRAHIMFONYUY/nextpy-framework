"""
Todo Server Actions
CRUD operations for Todo items using NextPy server actions.
"""

import nextpy as nx
from nextpy.server_actions import server_action, ActionSchema
from nextpy.db import get_session, Todo
from nextpy.websocket import manager as ws_manager



@server_action(name="create_todo")
async def create_todo(title: str, session=None):
    """Create a new todo item"""
    if not title or not title.strip():
        raise nx.server_actions.ValidationError("title", "Title cannot be empty")

    db = session or get_session()
    try:
        todo = Todo(title=title.strip(), completed=False)
        db.add(todo)
        db.commit()
        db.refresh(todo)

        todo_data = {
            "id": todo.id,
            "title": todo.title,
            "completed": todo.completed,
            "created_at": todo.created_at.isoformat() if todo.created_at else None,
        }

        await ws_manager.publish("todos", {
            "type": "TODO_CHANGED",
            "action": "created",
            "data": todo_data,
        })

        return todo_data
    finally:
        if not session:
            db.close()


@server_action(name="toggle_todo")
async def toggle_todo(todo_id: int, session=None):
    """Toggle todo completion status"""
    db = session or get_session()
    try:
        todo = db.get(Todo, todo_id)
        if not todo:
            raise nx.server_actions.ServerActionError("Todo not found", "NOT_FOUND")

        todo.completed = not todo.completed
        db.commit()
        db.refresh(todo)

        todo_data = {
            "id": todo.id,
            "title": todo.title,
            "completed": todo.completed,
            "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
        }

        await ws_manager.publish("todos", {
            "type": "TODO_CHANGED",
            "action": "updated",
            "data": todo_data,
        })

        return todo_data
    finally:
        if not session:
            db.close()


@server_action(name="delete_todo")
async def delete_todo(todo_id: int, session=None):
    """Delete a todo item"""
    db = session or get_session()
    try:
        todo = db.get(Todo, todo_id)
        if not todo:
            raise nx.server_actions.ServerActionError("Todo not found", "NOT_FOUND")

        db.delete(todo)
        db.commit()

        await ws_manager.publish("todos", {
            "type": "TODO_CHANGED",
            "action": "deleted",
            "data": {"id": todo_id},
        })

        return {"id": todo_id, "deleted": True}
    finally:
        if not session:
            db.close()


@server_action(name="get_todos")
async def get_todos(session=None):
    """Get all todo items"""
    db = session or get_session()
    try:
        todos = db.query(Todo).order_by(Todo.created_at.desc()).all()

        return [
            {
                "id": todo.id,
                "title": todo.title,
                "completed": todo.completed,
                "created_at": todo.created_at.isoformat() if todo.created_at else None,
                "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
            }
            for todo in todos
        ]
    finally:
        if not session:
            db.close()


@server_action(name="get_todo_stats")
async def get_todo_stats(session=None):
    """Get todo statistics for the useFetch demo"""
    db = session or get_session()
    try:
        todos = db.query(Todo).all()
        total = len(todos)
        completed = sum(1 for t in todos if t.completed)
        pending = total - completed
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": round(completed / total * 100, 1) if total > 0 else 0,
        }
    finally:
        if not session:
            db.close()


# Validation schema for the todo form
todo_form_schema = ActionSchema(
    title={
        "type": str,
        "required": True,
        "validator": lambda x: (len(x.strip()) > 0, "Title cannot be empty"),
    }
)
