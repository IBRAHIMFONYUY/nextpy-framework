"""
NextPy Full-Stack Demo
Demonstrates enhanced client-server communication with server actions and state synchronization
"""

import json
import nextpy as nx
from nextpy.psx import component, useState, useEffect, create_onclick, render_psx_component
from nextpy.server_actions import server_action, FormValidator, ActionSchema
from nextpy.db import get_session, Todo
from nextpy.websocket import manager as ws_manager


# Server Actions - Define backend functions that can be called from client
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
            "created_at": todo.created_at.isoformat() if todo.created_at else None
        }
        
        await ws_manager.publish("todos", {
            "type": "TODO_CHANGED",
            "action": "created",
            "data": todo_data
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
            "updated_at": todo.updated_at.isoformat() if todo.updated_at else None
        }
        
        await ws_manager.publish("todos", {
            "type": "TODO_CHANGED",
            "action": "updated",
            "data": todo_data
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
            "data": {"id": todo_id}
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
                "updated_at": todo.updated_at.isoformat() if todo.updated_at else None
            }
            for todo in todos
        ]
    finally:
        if not session:
            db.close()


# Validation schema for the todo form
todo_form_schema = ActionSchema(
    title={
        'type': str,
        'required': True,
        'validator': lambda x: (len(x.strip()) > 0, "Title cannot be empty")
    }
)


@component
def FullStackDemo(props=None):
    """Enhanced full-stack demo with server actions and state sync - PSX Compatible with Generic CRUD"""
    props = props or {}
    
    # Server-side data fetching
    server_todos = props.get("todos", [])
    
    # Generic CRUD configuration using Server Actions
    crud_config = {
        "createAction": "create_todo",
        "updateAction": "toggle_todo", 
        "deleteAction": "delete_todo",
        "resource": "todos",
        "wsChannel": "todos",
        "messageType": "TODO_CHANGED",
        "fieldMapping": {
            "title": "span"
        },
        "idParam": "todo_id",
        "deleteConfirm": "psx",
        "createReset": True
    }
    crud=json.dumps(crud_config)
    
    # PSX state for delete confirmation modal
    [show_modal, setShowModal] = useState(False)
    [pending_id, setPendingId] = useState(None)
    [pending_title, setPendingTitle] = useState("")
    
    # Create handlers for modal buttons (JS functions registered at runtime)
    confirm_delete = create_onclick(lambda e: confirmDeleteModal())  # type: ignore[name-defined]
    cancel_delete = create_onclick(lambda e: hideDeleteModal())  # type: ignore[name-defined]
    
    return (
        <main data-nextpy-crud={crud} class="min-h-screen px-4 py-12 bg-gradient-to-br from-gray-50 to-gray-100">
            <div class="max-w-3xl mx-auto">
                <div class="mb-12 text-center">
                    <h1 class="mb-4 text-4xl font-bold text-gray-900">
                        NextPy Full-Stack Demo
                    </h1>
                    <p class="text-lg text-gray-600">
                        Enhanced client-server communication with server actions and real-time sync
                    </p>
                </div>

                <div class="p-6 mb-8 bg-white shadow-lg rounded-xl">
                    <h2 class="mb-4 text-xl font-semibold text-gray-900">Server Actions Available</h2>
                    <ul class="space-y-2 text-gray-600">
                        <li>• <code>create_todo</code> - Create new todo items</li>
                        <li>• <code>toggle_todo</code> - Toggle todo completion</li>
                        <li>• <code>delete_todo</code> - Delete todo items</li>
                        <li>• <code>get_todos</code> - Fetch all todos</li>
                    </ul>
                </div>

                <div class="p-6 mb-8 bg-white shadow-lg rounded-xl">
                    <div class="flex items-center justify-between mb-4">
                        <h2 class="text-xl font-semibold text-gray-900">Interactive Todos (Generic CRUD)</h2>
                        <span data-nextpy-status class="text-sm text-gray-500">Connecting...</span>
                    </div>
                    
                    <form data-nextpy-action="create" class="flex gap-2 mb-6">
                        <input 
                            data-nextpy-field="title" 
                            required 
                            maxlength="255" 
                            placeholder="What needs doing?" 
                            class="flex-1 min-w-0 px-3 py-2 border rounded-lg border-slate-300 focus:border-blue-500 focus:outline-none" 
                        />
                        <button type="submit" class="px-4 py-2 font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700">Add</button>
                    </form>
                    
                    <p data-nextpy-error class="hidden p-3 mb-4 text-sm text-red-700 rounded-lg bg-red-50"></p>
                    
                    <ul data-nextpy-list class="space-y-3">
                        {for todo in server_todos:
                            <li data-nextpy-item={todo["id"]} class="flex items-center gap-4 p-4 rounded-lg bg-gray-50">
                                <input 
                                    data-nextpy-toggle={todo["id"]} 
                                    type="checkbox" 
                                    checked={todo["completed"]} 
                                    aria-label="Complete todo" 
                                    class="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                                />
                                <span class={"flex-1 " + (todo["completed"] and "line-through text-gray-400" or "text-gray-900")}>
                                    {todo["title"]}
                                </span>
                                <button 
                                    data-nextpy-delete={todo["id"]} 
                                    type="button" 
                                    class="text-sm font-medium text-red-600 hover:text-red-800"
                                >
                                    Delete
                                </button>
                            </li>
                        }
                    </ul>
                </div>

                <div class="grid grid-cols-1 gap-6 mt-8 md:grid-cols-3">
                    <div class="p-6 bg-white rounded-lg shadow">
                        <h3 class="mb-2 font-semibold text-gray-900">Server Actions</h3>
                        <p class="text-sm text-gray-600">
                            CRUD operations use server actions - no API endpoints needed
                        </p>
                    </div>
                    
                    <div class="p-6 bg-white rounded-lg shadow">
                        <h3 class="mb-2 font-semibold text-gray-900">Pure Python</h3>
                        <p class="text-sm text-gray-600">
                            Define backend logic with @server_action decorator
                        </p>
                    </div>
                    
                    <div class="p-6 bg-white rounded-lg shadow">
                        <h3 class="mb-2 font-semibold text-gray-900">Generic</h3>
                        <p class="text-sm text-gray-600">
                            Works for any model - posts, users, products, etc.
                        </p>
                    </div>
                </div>

                <div class="p-6 mt-8 font-mono text-sm text-green-400 bg-gray-900 rounded-lg">
                    <h3 class="mb-4 text-white">Server Actions CRUD Configuration:</h3>
                    <pre>
# Configure CRUD using Server Actions
crud_config = {
    "createAction": "create_post",    # Server action name
    "updateAction": "update_post",    # Server action name
    "deleteAction": "delete_post",    # Server action name
    "resource": "posts",             # Resource name
    "wsChannel": "posts",            # WebSocket channel
    "messageType": "POST_CHANGED",   # Message type
    "fieldMapping": {"title": "span", "content": "div.content"},
    "idParam": "post_id",
    "deleteConfirm": "Delete this post?"
}

# Server Actions are defined in Python
@server_action(name="create_post")
async def create_post(title: str, content: str, session=None):
    post = Post(title=title, content=content)
    session.add(post)
    session.commit()
    return {"id": post.id, "title": title, "content": content}

# Use in PSX - no API endpoints needed!
&lt;main data-nextpy-crud={json.dumps(crud_config)}&gt;
    &lt;form data-nextpy-action="create"&gt;
        &lt;input data-nextpy-field="title" /&gt;
        &lt;input data-nextpy-field="content" /&gt;
        &lt;button type="submit"&gt;Create&lt;/button&gt;
    &lt;/form&gt;
    &lt;ul data-nextpy-list&gt;
        {for post in posts:
            &lt;li data-nextpy-item={post["id"]}&gt;
                &lt;span&gt;{post["title"]}&lt;/span&gt;
                &lt;button data-nextpy-delete={post["id"]}&gt;Delete&lt;/button&gt;
            &lt;/li&gt;
        }
    &lt;/ul&gt;
&lt;/main&gt;
                    </pre>
                </div>

                <div data-delete-modal class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 backdrop-blur-sm hidden">
                    <div class="w-full max-w-sm p-6 bg-white rounded-xl shadow-xl">
                        <h3 class="text-lg font-semibold text-gray-900 mb-2">Confirm Delete</h3>
                        <p data-bind="textContent:pending_title" class="text-sm text-gray-600 mb-6">this item</p>
                        <div class="flex justify-end gap-3">
                            <button 
                                type="button" 
                                onclick={cancel_delete}
                                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                            >
                                Cancel
                            </button>
                            <button 
                                type="button" 
                                onclick={confirm_delete}
                                class="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    )


def getServerSideProps(context):
    """Server-side data fetching"""
    # Fetch todos from database for initial render
    with get_session() as db:
        todos = db.query(Todo).order_by(Todo.created_at.desc()).limit(10).all()
        
        return {
            "props": {
                "title": "NextPy Full-Stack Demo",
                "description": "Enhanced client-server communication with server actions and real-time sync",
                "todos": [
                    {
                        "id": todo.id,
                        "title": todo.title,
                        "completed": todo.completed,
                        "created_at": todo.created_at.isoformat() if todo.created_at else None
                    }
                    for todo in todos
                ]
            }
        }
    
    


default = FullStackDemo