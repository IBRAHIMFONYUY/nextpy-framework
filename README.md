<div align="center">

<img src="./public/images/icon.png" alt="NextPy Logo" width="120"/>



# NextPy Framework

### The Full-Stack Python Framework

![PyPI](https://img.shields.io/pypi/v/nextpy-framework)
![Python](https://img.shields.io/pypi/pyversions/nextpy-framework)
![License](https://img.shields.io/github/license/RahimStudios/nextpy-framework)
![Stars](https://img.shields.io/github/stars/RahimStudios/nextpy-framework)





Build modern web applications using Python, PSX, file-based routing, server-side rendering, static generation, React-style hooks, and integrated AI development tools.

[Documentation](https://nextpy.dev) •
[Examples](https://nextpy.dev/examples) •
[Discord](https://discord.gg/nextpy) •
[GitHub Discussions](https://github.com/RahimStudios/nextpy/discussions)

</div




---

## Getting Started

NextPy is a Python-first full-stack framework inspired by the developer experience of Next.js while introducing powerful innovations such as:

* PSX (Python Syntax Extension)
* File-based routing
* Server-side rendering (SSR)
* Static site generation (SSG)
* API routes
* React-style hooks in Python
* Built-in AI coding assistant
* Modern CLI tooling
* Enterprise-ready architecture

### Installation

```bash
pip install nextpy-framework
```

### Create a Project

```bash
nextpy create my-app
cd my-app
nextpy dev
```

Visit:

```text
http://localhost:8000
```

---

## Why NextPy?

### Python First

Build full-stack applications without switching languages.

### PSX

Write component-based user interfaces using NextPy's Python Syntax Extension.

### Enhanced Full-Stack Architecture (New in v5.0)

NextPy v5.0 introduces revolutionary client-server communication:

- **Server Actions**: Call Python functions directly from client JavaScript
- **State Synchronization**: Real-time state sync between client and server
- **Type-Safe APIs**: Automatic validation and type checking
- **WebSocket Integration**: Built-in real-time updates
- **Database-Backed State**: Persistent state management

```python
# Define a server action
from nextpy.server_actions import server_action

@server_action()
async def create_todo(title: str, session=None):
    todo = Todo(title=title, completed=False)
    session.add(todo)
    session.commit()
    return {"id": todo.id, "title": title}
```

And call it from client JavaScript:

```javascript
const result = await window.nextpy.executeAction("create_todo", {
    title: "Learn NextPy"
});
```

### AI Native

NextPy includes an integrated AI coding assistant:

```bash
nextpy ai
```

Chat mode:

```bash
nextpy ai chatbot
```

Agent mode:

```bash
nextpy ai agent
```

Generate complete applications:

```bash
nextpy ai create ecommerce app
```

### Full-Stack by Default

* Frontend with PSX components
* Backend with FastAPI
* Server Actions for client-server communication
* API Routes with automatic routing
* Database Integration with SQLAlchemy
* State Synchronization with WebSocket support
* Authentication & Authorization
* Real-time updates
* Everything in one framework

---

## Full-Stack Capabilities

NextPy v5.0 provides enhanced full-stack features:

- **Server Actions**: Direct client-to-server function calls
- **State Synchronization**: Real-time state management
- **Type-Safe APIs**: Automatic validation and type checking
- **WebSocket Integration**: Built-in real-time updates
- **Database-Backed State**: Persistent state management

[Read the Full-Stack Guide](FULLSTACK_GUIDE.md)

---

## Example

```python
from nextpy.psx import component, useState, create_onclick

@component
def Home(props=None):
    props = props or {}
    [count, setCount] = useState(0)
    handle_count = create_onclick(lambda e: setCount(count + 1))

    return (
        <div>
            <h1>Welcome to NextPy</h1>

            <button create_onclick={handle_count}>
                Count: {count}
            </button>
        </div>
    )

default = Home
```

---

## Documentation

Visit the official documentation:

https://nextpy.dev/docs

Documentation includes:

* Getting Started
* Routing
* PSX
* Components
* Hooks
* Data Fetching
* API Routes
* Deployment
* AI Assistant
* CLI Reference

---

## Community

The NextPy community can be found on GitHub Discussions where you can ask questions, share projects, suggest features, and connect with other developers.

* GitHub Discussions
* Discord Community
* X (Twitter)
* YouTube

Please read and follow our Code of Conduct when participating in community spaces.

---

## Contributing

Contributions are welcome and greatly appreciated.

Before contributing, please read:

* Contribution Guidelines
* Code of Conduct

- Go through this to know exactly what each file does https://github.com/RahimStudios/nextpy-framework/blob/main/.nextpy_framework/nextpy/docs/COMPLETE_FILE_DOCUMENTATION.md 

- Go through this to see all what is implemented fully, partially and what is not, so it can guide you on anywhere to start 
https://github.com/RahimStudios/nextpy-framework/blob/main/.nextpy_framework/nextpy/docs/FRAMEWORK_ANALYSIS.md

Good first issues are available for new contributors looking to get involved.

---

## Security

If you discover a security vulnerability, please do not create a public issue.

Instead, contact:

[security@rahimstudios.com](mailto:security@rahimstudios.com)

We will investigate and respond as quickly as possible.

---

## License

Licensed under the MIT License.

---

<div align="center">

### Built with ❤️ by RahimStudios

The future of AI-native Python development.

</div>
