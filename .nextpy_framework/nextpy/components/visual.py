"""
Visual Components for NextPy
Tabs, Accordion, Dropdown, Modal, Card variations
"""


def Tabs(tabs: list, active_index: int = 0) -> str:
    """
    Tabs component
    tabs: [{"label": "Tab 1", "content": "<p>Content 1</p>"}, ...]
    """
    tab_buttons = "\n".join([
        f'<button class="px-4 py-2 border-b-2 {"border-blue-600 text-blue-600 font-bold" if i == active_index else "border-gray-300 text-gray-600"}" onclick="switchTab({i})">
            {tab["label"]}
        </button>'
        for i, tab in enumerate(tabs)
    ])
    
    tab_contents = "\n".join([
        f'<div id="tab-content-{i}" class="{"block" if i == active_index else "hidden"} py-4">
            {tab["content"]}
        </div>'
        for i, tab in enumerate(tabs)
    ])
    
    return f'''
    <div class="space-y-4">
        <div class="flex border-b border-gray-200">
            {tab_buttons}
        </div>
        <div>
            {tab_contents}
        </div>
    </div>
    <script>
        function switchTab(index) {{
            document.querySelectorAll('[id^="tab-content-"]').forEach(el => el.classList.add('hidden'));
            document.getElementById('tab-content-' + index).classList.remove('hidden');
            document.querySelectorAll('button').forEach((btn, i) => {{
                btn.classList.toggle('border-blue-600', i === index);
                btn.classList.toggle('text-blue-600', i === index);
                btn.classList.toggle('font-bold', i === index);
                btn.classList.toggle('border-gray-300', i !== index);
                btn.classList.toggle('text-gray-600', i !== index);
            }});
        }}
    </script>
    '''


def Accordion(items: list) -> str:
    """
    Accordion component
    items: [{"title": "Section 1", "content": "<p>Content 1</p>"}, ...]
    """
    accordion_html = "\n".join([
        f'''
        <div class="border border-gray-300 mb-2 rounded-lg overflow-hidden">
            <button onclick="toggleAccordion({i})" class="w-full text-left px-4 py-3 bg-gray-100 hover:bg-gray-200 font-semibold flex justify-between items-center">
                {item["title"]}
                <span id="accordion-icon-{i}">▼</span>
            </button>
            <div id="accordion-content-{i}" class="hidden px-4 py-3 bg-white text-gray-700">
                {item["content"]}
            </div>
        </div>
        '''
        for i, item in enumerate(items)
    ])
    
    return f'''
    <div class="space-y-2">
        {accordion_html}
    </div>
    <script>
        function toggleAccordion(index) {{
            const content = document.getElementById('accordion-content-' + index);
            const icon = document.getElementById('accordion-icon-' + index);
            content.classList.toggle('hidden');
            icon.textContent = content.classList.contains('hidden') ? '▼' : '▲';
        }}
    </script>
    '''


def Dropdown(label: str, items: list, position: str = "left") -> str:
    """
    Dropdown component
    items: [{"label": "Option 1", "href": "/path"}, ...]
    """
    position_class = "right-0" if position == "right" else "left-0"
    items_html = "\n".join([
        f'<a href="{item.get("href", "#")}" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">{item["label"]}</a>'
        for item in items
    ])
    
    return f'''
    <div class="relative inline-block">
        <button onclick="toggleDropdown()" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            {label}
        </button>
        <div id="dropdown-menu" class="hidden absolute {position_class} mt-2 bg-white border border-gray-300 rounded-lg shadow-lg z-10">
            {items_html}
        </div>
    </div>
    <script>
        function toggleDropdown() {{
            const menu = document.getElementById('dropdown-menu');
            menu.classList.toggle('hidden');
        }}
        document.addEventListener('click', function(event) {{
            const menu = document.getElementById('dropdown-menu');
            if (!menu.parentElement.contains(event.target)) menu.classList.add('hidden');
        }});
    </script>
    '''


def Modal(title: str, content: str, footer: str = "", show: bool = False) -> str:
    """Modal component"""
    display = "flex" if show else "hidden"
    return f'''
    <div id="modal-overlay" class="{display} fixed inset-0 bg-black bg-opacity-50 justify-center items-center z-50">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h2 class="text-xl font-bold">{title}</h2>
                <button onclick="closeModal()" class="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
            </div>
            <div class="px-6 py-4">
                {content}
            </div>
            {f'<div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-2">{footer}</div>' if footer else ''}
        </div>
    </div>
    <script>
        function openModal() {{
            document.getElementById('modal-overlay').classList.remove('hidden');
            document.getElementById('modal-overlay').classList.add('flex');
        }}
        function closeModal() {{
            document.getElementById('modal-overlay').classList.add('hidden');
            document.getElementById('modal-overlay').classList.remove('flex');
        }}
    </script>
    '''


def Card(title: str, content: str, image: str = "", footer: str = "") -> str:
    """Enhanced Card component"""
    image_html = f'<img src="{image}" class="w-full h-48 object-cover rounded-t-lg"/>' if image else ""
    footer_html = f'<div class="px-6 py-3 bg-gray-50 border-t border-gray-200 text-sm text-gray-600">{footer}</div>' if footer else ""
    
    return f'''
    <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition">
        {image_html}
        <div class="px-6 py-4">
            <h3 class="font-bold text-lg mb-2">{title}</h3>
            <p class="text-gray-600">{content}</p>
        </div>
        {footer_html}
    </div>
    '''


def Breadcrumb(items: list) -> str:
    """Breadcrumb navigation"""
    breadcrumb_html = " / ".join([
        f'<a href="{item.get("href", "#")}" class="text-blue-600 hover:underline">{item["label"]}</a>'
        if item.get("href") else f'<span class="text-gray-700">{item["label"]}</span>'
        for item in items
    ])
    return f'<nav class="text-sm text-gray-600 mb-4">{breadcrumb_html}</nav>'


def Pagination(current: int = 1, total: int = 10, base_url: str = "") -> str:
    """Pagination component"""
    pages = []
    for i in range(1, total + 1):
        if i == current:
            pages.append(f'<span class="px-3 py-1 bg-blue-600 text-white rounded">{i}</span>')
        else:
            pages.append(f'<a href="{base_url}?page={i}" class="px-3 py-1 border border-gray-300 rounded hover:bg-gray-100">{i}</a>')
    
    return f'<div class="flex gap-2">{" ".join(pages)}</div>'
