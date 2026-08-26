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

    // Helper to dynamically inject custom modal CSS if it doesn't exist
    if (!document.getElementById('nextpy-modal-styles')) {
        var style = document.createElement('style');
        style.id = 'nextpy-modal-styles';
        style.textContent = '.nextpy-modal-open { overflow: hidden; }';
        document.head.appendChild(style);
    }

    // Global function for PSX components to execute CRUD delete actions
    window.executeCrudDelete = async function(actionName, idParam, itemId) {
        var body = {};
        body[idParam] = Number(itemId);
        return await callServerAction(actionName, body);
    };

    // Global function to show PSX delete modal
    window.showDeleteModal = function(itemId, itemTitle, crudConfig) {
        // Store the CRUD config for later use
        window.__nextpyDeleteConfig = crudConfig;
        
        // Find the PSX component that has the modal state
        var components = window.nextpyComponents || {};
        for (var compId in components) {
            var comp = components[compId];
            if (comp && comp.stateManager) {
                // Update the component state to show modal
                comp.stateManager.set('show_modal', true);
                comp.stateManager.set('pending_id', itemId);
                comp.stateManager.set('pending_title', itemTitle || 'this item');
                
                // Also directly show the modal element if it exists
                var modal = document.querySelector('[data-delete-modal]');
                if (modal) {
                    modal.classList.remove('hidden');
                    modal.style.display = 'flex';
                }
                return true;
            }
        }
        return false;
    };

    // Global function to hide PSX delete modal
    window.hideDeleteModal = function() {
        var modal = document.querySelector('[data-delete-modal]');
        if (modal) {
            modal.classList.add('hidden');
            modal.style.display = '';
        }
        // Update the component state
        var components = window.nextpyComponents || {};
        for (var compId in components) {
            var comp = components[compId];
            if (comp && comp.stateManager) {
                comp.stateManager.set('show_modal', false);
                return true;
            }
        }
        return false;
    };

    // Global function to confirm delete and hide modal
    window.confirmDeleteModal = async function() {
        // Hide the modal first
        window.hideDeleteModal();
        
        // Find the PSX component to get the pending_id
        var components = window.nextpyComponents || {};
        for (var compId in components) {
            var comp = components[compId];
            if (comp && comp.stateManager) {
                var pendingId = comp.stateManager.get('pending_id');
                if (pendingId !== null && pendingId !== undefined) {
                    // Use the stored CRUD config
                    var config = window.__nextpyDeleteConfig || {};
                    var deleteAction = config.deleteAction || 'delete_todo';
                    var idParam = config.idParam || 'todo_id';
                    // Execute the delete action
                    return await window.executeCrudDelete(deleteAction, idParam, pendingId);
                }
                break;
            }
        }
        return null;
    };

    // Register functions with JS action runtime if available
    if (window.NextPyActionRuntime) {
        window.NextPyActionRuntime.registerFunction('executeCrudDelete', window.executeCrudDelete);
        window.NextPyActionRuntime.registerFunction('showDeleteModal', window.showDeleteModal);
        window.NextPyActionRuntime.registerFunction('hideDeleteModal', window.hideDeleteModal);
        window.NextPyActionRuntime.registerFunction('confirmDeleteModal', window.confirmDeleteModal);
    }

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
        var response = await fetch('/__nextpy/actions/execute', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({action: actionName, params: data || {}})
        });
        var result = await response.json();
        if (!response.ok || result.error) {
            var msg = 'Server action failed';
            if (result.error) {
                msg = typeof result.error === 'object' ? (result.error.message || JSON.stringify(result.error)) : result.error;
            }
            throw new Error(msg);
        }
        return result;
    }

    // Custom helper to dynamically show a Tailwind CSS confirmation modal
        function showCustomConfirm(messageText) {
        return new Promise(function (resolve) {
            // Create backdrop overlay container with a lighter 25% opacity
            var overlay = document.createElement('div');
            overlay.className = 'fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/5 bg-opacity-25 backdrop-blur-sm transition-opacity duration-200';
            
            // Create modal content card
            var card = document.createElement('div');
            card.className = 'w-full max-w-sm p-6 bg-white rounded-xl shadow-xl transform scale-100 transition-transform duration-200';
            
            // Modal header
            var title = document.createElement('h3');
            title.className = 'text-lg font-semibold text-gray-900 mb-2';
            title.textContent = 'Confirm Action';
            card.appendChild(title);
            
            // Modal body text
            var bodyText = document.createElement('p');
            bodyText.className = 'text-sm text-gray-600 mb-6';
            bodyText.textContent = messageText;
            card.appendChild(bodyText);
            
            // Modal buttons wrapper
            var actions = document.createElement('div');
            actions.className = 'flex justify-end gap-3';
            
            // Cancel Button
            var cancelBtn = document.createElement('button');
            cancelBtn.type = 'button';
            cancelBtn.className = 'px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500';
            cancelBtn.textContent = 'Cancel';
            
            // Delete (Confirm) Button
            var confirmBtn = document.createElement('button');
            confirmBtn.type = 'button';
            confirmBtn.className = 'px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500';
            confirmBtn.textContent = 'Delete';
            
            actions.appendChild(cancelBtn);
            actions.appendChild(confirmBtn);
            card.appendChild(actions);
            overlay.appendChild(card);
            
            // Append modal to body and freeze background scrolling
            document.body.appendChild(overlay);
            document.body.classList.add('nextpy-modal-open');
            
            // Handle cleanup and resolve value
            function close(result) {
                cancelBtn.removeEventListener('click', handleCancel);
                confirmBtn.removeEventListener('click', handleConfirm);
                document.body.removeChild(overlay);
                document.body.classList.remove('nextpy-modal-open');
                resolve(result);
            }
            
            function handleCancel() { close(false); }
            function handleConfirm() { close(true); }
            
            cancelBtn.addEventListener('click', handleCancel);
            confirmBtn.addEventListener('click', handleConfirm);
        });
    }

    function applyChange(root, message, config) {
        var item = message.data;
        if (message.action === 'deleted') {
            var deleted = root.querySelector('[data-nextpy-item="' + item.id + '"]');
            if (deleted) deleted.remove();
            return;
        }
        if (message.action === 'created') {
            var existing = root.querySelector('[data-nextpy-item="' + item.id + '"]');
            if (existing) return;
            var list = root.querySelector('[data-nextpy-list]');
            if (!list) return;
            var li = document.createElement('li');
            li.setAttribute('data-nextpy-item', item.id);
            li.className = 'flex items-center gap-4 p-4 rounded-lg bg-gray-50';
            var cb = document.createElement('input');
            cb.setAttribute('data-nextpy-toggle', item.id);
            cb.type = 'checkbox';
            cb.checked = !!item.completed;
            cb.className = 'w-5 h-5 text-blue-600 rounded focus:ring-blue-500';
            cb.setAttribute('aria-label', 'Complete todo');
            li.appendChild(cb);
            var span = document.createElement('span');
            span.className = 'flex-1 ' + (item.completed ? 'line-through text-gray-400' : 'text-gray-900');
            span.textContent = item.title || '';
            li.appendChild(span);
            var btn = document.createElement('button');
            btn.setAttribute('data-nextpy-delete', item.id);
            btn.type = 'button';
            btn.className = 'text-sm font-medium text-red-600 hover:text-red-800';
            btn.textContent = 'Delete';
            li.appendChild(btn);
            list.appendChild(li);
            return;
        }
        var element = root.querySelector('[data-nextpy-item="' + item.id + '"]');
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
        var toggle = element.querySelector('[data-nextpy-toggle]');
        if (toggle && item.completed !== undefined) {
            toggle.checked = item.completed;
        }
        if (item.completed !== undefined) {
            var span = element.querySelector('span');
            if (span) {
                if (item.completed) {
                    span.classList.add('line-through', 'text-gray-400');
                    span.classList.remove('text-gray-900');
                } else {
                    span.classList.remove('line-through', 'text-gray-400');
                    span.classList.add('text-gray-900');
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
                if (config.createReset !== false) form.reset();
            }
            catch (err) { error(root, err.message); }
        });
        root.addEventListener('change', async function (event) {
            if (!event.target || typeof event.target.closest !== 'function') 
                return;

            var toggle = event.target.closest('[data-nextpy-toggle]');
            if (!toggle) return;
            var itemId = toggle.dataset.nextpyToggle;
            var idParam = config.idParam || 'id';
            var body = {};
            body[idParam] = Number(itemId);
            if (config.updateFields) {
                for (var f in config.updateFields) {
                    body[f] = config.updateFields[f];
                }
            }
            try { await callServerAction(updateAction, body); }
            catch (err) { error(root, err.message); toggle.checked = !toggle.checked; }
        });
        root.addEventListener('click', async function (event) {
            if (!event.target || typeof event.target.closest !== 'function') 
                return;
            var button = event.target.closest('[data-nextpy-delete]');
            if (!button) return;
            var itemId = button.dataset.nextpyDelete;
            
            // Try to show PSX modal if deleteConfirm is "psx"
            if (config.deleteConfirm === 'psx' && window.showDeleteModal) {
                var itemTitle = 'this item';
                var listItem = button.closest('[data-nextpy-item]');
                if (listItem) {
                    var titleSpan = listItem.querySelector('span');
                    if (titleSpan) itemTitle = titleSpan.textContent;
                }
                var psxModalShown = window.showDeleteModal(Number(itemId), itemTitle, config);
                if (psxModalShown) {
                    // PSX modal handles the delete action via its own confirm button
                    return;
                }
            }
            
            // Default behavior (custom confirm modal)
            if (config.deleteConfirm !== false && config.deleteConfirm !== 'psx') {
                var confirmMsg = typeof config.deleteConfirm === 'string' ? config.deleteConfirm : 'Delete this item?';
                var confirmed = await showCustomConfirm(confirmMsg);
                if (!confirmed) return;
            }
            
            var idParam = config.idParam || 'id';
            var body = {};
            body[idParam] = Number(itemId);
            try { 
                await callServerAction(deleteAction, body); 
            } catch (err) { 
                error(root, err.message); 
            }
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
            socket.addEventListener('error', function () { 
                status(root, 'Offline'); 
            });
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
