"""
PSX Package - Clean Python Syntax eXtension for NextPy
Production-ready PSX with clean architecture and enhanced full-stack support
"""

# Core imports
from .core.parser import PSXElement, PSXParser, psx, render_psx, fragment, key
from .core.runtime import process_python_logic, runtime
from .core.evaluator import SafeExpressionEngine
from .vdom.vnode import VNode, create_element, render, update, get_vdom_metrics
from .renderer.renderer import PSXRenderer, renderer
from .components.component import (
    PSXComponent, component, class_component, ChildrenComponent,
    register_component, clsx, Component, Props, Children,
    Head, Link, Script, Image, Meta, Title, Layout, Container,
    Row, Col, Form, Input, Button, Navbar, NavItem, Card, List,
    Conditional, Loop, ErrorBoundary, Suspense,
    # React Hooks
    useState, useEffect, useContext, useReducer, useRef, useMemo, useCallback,
    useImperativeHandle, useLayoutEffect, useDebugValue, useTransition,
    useDeferredValue, useId,
    # Custom Hooks
    useCounter, useToggle, useLocalStorage, useFetch, useDebounce,
    useInterval, usePrevious, useAsync, useMediaQuery, useGeolocation, usePerformance,
    # Event Handlers
    create_onclick, create_ondblclick, create_onmousedown, create_onmouseup,
    create_onmouseover, create_onmouseout, create_onmouseenter, create_onmouseleave, create_onmousemove,
    create_onchange, create_onsubmit, create_onreset, create_onfocus, create_onblur,
    create_oninput, create_oninvalid, create_onselect,
    create_onkeydown, create_onkeyup, create_onkeypress,
    create_ontouchstart, create_ontouchend, create_ontouchmove, create_ontouchcancel,
    create_onload, create_onunload, create_onresize, create_onscroll,
    create_ondrag, create_ondragstart, create_ondragend, create_ondragenter,
    create_ondragleave, create_ondragover, create_ondrop,
    create_onplay, create_onpause, create_onended, create_onvolumechange,
    create_ontimeupdate, create_onseeking, create_onseeked,
    create_onloadstart, create_onprogress, create_onerror, create_onabort,
    create_onanimationstart, create_onanimationend, create_onanimationiteration,
    create_ontransitionend, create_ontransitionrun, create_ontransitionstart,
    create_onwheel, create_oncopy, create_oncut, create_onpaste,
    create_onbeforeprint, create_onafterprint, create_onstorage,
    create_onopen, create_onmessage, create_onclose, create_oninstall, create_onactivate
)
from .utils.helpers import compile_psx, compile_psx_file, is_psx_file, PSXCompiler

# Load enhanced client runtime
import os
enhanced_runtime_path = os.path.join(os.path.dirname(__file__), 'runtime', 'enhanced_client_runtime.js')
try:
    with open(enhanced_runtime_path, 'r') as f:
        ENHANCED_CLIENT_RUNTIME_SCRIPT = f.read()
except FileNotFoundError:
    ENHANCED_CLIENT_RUNTIME_SCRIPT = ""

