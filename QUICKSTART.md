# NextPy Quick Start (5 Minutes)

Get a NextPy app running in 5 minutes.

## 1. Install (30 seconds)

```bash
pip install nextpy-framework
```

## 2. Create Project (1 minute)

```bash
nextpy create my-blog
cd my-blog
```

## 3. Start Server (1 minute)

```bash
nextpy dev
```

Visit `http://localhost:5000` - your app is live!

## 4. Create Your First Page (2 minutes)

**Create the page:**
```python
# pages/hello.py

def get_template():
    return "hello.html"

async def get_server_side_props(context):
    return {
        "props": {
            "name": "World",
            "message": "Welcome to NextPy!"
        }
    }
```

**Create the template:**
```html
<!-- templates/hello.html -->
{% extends "_base.html" %}

{% block content %}
<div class="max-w-4xl mx-auto py-12 px-4">
    <h1 class="text-4xl font-bold">Hello {{ name }}!</h1>
    <p class="text-lg text-gray-600">{{ message }}</p>
</div>
{% endblock %}
```

**Visit:** `http://localhost:5000/hello` ✨

---

## Next Steps

### Explore Components
```html
{% from "components/button.html" import button %}
{% from "components/card.html" import card %}

{{ button("Click Me", "/action", "primary") }}
{{ card(title="My Card", content="Description") }}
```

### Create API Endpoints
```python
# pages/api/hello.py

async def get(request):
    return {"message": "Hello from API!"}

async def post(request):
    data = await request.json()
    return {"received": data}
```

Visit: `http://localhost:5000/api/hello`

### Build for Production
```bash
nextpy build    # Generate static files
nextpy start    # Start production server
```

---

## Learn More

- **Full Guide**: See `DOCUMENTATION.md`
- **Examples**: Visit `/examples` in dev server
- **GitHub**: https://github.com/nextpy/nextpy-framework

---

## Troubleshooting

**Port 5000 already in use?**
```bash
nextpy dev --port 3000
```

**Hot reload not working?**
```bash
pip install --upgrade watchdog
```

**Template not found?**
Check the filename in `templates/` matches `get_template()` return value.

---

Happy coding! 🚀
