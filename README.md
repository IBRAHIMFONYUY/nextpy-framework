# 🚀 NextPy Framework

**The Python web framework with exact Next.js syntax!** Build modern web applications with file-based routing, JSX-like components, React-like hooks, server-side rendering (SSR), static site generation (SSG), and more - all with the same developer experience as Next.js but in Python!

## ✨ What's New - Complete Next.js Experience!

NextPy now provides **identical Next.js syntax** in Python with three different syntax styles:

### 🎯 True JSX Syntax (NEW!)
Write exact Next.js JSX syntax in Python:

```python
// pages/index.py - Exact Next.js syntax!
def Home(message):
  return (
    <div className="container">
      <h1>{message}</h1>
      <p>Welcome to NextPy!</p>
      <button onClick="alert('Hello!')">Click Me</button>
    </div>
  );

def getServerSideProps(context):
  return {
    'props': {
      'message': 'Hello from JSX!'
    }
  }

default = Home
```

### 🧩 Component-Style (Python Functions)
Traditional Python function components:

```python
from nextpy.components import Button, Card, Input

def Home(props):
    message = props.get('message', 'Hello!')
    
    return div({'className': 'container'},
        h1({}, message),
        Button(text="Click Me", variant="primary"),
        Input(name="email", placeholder="Enter email")
    )
```

### 📄 Template Style (Traditional)
Jinja2 templates with data fetching:

```python
def get_template():
    return "home.html"

async def get_server_side_props(context):
    return {
        "props": {
            "message": "Hello from templates!"
        }
    }
```

## 🎣 React-Like Hooks (NEW!)

All your favorite React hooks now work in Python:

```python
from nextpy import useState, useEffect, with_hooks

@with_hooks
def Counter(props):
  [count, setCount] = useState(0)
  [name, setName] = useState('NextPy')
  
  useEffect(() => {
    print(f'Count changed to: {count}')
  }, [count])
  
  return (
    <div>
      <h1>Hello {name}!</h1>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
```

### 🎨 Complete Component Library (NEW!)

50+ pre-built components for rapid development:

```python
from nextpy.components import (
    Button, Card, Input, Form, Select,
    Navbar, Tabs, Dropdown, Modal,
    Alert, Badge, Progress, Avatar,
    Container, Grid, Flex, Stack
)

def MyPage():
  return (
    <div>
      <Navbar brand="My App" />
      <Container>
        <Card title="Welcome">
          <Form>
            <Input name="email" placeholder="Enter email" />
            <Button text="Submit" variant="primary" />
          </Form>
        </Card>
      </Container>
    </div>
  );
```

## 🎉 Demo Mode (NEW!)

When users install NextPy and run `nextpy dev` without creating a project, they get beautiful built-in documentation and examples:

```bash
pip install nextpy-framework
nextpy dev  # No project needed!
```

**Demo Mode includes:**
- 🏠 Beautiful homepage with NextPy showcase
- 📚 Complete documentation hub
- 🎨 Component library demonstrations
- 🎣 Hooks examples and tutorials
- 🚀 Project creation interface

## 🚀 Features

### 🎯 Next.js-Style Components
- **True JSX Syntax** - Write `<div>` tags directly in Python
- **Component Functions** - Same structure as Next.js
- **Props & Children** - Pass props and children exactly like Next.js
- **Default Exports** - Use `default = Component` just like Next.js
- **50+ Components** - Pre-built UI components (Button, Card, Form, etc.)
- **React-like Hooks** - useState, useEffect, useReducer, useContext, etc.

### 🧩 Core Next.js Features
- **File-based Routing** - Pages in `pages/` become routes automatically
- **Dynamic Routes** - `[slug].py` creates dynamic URL segments
- **Server-Side Rendering** - `getServerSideProps` fetches data per request
- **Static Site Generation** - `getStaticProps` builds pages at compile time
- **API Routes** - Create API endpoints in `pages/api/` with HTTP method handlers

### 🎣 React-Like Hooks
- **useState** - State management: `[count, setCount] = useState(0)`
- **useEffect** - Side effects and lifecycle
- **useReducer** - Complex state management
- **useContext** - Global state sharing
- **useRef** - Mutable references
- **useMemo** - Memoized values
- **useCallback** - Memoized functions
- **Custom Hooks** - useCounter, useToggle, useLocalStorage, useFetch, useDebounce