CLIENT_ROUTER_SCRIPT = r"""
(function () {
    if (window.__nextpyRouterInstalled) return;
    window.__nextpyRouterInstalled = true;
    var cache = new Map();
    var navigating = false;

    function isInternal(url) {
        return url.origin === window.location.origin &&
            (url.protocol === 'http:' || url.protocol === 'https:');
    }

    async function load(url, replace, scroll) {
        if (navigating) return;
        navigating = true;
        try {
            var documentText = cache.get(url.href);
            if (!documentText) {
                var response = await fetch(url.href, {
                    headers: {'X-NextPy-Navigation': 'true', 'Accept': 'text/html'}
                });
                if (!response.ok) throw new Error('Navigation failed: ' + response.status);
                documentText = await response.text();
                cache.set(url.href, documentText);
            }
            var parsed = new DOMParser().parseFromString(documentText, 'text/html');
            if (!parsed.body) throw new Error('Navigation returned invalid HTML');
            document.body.replaceWith(parsed.body);
            document.title = parsed.title || document.title;
            if (replace) history.replaceState({}, '', url.href);
            else history.pushState({}, '', url.href);
            if (scroll !== false) window.scrollTo(0, 0);
            document.dispatchEvent(new CustomEvent('nextpy:navigate', {detail: {url: url.href}}));
        } catch (error) {
            console.error('[NextPy] client navigation failed; using browser navigation', error);
            window.location.href = url.href;
        } finally {
            navigating = false;
        }
    }

    document.addEventListener('click', function (event) {
        var link = event.target.closest('[data-nextpy-link]');
        if (!link || event.defaultPrevented || event.button !== 0 ||
            event.metaKey || event.ctrlKey || event.shiftKey || event.altKey ||
            link.target === '_blank') return;
        var url = new URL(link.href, window.location.href);
        if (!isInternal(url)) return;
        event.preventDefault();
        load(url, link.dataset.nextpyReplace === 'true', link.dataset.nextpyScroll !== 'false');
    });

    document.addEventListener('mouseenter', function(event) {
        // FIX: Safely check if event.target exists and supports closest()
        if (!event.target || typeof event.target.closest !== 'function')
            return;

        var link = event.target.closest('[data-nextpy-prefetch]');
        if (!link)
            return;
        var url = new URL(link.href, window.location.href);
        if (isInternal(url) && !cache.has(url.href)) {
            fetch(url.href, {
                headers: {
                    'X-NextPy-Navigation': 'true',
                    'Accept': 'text/html'
                }
            }).then(function(response) {
                return response.ok ? response.text() : null;
            }).then(function(text) {
                if (text)
                    cache.set(url.href, text);
            }).catch(function() {});
        }
    }, true);


    window.addEventListener('popstate', function () {
        load(new URL(window.location.href), true, false);
    });
})();
"""

