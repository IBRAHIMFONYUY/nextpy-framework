"""
NextPy Development Tools - Generators and scaffolding
"""

from pathlib import Path
from typing import Optional, List, Tuple


class PageGenerator:
    """Generate page files from templates"""
    
    @staticmethod
    def create_page(name: str, pages_dir: Path = Path("pages")) -> Tuple[Path, Path]:
        """Generate a new page file"""
        name_clean = name.replace("-", "_").lower()
        page_file = pages_dir / f"{name_clean}.py"
        
        content = f'''"""
{name} page
"""

def get_template():
    return "{name_clean}.html"


async def get_server_side_props(context):
    return {{
        "props": {{
            "title": "{name}",
            "description": "Page description"
        }}
    }}
'''
        
        page_file.write_text(content)
        
        # Create template
        template_file = Path("templates") / f"{name_clean}.html"
        template_content = f'''{% extends "_base.html" %}

{% block content %}
<div class="max-w-6xl mx-auto py-12 px-4">
    <h1 class="text-4xl font-bold mb-4">{{{{ title }}}}</h1>
    <p class="text-gray-600 mb-8">{{{{ description }}}}</p>
    
    <!-- Your content here -->
</div>
{% endblock %}
'''
        template_file.write_text(template_content)
        
        return page_file, template_file


class APIGenerator:
    """Generate API route files"""
    
    @staticmethod
    def create_api(name: str, methods: Optional[List[str]] = None, api_dir: Path = Path("pages/api")) -> Path:
        """Generate API endpoint"""
        if methods is None:
            methods = ["GET"]
        
        name_clean = name.replace("-", "_").lower()
        api_file = api_dir / f"{name_clean}.py"
        
        method_stubs: List[str] = []
        for method in methods:
            method_lower = method.lower()
            if method == "GET":
                method_stubs.append(f'''async def {method_lower}(request):
    """GET /{name_clean}"""
    return {{"data": "hello"}}
''')
            elif method == "POST":
                method_stubs.append(f'''async def {method_lower}(request):
    """POST /{name_clean}"""
    data = await request.json()
    return {{"created": data}}
''')
            elif method in ["PUT", "DELETE"]:
                method_stubs.append(f'''async def {method_lower}(request):
    """{method} /{name_clean}"""
    return {{"{method_lower.lower()}_id": 1}}
''')
        
        content = f'''"""
{name} API endpoint
"""

{chr(10).join(method_stubs)}
'''
        
        api_file.write_text(content)
        return api_file


class ComponentGenerator:
    """Generate component files"""
    
    @staticmethod
    def create_component(name: str, templates_dir: Path = Path("templates/components")) -> Path:
        """Generate a new component"""
        name_clean = name.replace("-", "_").lower()
        component_file = templates_dir / f"{name_clean}.html"
        
        content = f'''{{%- macro {name_clean}(label, items=[], **kwargs) -}}
<!-- {name} component -->
<div class="component-{name_clean}">
    <h3>{{{{ label }}}}</h3>
    {{% for item in items %}}
    <div class="item">{{{{ item }}}}</div>
    {{% endfor %}}
</div>
{{%- endmacro %}}
'''
        
        component_file.write_text(content)
        return component_file


class ModelGenerator:
    """Generate database models"""
    
    @staticmethod
    def create_model(name: str, fields: Optional[dict] = None, models_dir: Path = Path("models")) -> Path:
        """Generate database model"""
        if fields is None:
            fields = {"id": "Integer, primary_key=True", "name": "String(255)"}
        
        models_dir.mkdir(exist_ok=True)
        model_file = models_dir / f"{name.lower()}.py"
        
        field_stubs: List[str] = []
        for field_name, field_type in fields.items():
            field_stubs.append(f"    {field_name} = Column({field_type})")
        
        content = f'''"""
{name} model
"""

from nextpy.db import Base
from sqlalchemy import Column, String, Integer, DateTime, Text
from datetime import datetime


class {name}(Base):
    """{{docstring}}"""
    __tablename__ = "{name.lower()}s"
    
{chr(10).join(field_stubs)}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
'''
        
        model_file.write_text(content)
        return model_file