### 🎨 Development Experience
- **Hot Reload** - Instant updates on file changes during development
- **Demo Mode** - Built-in documentation when no project exists
- **Dual Rendering** - Choose between JSX, component, or template rendering
- **Type Safety** - Full Python type hints support
- **Error Handling** - Comprehensive error messages and debugging

### 🛠️ Traditional Features (Still Supported)
- **HTMX Integration** - SPA-like navigation without heavy JavaScript
- **Jinja2 Templates** - Powerful templating with layout inheritance
- **Tailwind CSS Integration** - Utility-first CSS framework
- **Database Integration** - SQLAlchemy and database utilities

## 📦 Installation

### Via pip
```bash
pip install nextpy-framework
```

### Development Install (Editable)
```bash
git clone https://github.com/nextpy/nextpy-framework.git
cd nextpy-framework
pip install -e .
```

## 🚀 Quick Start

### 1. Create a new project
```bash
nextpy create my-app
cd my-app
```

### 2. Start development server
```bash
nextpy dev
```

### 3. Open your browser
Navigate to `http://localhost:5000` to see your app!

## 📁 Project Structure

```
my-app/
├── pages/                 # File-based routing
│   ├── index.py          # Homepage (/)
│   ├── about.py          # About page (/about)
│   ├── [slug].py         # Dynamic routes (/:slug)
│   └── api/              # API routes
│       ├── users.py      # API endpoint (/api/users)
│       └── posts.py      # API endpoint (/api/posts)
├── components/           # Reusable components (NEW!)
│   ├── ui/              # Basic UI components
│   │   ├── Button.jsx
│   │   ├── Card.jsx
│   │   └── Modal.jsx
│   ├── forms/            # Form components
│   │   ├── Form.jsx
│   │   └── Input.jsx
│   ├── layout/           # Layout components
│   │   ├── Header.jsx
│   │   ├── Footer.jsx
│   │   └── Sidebar.jsx
│   └── features/        # Feature-specific components
│       ├── DataTable.jsx
│       └── Chart.jsx
├── templates/            # Jinja2 templates (optional)
├── public/              # Static files
├── main.py              # Application entry point
└── requirements.txt     # Python dependencies
```

### 📦 Framework Structure

```
.nextpy_framework/nextpy/
├── __init__.py           # Main exports and imports
├── hooks.py              # React-like hooks implementation
├── hooks_provider.py     # Hooks integration with components
├── jsx.py                # JSX element system
├── jsx_preprocessor.py   # JSX to Python transformer
├── true_jsx.py          # True JSX parser
├── components/           # Component library
│   ├── __init__.py       # Component exports
│   ├── form.py           # Form components
│   ├── layout.py         # Layout components
│   ├── ui.py             # UI components
│   └── navigation.py     # Navigation components
├── core/
│   ├── router.py         # Main routing system
│   ├── component_router.py # Component rendering
│   ├── renderer.py       # Template rendering
│   ├── demo_router.py    # Demo mode routing
│   └── demo_pages_simple.py # Demo pages
└── server/
    └── app.py            # FastAPI application
```

## 🎯 Syntax Examples

### True JSX Syntax (Recommended)
```python
// pages/index.py
def HomePage():
  return (
    <div className="container">
      <header>
        <h1>Welcome to NextPy!</h1>
        <p>Building modern web apps with Python!</p>
      </header>
      
      <main>
        <section>
          <h2>Features</h2>
          <ul>
            <li>File-based routing</li>
            <li>Server-side rendering</li>
            <li>React-like hooks</li>
            <li>50+ components</li>
          </ul>
        </section>
        
        <section>
          <h2>Get Started</h2>
          <button onClick="alert('Hello!')">Click Me</button>
        </section>
      </main>
    </div>
  );

def getServerSideProps(context):
  return {
    'props': {}
  }

default = HomePage
```

### Component-Style with Hooks
```python
// pages/counter.py
from nextpy import useState, useEffect, with_hooks
from nextpy.components import Button, Card

@with_hooks
def CounterPage():
  [count, setCount] = useState(0)
  [message, setMessage] = useState('Click the button!')
  
  useEffect(() => {
    if count > 0:
      setMessage(f'Button clicked {count} times!')
  }, [count])
  
  return (
    <div className="container">
      <Card title="Counter Demo">
        <h2>{message}</h2>
        <p>Count: {count}</p>
        <Button 
          text="Increment" 
          onClick={() => setCount(count + 1)}
          variant="primary"
        />
      </Card>
    </div>
  );
```