CRUD_RUNTIME_SCRIPT = r"""
(function () {
    if (window.__nextpyCrudRuntime) return;
    window.__nextpyCrudRuntime = true;

    function roots() { return document.querySelectorAll('[data-nextpy-crud]'); }
    function error(root, message) {
        var target = root.querySelector('[data-nextpy-error]');
        if (target) { target.textContent = message || ''; target.classList.toggle('hidden', !message); }
    }
    function status(root, message) {
        var target = root.querySelector('[data-nextpy-status]');
        if (target) target.textContent = message;
    }
    async function callServerAction(actionName, data) {
        var token = window.localStorage.getItem('nextpy_access_token') ||
            window.sessionStorage.getItem('nextpy_access_token');
        var headers = {'Content-Type': 'application/json', 'Accept': 'application/json'};
        if (token) headers.Authorization = 'Bearer ' + token;
        var response = await fetch('/_server_actions/' + actionName, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(data || {})
        });
        var result = await response.json();
        if (!response.ok || result.error) throw new Error(result.error || 'Server action failed');
        return result;
    }
    function applyChange(root, message, config) {
        var item = message.data;
        if (message.action === 'deleted') {
            var deleted = root.querySelector('[data-nextpy-item="' + item.id + '"]');
            if (deleted) deleted.remove();
            return;
        }
        var element = root.querySelector('[data-nextpy-item="' + item.id + '"]');
        if (!element && message.action === 'created') {
            var list = root.querySelector('[data-nextpy-list]');
            if (!list) return;
            window.location.reload();
            return;
        }
        if (!element) return;
        if (config.fieldMapping) {
            for (var field in config.fieldMapping) {
                var selector = config.fieldMapping[field];
                var target = element.querySelector(selector);
                if (target && item[field] !== undefined) {
                    target.textContent = item[field];
                }
            }
        }
    }
    roots().forEach(function (root) {
        var config = JSON.parse(root.dataset.nextpyCrud || '{}');
        var createAction = config.createAction || 'create';
        var updateAction = config.updateAction || 'update';
        var deleteAction = config.deleteAction || 'delete';
        var wsChannel = config.wsChannel || config.resource || 'items';
        var messageType = config.messageType || (config.resource || 'ITEM') + '_CHANGED';
        
        var form = root.querySelector('[data-nextpy-action="create"]');
        if (form) form.addEventListener('submit', async function (event) {
            event.preventDefault(); error(root, '');
            var body = {};
            form.querySelectorAll('[data-nextpy-field]').forEach(function (field) {
                body[field.dataset.nextpyField] = field.value;
            });
            try { 
                await callServerAction(createAction, body); 
                form.reset();
            }
            catch (err) { error(root, err.message); }
        });
        root.addEventListener('change', async function (event) {
            // FIX: Safely check if event.target exists and supports closest()
            if (!event.target || typeof event.target.closest !== 'function') 
                return;

            var toggle = event.target.closest('[data-nextpy-toggle]');
            if (!toggle) return;
            var itemId = toggle.dataset.nextpyToggle;
            var updateBody = config.updateBody ? config.updateBody(itemId, toggle.checked) : {id: Number(itemId), completed: toggle.checked};
            try { await callServerAction(updateAction, updateBody); }
            catch (err) { error(root, err.message); toggle.checked = !toggle.checked; }
        });
        root.addEventListener('click', async function (event) {
            // FIX: Safely check if event.target exists and supports closest()
            if (!event.target || typeof event.target.closest !== 'function') 
                return;

            var button = event.target.closest('[data-nextpy-delete]');
            if (!button) return;
            var itemId = button.dataset.nextpyDelete;
            var confirmMsg = config.deleteConfirm || 'Delete this item?';
            if (!window.confirm(confirmMsg)) return;
            var deleteBody = config.deleteBody ? config.deleteBody(itemId) : {id: Number(itemId)};
            try { await callServerAction(deleteAction, deleteBody); }
            catch (err) { error(root, err.message); }
        });
        var protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        var socket;
        var reconnectTimer;
        function connect() {
            socket = new WebSocket(protocol + '//' + window.location.host + '/ws');
            socket.addEventListener('open', function () {
                status(root, 'Live'); 
                socket.send(JSON.stringify({type: 'subscribe', channel: wsChannel}));
            });
            socket.addEventListener('close', function () {
                status(root, 'Offline');
                clearTimeout(reconnectTimer);
                reconnectTimer = setTimeout(connect, 2000);
            });
            socket.addEventListener('error', function () { status(root, 'Offline'); });
            socket.addEventListener('message', function (event) {
                var message = JSON.parse(event.data);
                if (message.type === messageType) applyChange(root, message, config);
            });
        }
        connect();
    });
})();
"""


# Hydration Engine imports
from .hydration import (
    HydrationEngine, get_hydration_engine,
    interactive_component, enable_hydration_globally, create_interactive_page,
    hydrate_component, get_component_hydrator,
)

# Convenience functions
def render_psx_component(element, context=None):
    """Render PSX component using the clean renderer with enhanced full-stack support"""
    html = renderer.render(element, context)
    
    # Inject JavaScript runtime scripts for interactive components and full HTML documents
    try:
        from .runtime.js_actions_runtime import JS_ACTION_RUNTIME_SCRIPT
        
        # Always inject enhanced runtime for full-stack applications
        if ENHANCED_CLIENT_RUNTIME_SCRIPT:
            html = f"<script>{ENHANCED_CLIENT_RUNTIME_SCRIPT}</script>{html}"
        
        # Inject legacy runtime for backwards compatibility
        if 'data-handler-' in html or 'data-bind' in html or '<html' in html:
            html = f"<script>{JS_ACTION_RUNTIME_SCRIPT}</script>{html}"
            
    except ImportError:
        # Fallback to enhanced runtime only
        if ENHANCED_CLIENT_RUNTIME_SCRIPT:
            html = f"<script>{ENHANCED_CLIENT_RUNTIME_SCRIPT}</script>{html}"
    
    return html

