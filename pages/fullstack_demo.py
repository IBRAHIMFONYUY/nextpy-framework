"""
NextPy Full-Stack Demo
Demonstrates enhanced client-server communication with server actions and state synchronization
"""

import json
import nextpy as nx
from nextpy.psx import component, useState, useEffect, create_onclick
from nextpy.server_actions import server_action, FormValidator, ActionSchema
from nextpy.db import get_session, Todo


# Server Actions - Define backend functions that can be called from client
@server_action(name="create_todo")
async def create_todo(title: str, session=None):
    """Create a new todo item"""
    if not title or not title.strip():
        raise nx.server_actions.ValidationError("title", "Title cannot be empty")
    
    with session if session else get_session() as db:
        todo = Todo(title=title.strip(), completed=False)
        db.add(todo)
        db.commit()
        db.refresh(todo)
        
        return {
            "id": todo.id,
            "title": todo.title,
            "completed": todo.completed,
            "created_at": todo.created_at.isoformat() if todo.created_at else None
        }


@server_action(name="toggle_todo")
async def toggle_todo(todo_id: int, session=None):
    """Toggle todo completion status"""
    with session if session else get_session() as db:
        todo = db.get(Todo, todo_id)
        if not todo:
            raise nx.server_actions.ServerActionError("Todo not found", "NOT_FOUND")
        
        todo.completed = not todo.completed
        db.commit()
        db.refresh(todo)
        
        return {
            "id": todo.id,
            "title": todo.title,
            "completed": todo.completed,
            "updated_at": todo.updated_at.isoformat() if todo.updated_at else None
        }


@server_action(name="delete_todo")
async def delete_todo(todo_id: int, session=None):
    """Delete a todo item"""
    with session if session else get_session() as db:
        todo = db.get(Todo, todo_id)
        if not todo:
            raise nx.server_actions.ServerActionError("Todo not found", "NOT_FOUND")
        
        db.delete(todo)
        db.commit()
        
        return {"id": todo_id, "deleted": True}


@server_action(name="get_todos")
async def get_todos(session=None):
    """Get all todo items"""
    with session if session else get_session() as db:
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
        "updateBody": lambda item_id, completed: {"todo_id": int(item_id)},
        "deleteBody": lambda item_id: {"todo_id": int(item_id)},
        "deleteConfirm": "Delete this todo?"
    }
    
    return (
        <main data-nextpy-crud={json.dumps(crud_config)} class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12 px-4">
            <div class="max-w-3xl mx-auto">
                <div class="text-center mb-12">
                    <h1 class="text-4xl font-bold text-gray-900 mb-4">
                        NextPy Full-Stack Demo
                    </h1>
                    <p class="text-lg text-gray-600">
                        Enhanced client-server communication with server actions and real-time sync
                    </p>
                </div>

                <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
                    <h2 class="text-xl font-semibold text-gray-900 mb-4">Server Actions Available</h2>
                    <ul class="space-y-2 text-gray-600">
                        <li>• <code>create_todo</code> - Create new todo items</li>
                        <li>• <code>toggle_todo</code> - Toggle todo completion</li>
                        <li>• <code>delete_todo</code> - Delete todo items</li>
                        <li>• <code>get_todos</code> - Fetch all todos</li>
                    </ul>
                </div>

                <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
                    <div class="flex justify-between items-center mb-4">
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
                            <li data-nextpy-item={todo["id"]} class="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
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
                                    class="text-red-600 hover:text-red-800 text-sm font-medium"
                                >
                                    Delete
                                </button>
                            </li>
                        }
                    </ul>
                </div>

                <div class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-white rounded-lg shadow p-6">
                        <h3 class="font-semibold text-gray-900 mb-2">Server Actions</h3>
                        <p class="text-sm text-gray-600">
                            CRUD operations use server actions - no API endpoints needed
                        </p>
                    </div>
                    
                    <div class="bg-white rounded-lg shadow p-6">
                        <h3 class="font-semibold text-gray-900 mb-2">Pure Python</h3>
                        <p class="text-sm text-gray-600">
                            Define backend logic with @server_action decorator
                        </p>
                    </div>
                    
                    <div class="bg-white rounded-lg shadow p-6">
                        <h3 class="font-semibold text-gray-900 mb-2">Generic</h3>
                        <p class="text-sm text-gray-600">
                            Works for any model - posts, users, products, etc.
                        </p>
                    </div>
                </div>

                <div class="mt-8 bg-gray-900 rounded-lg p-6 text-green-400 font-mono text-sm">
                    <h3 class="text-white mb-4">Server Actions CRUD Configuration:</h3>
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
    "updateBody": lambda id, data: {"post_id": id, **data},
    "deleteBody": lambda id: {"post_id": id},
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