### API Routes
```python
// pages/api/users.py
def get(request):
  return {
    'users': [
      {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
      {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'}
    ]
  }

def post(request):
  data = request.get('json', {})
  return {
    'user': data,
    'created': True
  }, 201

default = lambda request: {
    'GET': get,
    'POST': post
  }.get(request.get('method', 'GET'), lambda: {'error': 'Method not allowed'})(request)
```

## 🧩 Reusable JSX Components

### Creating Reusable Components

Create reusable JSX components in the `components/` directory:

```python
// components/ui/Button.jsx
def Button(text, variant="primary", size="medium", onClick=None, className=""):
  base_classes = "px-4 py-2 rounded-md font-medium transition-colors"
  
  variant_classes = {
    "primary": "bg-blue-600 text-white hover:bg-blue-700",
    "secondary": "bg-gray-200 text-gray-900 hover:bg-gray-300",
    "danger": "bg-red-600 text-white hover:bg-red-700"
  }
  
  size_classes = {
    "small": "px-2 py-1 text-sm",
    "medium": "px-4 py-2 text-sm",
    "large": "px-6 py-3 text-base"
  }
  
  classes = f"{base_classes} {variant_classes[variant]} {size_classes[size]} {className}"
  
  return (
    <button className={classes} onClick={onClick}>
      {text}
    </button>
  );
```

```python
// components/ui/Card.jsx
def Card(title, children, className=""):
  return (
    <div className={"bg-white rounded-lg shadow-md p-6 " + className}>
      <h2 className="text-xl font-bold mb-4">{title}</h2>
      {children}
    </div>
  );
```

### Using Reusable Components

```python
// pages/index.py
from components.ui.Button import Button
from components.ui.Card import Card

def HomePage():
  return (
    <div className="container mx-auto p-8">
      <Card title="Welcome">
        <p>This is a reusable card component!</p>
        <Button 
          text="Click Me" 
          variant="primary"
          onClick={() => alert('Button clicked!')}
        />
      </Card>
    </div>
  );
```

### Advanced Reusable Components

```python
// components/layout/Header.jsx
def Header(title, links):
  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <h1 className="text-2xl font-bold">{title}</h1>
          <nav>
            {links.map(link => (
              <a 
                key={link.href}
                href={link.href}
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                {link.label}
              </a>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
```

### Component Organization Best Practices

```
components/
├── ui/              # Basic UI components
│   ├── Button.jsx
│   ├── Card.jsx
│   └── Modal.jsx
├── forms/            # Form components
│   ├── Form.jsx
│   └── Input.jsx
├── layout/           # Layout components
│   ├── Header.jsx
│   ├── Footer.jsx
│   └── Sidebar.jsx
└── features/        # Feature-specific components
    ├── DataTable.jsx
    └── Chart.jsx
```

## 🏠 Default Export Pattern

### What `export = Home` Means

In NextPy (like Next.js), `export = Home` specifies the **default export** of a module. This tells NextPy which component to render for a page.

### Page Component Structure

```python
// pages/index.py

# 1. Define your component function
def Home(props):
  message = props.get('message', 'Hello World!')
  return (
    <div>
      <h1>{message}</h1>
      <p>Welcome to NextPy!</p>
    </div>
  );

# 2. Define data fetching function (optional)
def getServerSideProps(context):
  return {
    'props': {
      'message': 'Hello from Server!'
    }
  }

# 3. Set default export - THIS IS THE PAGE COMPONENT
export = Home
```

### Alternative Syntax

```python
// pages/index.py
def Home(props):
  return <div>Hello World!</div>

def getServerSideProps(context):
  return {'props': {}}

# Alternative way to set default export
default = Home
```

### Why Default Export Matters

1. **Page Identification**: NextPy uses this to identify the main page component
2. **Rendering**: When someone visits `/`, NextPy renders the `Home` component
3. **Data Flow**: Props from `getServerSideProps` are passed to the `Home` component
4. **Consistency**: Matches Next.js pattern exactly

### Complete Example: Reusable Components + Default Export