# Auto-export all PSX features
__all__ = [
    # Core
    'PSXElement', 'PSXParser', 'psx', 'render_psx', 'fragment', 'key',
    'process_python_logic', 'runtime', 'SafeExpressionEngine',
    'CLIENT_ROUTER_SCRIPT',
    'CRUD_RUNTIME_SCRIPT',
    
    # VDOM
    'VNode', 'create_element', 'render', 'update', 'get_vdom_metrics',
    
    # Renderer
    'PSXRenderer', 'renderer', 'render_psx_component',
    
    # Components
    'PSXComponent', 'component', 'Component', 'class_component', 'Props', 'Children',
    'Head', 'Link', 'Script', 'Image', 'Meta', 'Title', 'Layout', 'Container',
    'Row', 'Col', 'Form', 'Input', 'Button', 'Navbar', 'NavItem', 'Card', 'List',
    'Conditional', 'Loop', 'ErrorBoundary', 'Suspense', 'ChildrenComponent',
    'register_component', 'clsx',
    
    # React Hooks
    'useState', 'useEffect', 'useContext', 'useReducer', 'useRef',
    'useMemo', 'useCallback', 'useImperativeHandle', 'useLayoutEffect',
    'useDebugValue', 'useTransition', 'useDeferredValue', 'useId',
    
    # Custom Hooks
    'useCounter', 'useToggle', 'useLocalStorage', 'useFetch', 'useDebounce',
    'useInterval', 'usePrevious', 'useAsync', 'useMediaQuery', 'useGeolocation', 'usePerformance',
    
    # Event Handlers
    'create_onclick', 'create_ondblclick', 'create_onmousedown', 'create_onmouseup',
    'create_onmouseover', 'create_onmouseout', 'create_onmouseenter', 'create_onmouseleave', 'create_onmousemove',
    'create_onchange', 'create_onsubmit', 'create_onreset', 'create_onfocus', 'create_onblur',
    'create_oninput', 'create_oninvalid', 'create_onselect',
    'create_onkeydown', 'create_onkeyup', 'create_onkeypress',
    'create_ontouchstart', 'create_ontouchend', 'create_ontouchmove', 'create_ontouchcancel',
    'create_onload', 'create_onunload', 'create_onresize', 'create_onscroll',
    'create_ondrag', 'create_ondragstart', 'create_ondragend', 'create_ondragenter',
    'create_ondragleave', 'create_ondragover', 'create_ondrop',
    'create_onplay', 'create_onpause', 'create_onended', 'create_onvolumechange',
    'create_ontimeupdate', 'create_onseeking', 'create_onseeked',
    'create_onloadstart', 'create_onprogress', 'create_onerror', 'create_onabort',
    'create_onanimationstart', 'create_onanimationend', 'create_onanimationiteration',
    'create_ontransitionend', 'create_ontransitionrun', 'create_ontransitionstart',
    'create_onwheel', 'create_oncopy', 'create_oncut', 'create_onpaste',
    'create_onbeforeprint', 'create_onafterprint', 'create_onstorage',
    'create_onopen', 'create_onmessage', 'create_onclose', 'create_oninstall', 'create_onactivate',
    
    # Utils
    'compile_psx', 'compile_psx_file', 'is_psx_file', 'PSXCompiler',
    
    # Hydration Engine
    'HydrationEngine', 'get_hydration_engine',
    'interactive_component', 'enable_hydration_globally', 'create_interactive_page',
    'hydrate_component', 'get_component_hydrator',
    
    # Enhanced Full-Stack Runtime
    'ENHANCED_CLIENT_RUNTIME_SCRIPT',
]
