"""
Form components for NextPy
Input, TextArea, Select, Checkbox, Radio, Form, etc.
"""

from typing import Optional, List, Dict, Any


def Input(
    name: str = "",
    type: str = "text",
    placeholder: str = "",
    value: str = "",
    required: bool = False,
    disabled: bool = False,
    class_name: str = "",
    **kwargs
) -> str:
    """Input component"""
    req = "required" if required else ""
    dis = "disabled" if disabled else ""
    default_class = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
    
    return f'''<input 
        type="{type}"
        name="{name}"
        placeholder="{placeholder}"
        value="{value}"
        class="{class_name or default_class}"
        {req}
        {dis}
    >'''


def TextArea(
    name: str = "",
    placeholder: str = "",
    value: str = "",
    rows: int = 4,
    required: bool = False,
    disabled: bool = False,
    class_name: str = "",
    **kwargs
) -> str:
    """TextArea component"""
    req = "required" if required else ""
    dis = "disabled" if disabled else ""
    default_class = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
    
    return f'''<textarea 
        name="{name}"
        placeholder="{placeholder}"
        rows="{rows}"
        class="{class_name or default_class}"
        {req}
        {dis}
    >{value}</textarea>'''


def Select(
    name: str = "",
    options: Optional[List[Dict[str, str]]] = None,
    value: str = "",
    required: bool = False,
    disabled: bool = False,
    class_name: str = "",
    **kwargs
) -> str:
    """Select dropdown component"""
    if options is None:
        options = []
    
    req = "required" if required else ""
    dis = "disabled" if disabled else ""
    default_class = "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
    
    option_html = ""
    for opt in options:
        selected = "selected" if opt.get("value") == value else ""
        option_html += f'<option value="{opt.get("value")}" {selected}>{opt.get("label")}</option>'
    
    return f'''<select 
        name="{name}"
        class="{class_name or default_class}"
        {req}
        {dis}
    >{option_html}</select>'''


def Checkbox(
    name: str = "",
    label: str = "",
    checked: bool = False,
    required: bool = False,
    disabled: bool = False,
    **kwargs
) -> str:
    """Checkbox component"""
    check = "checked" if checked else ""
    dis = "disabled" if disabled else ""
    req = "required" if required else ""
    
    return f'''<label class="flex items-center gap-2">
        <input 
            type="checkbox"
            name="{name}"
            class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            {check}
            {req}
            {dis}
        >
        <span>{label}</span>
    </label>'''


def Radio(
    name: str = "",
    label: str = "",
    value: str = "",
    checked: bool = False,
    required: bool = False,
    disabled: bool = False,
    **kwargs
) -> str:
    """Radio button component"""
    check = "checked" if checked else ""
    dis = "disabled" if disabled else ""
    req = "required" if required else ""
    
    return f'''<label class="flex items-center gap-2">
        <input 
            type="radio"
            name="{name}"
            value="{value}"
            class="w-4 h-4 text-blue-600 border-gray-300 focus:ring-2 focus:ring-blue-500"
            {check}
            {req}
            {dis}
        >
        <span>{label}</span>
    </label>'''


def RadioGroup(
    name: str = "",
    options: Optional[List[Dict[str, str]]] = None,
    value: str = "",
    **kwargs
) -> str:
    """Radio group component"""
    if options is None:
        options = []
    
    html = f'<fieldset class="space-y-3">'
    
    for opt in options:
        checked = opt.get("value") == value
        label = opt.get("label", "")
        opt_value = opt.get("value", "")
        html += Radio(
            name=name,
            label=label,
            value=opt_value,
            checked=checked
        )
    
    html += '</fieldset>'
    return html


def Form(
    children: str = "",
    action: str = "",
    method: str = "POST",
    onsubmit: str = "",
    class_name: str = "",
    **kwargs
) -> str:
    """Form component"""
    submit_handler = f'onsubmit="{onsubmit}"' if onsubmit else ""
    default_class = "space-y-6"
    
    return f'''<form 
        action="{action}"
        method="{method}"
        class="{class_name or default_class}"
        {submit_handler}
    >{children}</form>'''


def FormGroup(
    label: str = "",
    children: str = "",
    error: str = "",
    **kwargs
) -> str:
    """Form group component (label + input)"""
    error_html = f'<p class="text-red-600 text-sm mt-1">{error}</p>' if error else ""
    
    return f'''<div class="space-y-2">
        {f'<label class="block text-sm font-semibold text-gray-900">{label}</label>' if label else ''}
        {children}
        {error_html}
    </div>'''


def FileInput(
    name: str = "",
    accept: str = "",
    multiple: bool = False,
    required: bool = False,
    disabled: bool = False,
    **kwargs
) -> str:
    """File input component"""
    req = "required" if required else ""
    dis = "disabled" if disabled else ""
    mult = "multiple" if multiple else ""
    
    return f'''<input 
        type="file"
        name="{name}"
        accept="{accept}"
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        {mult}
        {req}
        {dis}
    >'''


def PasswordInput(
    name: str = "",
    placeholder: str = "",
    value: str = "",
    required: bool = False,
    **kwargs
) -> str:
    """Password input component"""
    return Input(
        name=name,
        type="password",
        placeholder=placeholder,
        value=value,
        required=required
    )


def EmailInput(
    name: str = "",
    placeholder: str = "Enter email",
    value: str = "",
    required: bool = True,
    **kwargs
) -> str:
    """Email input component"""
    return Input(
        name=name,
        type="email",
        placeholder=placeholder,
        value=value,
        required=required
    )


def NumberInput(
    name: str = "",
    placeholder: str = "",
    value: str = "",
    min: str = "",
    max: str = "",
    step: str = "1",
    required: bool = False,
    **kwargs
) -> str:
    """Number input component"""
    return Input(
        name=name,
        type="number",
        placeholder=placeholder,
        value=value,
        required=required
    )


__all__ = [
    'Input',
    'TextArea',
    'Select',
    'Checkbox',
    'Radio',
    'RadioGroup',
    'Form',
    'FormGroup',
    'FileInput',
    'PasswordInput',
    'EmailInput',
    'NumberInput',
]