```python
// pages/index.py
from components.layout.Header import Header
from components.layout.Footer import Footer
from components.ui.Button import Button
from components.ui.Card import Card

def Home(props):
  user = props.get('user', {'name': 'Guest'})
  
  return (
    <div>
      <Header 
        title="NextPy App"
        links={[
          {'label': 'Home', 'href': '/'},
          {'label': 'About', 'href': '/about'},
          {'label': 'Contact', 'href': '/contact'}
        ]}
      />
      
      <main className="container mx-auto p-8">
        <Card title={`Welcome ${user['name']}!`}>
          <p>This is NextPy with reusable JSX components!</p>
          <Button 
            text="Get Started" 
            variant="primary"
            onClick={() => alert('Welcome to NextPy!')}
          />
        </Card>
      </main>
      
      <Footer />
    </div>
  );

def getServerSideProps(context):
  return {
    'props': {
      'user': {'name': 'John Doe'}
    }
  }

export = Home  # This is the page component!
```

### File Structure with Default Exports

```
pages/
├── index.py          # export = Home (renders at /)
├── about.py          # export = About (renders at /about)
├── contact.py         # export = Contact (renders at /contact)
├── [slug].py         # export = Post (renders at /:slug)
└── api/
    ├── users.py      # No default export (API route)
    └── posts.py      # No default export (API route)
```

## 🎣 Hooks Reference

### Core Hooks
```python
# State management
[count, setCount] = useState(0)

# Side effects
useEffect(() => {
  console.log('Component mounted')
  return () => console.log('Cleanup')
}, [])

# Complex state
def counterReducer(state, action):
  if action['type'] == 'increment':
    return {'count': state['count'] + 1}
  return state

[state, dispatch] = useReducer(counterReducer, {'count': 0})

# Context
ThemeContext = createContext('theme', 'light')
theme = useContext(ThemeContext)

# Mutable refs
inputRef = useRef()

# Memoization
expensiveValue = useMemo(() => calculateExpensiveValue(data), [data])

# Memoized callbacks
handleClick = useCallback(() => setCount(count + 1), [])
```

### Custom Hooks
```python
# Counter with increment/decrement
[count, increment, decrement] = useCounter(10)

# Toggle boolean values
[visible, toggle] = useToggle(true)

# LocalStorage persistence
[value, setValue] = useLocalStorage('key', 'default')

# API data fetching
data = useFetch('/api/users')

# Debounced values
debouncedSearch = useDebounce(searchTerm, 500)
```

## 🎨 Components Reference

### Form Components
```python
Input(name="email", type="email", placeholder="Enter email")
TextArea(name="message", placeholder="Your message", rows=4)
Select(name="country", options=[
  {'label': 'USA', 'value': 'us'},
  {'label': 'Canada', 'value': 'ca'}
])
Checkbox(name="newsletter", label="Subscribe to newsletter")
RadioGroup(name="contact", options=[
  {'label': 'Email', 'value': 'email'},
  {'label': 'Phone', 'value': 'phone'}
])
Form(action="/submit", method="POST", children=[...])
SubmitButton(text="Submit Form")
```

### UI Components
```python
Button(text="Click Me", variant="primary", size="large")
Badge(text="New", variant="success")
Avatar(size="medium", fallback="JD")
Alert(message="Success!", variant="success")
Progress(value={75}, variant="primary")
Skeleton(variant="text")
Tooltip(text="Hover info", children=[...])
Chip(text="Removable", removable=True)
```

### Layout Components
```python
Container(max_width="6xl", children=[...])
Grid(columns=3, gap=4, children=[...])
Flex(direction="row", justify="center", children=[...])
Stack(direction="vertical", spacing=4, children=[...])
Card(title="Title", children=[...])
```

### Navigation Components
```python
Navbar(brand="My App", menu_items=[...])
Tabs(tabs=[...], active_tab="tab1")
Dropdown(trigger="Menu", items=[...])
Pagination(current_page=3, total_pages=10)
SearchBar(placeholder="Search...")
BreadcrumbNav(items=[...])
```

## 🔧 Data Fetching

### Server-Side Rendering
```python
// pages/posts/[slug].py
async def getServerSideProps(context):
  slug = context.get('params', {}).get('slug')
  
  # Fetch data from database or API
  post = await fetch_post_by_slug(slug)
  
  if not post:
    return {'notFound': True}
  
  return {
    'props': {
      'post': post
    }
  }

def PostPage(props):
  post = props.get('post')
  return (
    <div>
      <h1>{post['title']}</h1>
      <div>{post['content']}</div>
    </div>
  );
```

### Static Site Generation
```python
// pages/blog/index.py
async def getStaticProps(context):
  posts = await fetch_all_posts()
  
  return {
    'props': {
      'posts': posts
    },
    'revalidate': 3600  # Revalidate every hour
  }

def BlogIndex(props):
  posts = props.get('posts', [])
  return (
    <div>
      <h1>Blog Posts</h1>
      {posts.map(post => (
        <article key={post['id']}>
          <h2>{post['title']}</h2>
          <p>{post['excerpt']}</p>
        </article>
      ))}
    </div>
  );
```

### Static Paths
```python
// pages/blog/[slug].py
async def getStaticPaths(context):
  posts = await fetch_all_posts()
  
  return {
    'paths': [
      {'params': {'slug': post['slug']}}
      for post in posts
    ],
    'fallback': 'blocking'
  }
```

## 🚀 CLI Commands

### Project Creation
```bash
# Create new project
nextpy create my-app

# Create project with specific template
nextpy create my-app --template blog

# Create project in current directory
nextpy create .
```

### Development
```bash
# Start development server
nextpy dev

# Start on specific port
nextpy dev --port 3000

# Start with debug mode
nextpy dev --debug
```

### Build & Deploy
```bash
# Build for production
nextpy build

# Build static site
nextpy build --static

# Export to static files
nextpy export
```

### Database
```bash
# Initialize database
nextpy db init

# Run migrations
nextpy db migrate

# Create migration
nextpy db migration create add_users_table
```

## 🎯 Demo Mode

When you install NextPy and run `nextpy dev` without creating a project:

```bash
pip install nextpy-framework
nextpy dev
```

You'll see:
- 🎉 **Demo Mode Activated** message
- 🏠 **Beautiful homepage** showcasing NextPy features
- 📚 **Complete documentation** with examples
- 🎨 **Component demonstrations** with live code
- 🎣 **Hooks tutorials** and API reference
- 🚀 **Project creation interface**

## 📚 Documentation

### Getting Started
- [Quick Start Guide](QUICKSTART.md) - 5-minute setup
- [Step-by-Step Todo App](TODO_APP_TUTORIAL.md) - Complete tutorial
- [Components Guide](COMPONENTS_GUIDE.md) - Component library
- [Hooks Guide](HOOKS_GUIDE_COMPLETE.md) - React-like hooks
- [True JSX Guide](TRUE_JSX_GUIDE.md) - JSX syntax

### Advanced Topics
- [Performance Guide](PERFORMANCE.md) - Optimization tips
- [Testing Guide](TESTING.md) - Testing strategies
- [Database Integration](DB_INTEGRATION.md) - Database setup
- [Authentication](AUTHENTICATION.md) - User authentication
- [Deployment Guide](DEPLOYMENT.md) - Production deployment

### API Reference
- [Component API](COMPONENTS_GUIDE.md#component-reference)
- [Hooks API](HOOKS_GUIDE_COMPLETE.md#hook-reference)
- [CLI Commands](QUICK_REFERENCE.md#cli-commands)
- [Configuration](CONFIGURATION.md) - All options

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest test_components.py

# Run with coverage
pytest --cov=nextpy_framework
```

### Test Examples
```python
# test_components.py
from nextpy.components import Button, Card

def test_button_component():
    button = Button(text="Click Me", variant="primary")
    assert button is not None

def test_card_component():
    card = Card(title="Test", children=["Content"])
    assert card is not None
```

## 🚀 Deployment

### Production Build
```bash
# Build for production
nextpy build

# Start production server
nextpy start
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN nextpy build

EXPOSE 5000
CMD ["nextpy", "start"]
```

### Vercel
```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ]
}
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone repository
git clone https://github.com/nextpy/nextpy-framework.git
cd nextpy-framework

# Install in development mode
pip install -e .

# Run tests
pytest

# Run development server
python main.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Next.js Team** - For the amazing framework that inspired NextPy
- **React Team** - For the hooks and component patterns
- **FastAPI** - For the excellent ASGI framework
- **Python Community** - For the amazing ecosystem

## 🎉 What's Next?

- 🚀 **More Components** - Expanding the component library
- 🎨 **Theme System** - Built-in theming support
- 📱 **Mobile App** - React Native integration
- 🔌 **Plugin System** - Extensible plugin architecture
- 🌐 **Internationalization** - Multi-language support

---

**NextPy: Next.js for Python 🐍 → React ❤️ Python**

*Build modern web applications with the exact Next.js experience, but in Python!* 🚀
