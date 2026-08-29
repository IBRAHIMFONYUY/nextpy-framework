"""
NextPy PSX JavaScript Runtime - Structured Action Execution
Replaces JS string evaluation with structured action processing
"""

# JavaScript runtime script as a constant
JS_ACTION_RUNTIME_SCRIPT = r"""
(function() {
if (window.__nextpyActionRuntimeLoaded) return;
window.__nextpyActionRuntimeLoaded = true;
/**
 * NextPy PSX JavaScript Runtime - Structured Action Execution
 * Replacing JS string evaluation with structured action processing
 */

class NextPyActionRuntime {
    constructor() {
        this.components = new Map();
        this.globalState = {};
        this.functions = new Map();
        this.dependencyMap = new Map(); // FIX: Track state dependencies
        this._registerBuiltinFunctions();
    }

    registerComponent(componentId, initialState = {}) {
        this.components.set(componentId, {
            state: { ...initialState },
            listeners: []
        });
        this.dependencyMap.set(componentId, {}); // FIX: Initialize dependency map for component
        this._ensureStateDefaults(componentId);
        // FIX: Build dependency map for conditional elements (deferred to after DOM is ready)
        setTimeout(() => this._buildDependencyMap(componentId), 100); // Delay to ensure DOM is ready
        return this.components.get(componentId);
    }

    _buildDependencyMap(componentId) {
        // FIX: Scan DOM and build dependency map for conditional elements
        const conditionalElements = document.querySelectorAll(`[data-if-condition]`);
        // FIX: Initialize dependency map for component if not exists
        if (!this.dependencyMap.has(componentId)) {
            this.dependencyMap.set(componentId, {});
        }
        
        conditionalElements.forEach(element => {
            if (element.dataset.componentId === componentId) {
                this._registerConditionalElement(element, componentId);
            }
        });
        // FIX: Set up input bindings for elements with data-bind attribute
        this._setupInputBindings(componentId);
    }
    
    _setupInputBindings(componentId) {
        // FIX: Set up automatic input bindings for elements with data-bind attribute
        const boundElements = document.querySelectorAll(`[data-bind]`);
        boundElements.forEach(element => {
            const bindSpec = element.dataset.bind;
            if (!bindSpec) return;
            
            // Parse bind specification: "value:name" or "checked:name"
            const [bindType, stateKey] = bindSpec.split(':');
            // Determine the appropriate event based on element type
            let eventType = 'input';
            if (element.tagName === 'SELECT' || element.type === 'checkbox' || element.type === 'radio') {
                eventType = 'change';
            }
            
            // Add event listener to update state when input changes
            element.addEventListener(eventType, (e) => {
                const component = this.components.get(componentId);
                if (!component) return;
                
                let newValue;
                if (bindType === 'value') {
                    newValue = e.target.value;
                } else if (bindType === 'checked') {
                    newValue = e.target.checked;
                } else {
                    newValue = e.target.value;
                }
                
                this._executeSetState(componentId, stateKey, newValue);
            });
            
            // Set initial value from state
            const component = this.components.get(componentId);
            if (component && component.state[stateKey] !== undefined) {
                if (bindType === 'value') {
                    element.value = component.state[stateKey];
                } else if (bindType === 'checked') {
                    element.checked = component.state[stateKey];
                }
            }
            
            // Listen for state changes to update input value
            this._addStateListener(componentId, stateKey, (newValue) => {
                if (bindType === 'value') {
                    element.value = newValue;
                } else if (bindType === 'checked') {
                    element.checked = newValue;
                }
            });
        });
    }
    
    _addStateListener(componentId, stateKey, callback) {
        // FIX: Add a listener for state changes
        const component = this.components.get(componentId);
        if (!component) return;
        
        component.listeners.push({ stateKey, callback });
    }

    // FIX: Public method to rebuild dependency map after DOM is ready
    rebuildDependencyMap(componentId) {
        this.dependencyMap.set(componentId, {});
        this._buildDependencyMap(componentId);
    }

    _ensureStateDefaults(componentId) {
        if (!this.components.has(componentId)) return;
        const state = this.components.get(componentId).state;
        for (const key of Object.keys(state)) {
            if (!(key in state)) state[key] = null;
        }
    }

    executeAction(action, componentId = null) {
        const { type, data } = action;

        try {
            switch (type) {
                case 'SET_STATE':
                    return this._executeSetState(data, componentId);
                case 'SET_STATE_BATCH':
                    return this._executeSetStateBatch(data, componentId);
                case 'GET_STATE':
                    return this._executeGetState(data, componentId);
                case 'CALL_FUNCTION':
                    return this._executeCallFunction(data, componentId);
                case 'CALL_METHOD':
                    return this._executeCallMethod(data, componentId);
                case 'BINARY_OP':
                    return this._executeBinaryOp(data, componentId);
                case 'UNARY_OP':
                    return this._executeUnaryOp(data, componentId);
                case 'COMPARE_OP':
                    return this._executeCompareOp(data, componentId);
                case 'BOOLEAN_OP':
                    return this._executeBooleanOp(data, componentId);
                case 'PRINT':
                    return this._executePrint(data, componentId);
                case 'CONSTANT':
                    return this._executeConstant(data);
                case 'VARIABLE':
                    return this._executeVariable(data, componentId);
                case 'LIST':
                    return this._executeList(data, componentId);
                case 'DICT':
                    return this._executeDict(data, componentId);
                case 'INDEX':
                    return this._executeIndex(data, componentId);
                case 'ATTRIBUTE':
                    return this._executeAttribute(data, componentId);
                case 'FOR_LOOP':
                    return this._executeForLoop(data, componentId);
                case 'WHILE_LOOP':
                    return this._executeWhileLoop(data, componentId);
                case 'BREAK':
                    return this._executeBreak();
                case 'CONTINUE':
                    return this._executeContinue();
                case 'TRY':
                    return this._executeTry(data, componentId);
                case 'RETURN':
                    return this._executeReturn(data);
                case 'LAMBDA':
                    return this._executeLambda(data);
                case 'JSX_UPDATE':
                    return this._executeJsxUpdate(data, componentId);
                case 'FETCH_DATA':
                    return this._executeFetchData(data, componentId);
                case 'SUBSCRIBE_CRUD_EVENT':
                    return this._executeSubscribeCrudEvent(data, componentId);
                case 'CALL_SERVER_ACTION':
                    return this._executeCallServerAction(data, componentId);
                case 'IF':
                    return this._executeIf(data, componentId);
                case 'NAVIGATE':
                    return this._executeNavigate(data, componentId);
                default:
                    console.warn(`Unknown action type: ${type}`);
                    return null;
            }
        } catch (error) {
            console.error(`Action execution error:`, error);
            if (window.NEXTPY_DEBUG) throw error;
            return null;
        }
    }

    async executeActions(actions, componentId = null) {
        const results = [];
        for (const action of actions) {
            const result = await this.executeAction(action, componentId);
            results.push(result);
        }
        return results;
    }

    _executeSetState(data, componentId) {
        const { key, value } = data;
        const evaluatedValue = this._evaluateExpression(value, componentId);

        // FIX: Require componentId to prevent state contamination
        if (!componentId || !this.components.has(componentId)) {
            console.warn('SET_STATE: componentId required or component not found:', componentId);
            return;
        }

        const component = this.components.get(componentId);
        const oldValue = component.state[key];
        component.state[key] = evaluatedValue;

        // FIX: Call state listeners for this key
        component.listeners.forEach(listener => {
            if (listener.stateKey === key) {
                listener.callback(evaluatedValue);
            }
        });

        // Trigger re-render if DOM element exists
        this._triggerComponentUpdate(componentId, key, evaluatedValue, oldValue);
    }

    _executeSetStateBatch(data, componentId) {
        const { updates } = data;

        // FIX: Require componentId to prevent state contamination
        if (!componentId || !this.components.has(componentId)) {
            console.warn('SET_STATE_BATCH: componentId required or component not found:', componentId);
            return;
        }

        const component = this.components.get(componentId);
        for (const update of updates) {
            const { key, value } = update;
            const evaluatedValue = this._evaluateExpression(value, componentId);
            const oldValue = component.state[key];
            component.state[key] = evaluatedValue;
            this._triggerComponentUpdate(componentId, key, evaluatedValue, oldValue);
        }
    }

    _executeGetState(data, componentId) {
        const { key } = data;
        
        // FIX: Require componentId to prevent state contamination
        if (!componentId || !this.components.has(componentId)) {
            console.warn('GET_STATE: componentId required or component not found:', componentId);
            return undefined;
        }
        
        return this.components.get(componentId).state[key];
    }

    _executeCallFunction(data, componentId) {
        const { function: funcName, args = [], kwargs = {} } = data;
        const evaluatedArgs = args.map(arg => this._evaluateExpression(arg, componentId));
        const evaluatedKwargs = {};

        for (const [key, value] of Object.entries(kwargs)) {
            evaluatedKwargs[key] = this._evaluateExpression(value, componentId);
        }

        if (this.functions.has(funcName)) {
            const func = this.functions.get(funcName);
            return func(...evaluatedArgs, evaluatedKwargs || {});
        } else if (typeof window[funcName] === 'function') {
            return window[funcName](...evaluatedArgs);
        } else {
            throw new Error(`Unknown function: ${funcName}`);
        }
    }

    _executeCallMethod(data, componentId) {
        const { object, method, args = [], kwargs = {} } = data;
        const evaluatedArgs = args.map(arg => this._evaluateExpression(arg, componentId));
        const evaluatedKwargs = {};

        for (const [key, value] of Object.entries(kwargs)) {
            evaluatedKwargs[key] = this._evaluateExpression(value, componentId);
        }

        if (!componentId || !this.components.has(componentId)) {
            console.warn('CALL_METHOD: componentId required or component not found:', componentId);
            throw new Error(`Cannot call method without component context`);
        }

        const component = this.components.get(componentId);
        let obj = component.state[object];

        // Handle global objects (window, document, etc.)
        if (obj === undefined || obj === null) {
            if (object === 'window' && typeof window !== 'undefined') {
                obj = window;
            } else if (object === 'document' && typeof document !== 'undefined') {
                obj = document;
            } else if (object === 'console' && typeof console !== 'undefined') {
                obj = console;
            } else if (object === 'localStorage' && typeof localStorage !== 'undefined') {
                obj = localStorage;
            } else if (object === 'Math' && typeof Math !== 'undefined') {
                obj = Math;
            } else {
                console.warn(`Object '${object}' is undefined or null, returning empty string`);
                return "";
            }
        }

        // Handle Python dict.get() as bracket notation
        if (method === 'get' && typeof obj === 'object' && !Array.isArray(obj)) {
            const key = evaluatedArgs[0];
            const defaultVal = evaluatedArgs.length > 1 ? evaluatedArgs[1] : undefined;
            if (key in obj) return obj[key];
            return defaultVal !== undefined ? defaultVal : "";
        }

        // Handle Python dict.keys(), dict.values(), dict.items()
        if (typeof obj === 'object' && !Array.isArray(obj)) {
            if (method === 'keys') return Object.keys(obj);
            if (method === 'values') return Object.values(obj);
            if (method === 'items') return Object.entries(obj);
        }

        if (obj && typeof obj[method] === 'function') {
            return obj[method](...evaluatedArgs);
        } else {
            throw new Error(`Method '${method}' not found on object '${object}' (type: ${typeof obj})`);
        }
    }


    _executeBinaryOp(data, componentId) {
        const { left, op, right } = data;
        const leftValue = this._evaluateExpression(left, componentId);
        const rightValue = this._evaluateExpression(right, componentId);

        // Array concat when either operand is an array
        if (op === '+') {
            if (Array.isArray(leftValue) && Array.isArray(rightValue)) {
                return [...leftValue, ...rightValue];
            }
            if (Array.isArray(leftValue)) {
                return [...leftValue, rightValue];
            }
            if (Array.isArray(rightValue)) {
                return [leftValue, ...rightValue];
            }
        }

        switch (op) {
            case '+': return leftValue + rightValue;
            case '-': return leftValue - rightValue;
            case '*': return leftValue * rightValue;
            case '/': return leftValue / rightValue;
            case '%': return leftValue % rightValue;
            case '**': return leftValue ** rightValue;
            case '//': return Math.floor(leftValue / rightValue);
            case '<<': return leftValue << rightValue;
            case '>>': return leftValue >> rightValue;
            case '|': return leftValue | rightValue;
            case '^': return leftValue ^ rightValue;
            case '&': return leftValue & rightValue;
            default:
                throw new Error(`Unknown binary operator: ${op}`);
        }
    }

    _executeUnaryOp(data, componentId) {
        const { op, operand } = data;
        const operandValue = this._evaluateExpression(operand, componentId);
        
        switch (op) {
            case '+': return +operandValue;
            case '-': return -operandValue;
            case 'not': return !operandValue;
            case '~': return ~operandValue;
            default:
                throw new Error(`Unknown unary operator: ${op}`);
        }
    }

    _executeCompareOp(data, componentId) {
        const { left, ops, comparators } = data;
        const leftValue = this._evaluateExpression(left, componentId);
        const comparatorValues = comparators.map(c => this._evaluateExpression(c, componentId));

        let result = true;
        for (let i = 0; i < ops.length && i < comparatorValues.length; i++) {
            const op = ops[i];
            const comparator = comparatorValues[i];

            if (i === 0) {
                switch (op) {
                    case '==': result = leftValue == comparator; break;
                    case '!=': result = leftValue != comparator; break;
                    case '<': result = leftValue < comparator; break;
                    case '<=': result = leftValue <= comparator; break;
                    case '>': result = leftValue > comparator; break;
                    case '>=': result = leftValue >= comparator; break;
                    case 'is': result = leftValue === comparator; break;
                    case 'is not': result = leftValue !== comparator; break;
                    case 'in':
                        result = Array.isArray(comparator)
                            ? comparator.includes(leftValue)
                            : leftValue in comparator;
                        break;
                    case 'not in':
                        result = Array.isArray(comparator)
                            ? !comparator.includes(leftValue)
                            : !(leftValue in comparator);
                        break;
                    default:
                        throw new Error(`Unknown comparison operator: ${op}`);
                }
            } else {
                // Chain comparisons (simplified)
                const prevComparator = comparatorValues[i - 1];
                switch (op) {
                    case '<': result = result && prevComparator < comparator; break;
                    case '<=': result = result && prevComparator <= comparator; break;
                    case '>': result = result && prevComparator > comparator; break;
                    case '>=': result = result && prevComparator >= comparator; break;
                    default:
                        break;
                }
            }
        }

        return result;
    }

    _executeBooleanOp(data, componentId) {
        const { op, values } = data;
        const evaluatedValues = values.map(v => this._evaluateExpression(v, componentId));
        const trimmedOp = (op || '').trim();
        
        switch (trimmedOp) {
            case 'and': return evaluatedValues.every(v => v);
            case 'or': return evaluatedValues.some(v => v);
            case '&&': return evaluatedValues.every(v => v);
            case '||': return evaluatedValues.some(v => v);
            default:
                throw new Error(`Unknown boolean operator: '${trimmedOp}'`);
        }
    }

    _executePrint(data, componentId) {
        const { args = [] } = data;
        const evaluatedArgs = args.map(arg => this._evaluateExpression(arg, componentId));
        console.log(...evaluatedArgs);
    }

    _executeConstant(data) {
        return data.value;
    }

    _executeVariable(data, componentId) {
        const { name } = data;
        
        // FIX: Only check component state to prevent cross-component contamination
        if (!componentId || !this.components.has(componentId)) {
            console.warn('VARIABLE: componentId required or component not found:', componentId);
            throw new Error(`Unknown variable: ${name} (no component context)`);
        }
        
        const component = this.components.get(componentId);
        if (name in component.state) {
            return component.state[name];
        }
        
        // Only allow window object access for built-in functions/constants
        if (name in window && typeof window[name] !== 'undefined') {
            return window[name];
        }
        
        throw new Error(`Unknown variable: ${name} in component ${componentId}`);
    }

    _executeList(data, componentId) {
        const { elements } = data;
        return elements.map(el => this._evaluateExpression(el, componentId));
    }

    _executeDict(data, componentId) {
        const { keys, values } = data;
        const result = {};
        
        for (let i = 0; i < keys.length && i < values.length; i++) {
            const key = this._evaluateExpression(keys[i], componentId);
            const value = this._evaluateExpression(values[i], componentId);
            result[key] = value;
        }
        
        return result;
    }

    _executeIndex(data, componentId) {
        const { value, slice } = data;
        const valueObj = this._evaluateExpression(value, componentId);
        const sliceValue = this._evaluateExpression(slice, componentId);
        
        return valueObj[sliceValue];
    }

    _executeAttribute(data, componentId) {
        const { object, attr } = data;
        const obj = this._evaluateExpression(object, componentId);
        
        return obj[attr];
    }

    async _executeFetchData(data, componentId) {
        const { url, options, dataKey, loadingKey, errorKey } = data;
        const component = this.components.get(componentId);
        if (!component) {
            console.warn('FETCH_DATA: component not found:', componentId);
            return null;
        }

        // Set loading state
        if (loadingKey) {
            component.state[loadingKey] = true;
            this._triggerComponentUpdate(componentId, loadingKey, true);
        }
        if (errorKey) {
            component.state[errorKey] = null;
            this._triggerComponentUpdate(componentId, errorKey, null);
        }

        try {
            const fetchOptions = options || {};
            const response = await fetch(url, fetchOptions);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type') || '';
            let result;
            if (contentType.includes('application/json')) {
                result = await response.json();
            } else {
                result = await response.text();
            }

            if (dataKey) {
                component.state[dataKey] = result;
                this._triggerComponentUpdate(componentId, dataKey, result);
            }
        } catch (err) {
            console.error('FETCH_DATA error:', err);
            if (errorKey) {
                component.state[errorKey] = err.message || String(err);
                this._triggerComponentUpdate(componentId, errorKey, err.message || String(err));
            }
        } finally {
            if (loadingKey) {
                component.state[loadingKey] = false;
                this._triggerComponentUpdate(componentId, loadingKey, false);
            }
        }
    }

    async _executeSubscribeCrudEvent(data, componentId) {
        const { eventKey, resource } = data;
        const component = this.components.get(componentId);
        if (!component) {
            console.warn('SUBSCRIBE_CRUD_EVENT: component not found:', componentId);
            return null;
        }

        const handler = (e) => {
            const detail = e.detail || {};
            if (resource && detail.config && detail.config.resource !== resource) return;

            this._executeSetState({key: eventKey, value: detail}, componentId);
        };

        window.addEventListener('nextpy:crud:changed', handler);

        const cleanupFn = () => {
            window.removeEventListener('nextpy:crud:changed', handler);
        };

        if (window.nextpyComponents && window.nextpyComponents[componentId]) {
            window.nextpyComponents[componentId].unsubscribers.push(cleanupFn);
        }

        return cleanupFn;
    }

    async _executeCallServerAction(data, componentId) {
        let actionName = data.action;
        let params = data.params || {};

        // Resolve action name if it's a dynamic value
        if (actionName && typeof actionName === 'object' && actionName.type) {
            actionName = this._evaluateExpression(actionName, componentId);
        }
        if (params && typeof params === 'object' && params.type) {
            params = this._evaluateExpression(params, componentId);
        }

        const component = componentId ? this.components.get(componentId) : null;

        // Store loading state
        if (component) {
            component.state['_server_loading'] = true;
            component.state['_server_error'] = null;
            this._triggerComponentUpdate(componentId, '_server_loading', true);
        }

        try {
            const response = await fetch('/__nextpy/actions/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify({ action: actionName, params: params }),
            });

            const result = await response.json();

            if (component) {
                component.state['_server_loading'] = false;
                component.state['_server_result'] = result;
                this._triggerComponentUpdate(componentId, '_server_loading', false);
                this._triggerComponentUpdate(componentId, '_server_result', result);
            }

            return result;
        } catch (err) {
            console.error('CALL_SERVER_ACTION error:', err);
            if (component) {
                component.state['_server_loading'] = false;
                component.state['_server_error'] = err.message || String(err);
                this._triggerComponentUpdate(componentId, '_server_loading', false);
                this._triggerComponentUpdate(componentId, '_server_error', err.message || String(err));
            }
            return { success: false, error: err.message || String(err) };
        }
    }

    async _executeIf(data, componentId) {
        const { condition, then: thenActions, else: elseActions } = data;
        const result = this._evaluateExpression(condition, componentId);

        if (result) {
            if (thenActions && thenActions.length > 0) {
                await this.executeActions(thenActions, componentId);
            }
        } else {
            if (elseActions && elseActions.length > 0) {
                await this.executeActions(elseActions, componentId);
            }
        }
        return null;
    }

    _executeNavigate(data, componentId) {
        const { url } = data;
        const resolvedUrl = typeof url === 'object' ? this._evaluateExpression(url, componentId) : url;
        if (window.__nextpyNavigate) {
            window.__nextpyNavigate(resolvedUrl);
        } else {
            window.location.href = resolvedUrl;
        }
    }

    _evaluateExpression(expr, componentId = null) {
        if (expr === null || expr === undefined) {
            return null;
        } else if (typeof expr === 'object' && expr.type) {
            return this.executeAction(expr, componentId);
        } else {
            return expr;
        }
    }

    _triggerComponentUpdate(componentId, key, newValue, oldValue) {
        // Sync to hydration component's StateManager to trigger DOM data-bind updates
        if (window.nextpyComponents && window.nextpyComponents[componentId]) {
            const hydComp = window.nextpyComponents[componentId];
            if (hydComp.stateManager && hydComp.stateManager.state[key] !== newValue) {
                hydComp.stateManager.set(key, newValue);
            }
        }

        // Find DOM elements that depend on this state (legacy data-state-* attributes)
        const elements = document.querySelectorAll(`[data-state-${key}]`);
        elements.forEach(element => {
            if (element.dataset.componentId === componentId) {
                element.textContent = newValue;
            }
        });
        
        // FIX: Re-evaluate ALL conditional elements for this component on ANY state change.
        // Conditions reference derived Python variables (user, is_employer, etc.) that
        // don't match state keys (_fetch_data_0, etc.), so we can't rely on the
        // dependency map for targeted updates. Instead, re-evaluate all conditionals.
        // Also update layout elements with empty data-component-id that reference the
        // same state (e.g., layout nav conditionals for user/login).
        const allConditionals = document.querySelectorAll(`[data-if-condition]`);
        const component = this.components.get(componentId);
        allConditionals.forEach(element => {
            if (element.dataset.componentId === componentId) {
                const condition = element.dataset.ifCondition;
                if (condition) {
                    this._updateConditionalElement(element, componentId, condition);
                }
            } else if (!element.dataset.componentId && component) {
                // Layout element with empty component ID — update using this component's state
                const condition = element.dataset.ifCondition;
                if (condition) {
                    this._updateConditionalElement(element, componentId, condition);
                }
            }
        });
        
        // Trigger custom event
        const event = new CustomEvent('nextpy:stateChange', {
            detail: { componentId, key, newValue, oldValue }
        });
        document.dispatchEvent(event);
    }

    _updateConditionalElement(element, componentId, condition) {
        // Evaluate the condition with current state
        const component = this.components.get(componentId);
        if (!component) {
            return;
        }
        
        try {
            // FIX: Safe expression evaluation
            const result = this._evaluateCondition(condition, component.state);
            
            // Get the true and false branches from data attributes
            const trueContent = element.dataset.ifTrue || '';
            const falseContent = element.dataset.ifFalse || '';
            
            // FIX: Unescape HTML content before setting as innerHTML
            const unescapeHtml = (html) => {
                const textArea = document.createElement('textarea');
                textArea.innerHTML = html;
                return textArea.value;
            };
            
            // Update the element content based on condition result
            if (result) {
                element.innerHTML = unescapeHtml(trueContent);
            } else {
                element.innerHTML = unescapeHtml(falseContent);
            }
        } catch (error) {
            console.error('Conditional update error:', error);
        }
    }

    _evaluateCondition(expr, state) {
        // Derive common Python variables from fetch data before evaluating
        const derived = this._deriveVariables(state);
        
        // Merge derived variables with state for evaluation
        const fullState = { ...state, ...derived };
        
        // Convert Python operators to JS operators
        let evalExpr = expr
            .replace(/\bnot\s+/g, '!')          // Python 'not' -> JS '!'
            .replace(/\band\b/g, '&&')           // Python 'and' -> JS '&&'
            .replace(/\bor\b/g, '||')            // Python 'or' -> JS '||'
            .replace(/\bNone\b/g, 'null')        // Python 'None' -> JS 'null'
            .replace(/\bTrue\b/g, 'true')        // Python 'True' -> JS 'true'
            .replace(/\bFalse\b/g, 'false')      // Python 'False' -> JS 'false'
            .replace(/\blen\((\w+)\)/g, '$1.length')  // Python 'len(x)' -> JS 'x.length'
            .replace(/\b(\w+)\.get\(([^)]+)\)/g, '$1[$2]');  // Python 'x.get("k")' -> JS 'x["k"]'
        
        // Safe condition evaluation with proper variable substitution
        // Replace state variable names with their values
        const replacedKeys = new Set();
        for (const [key, value] of Object.entries(fullState)) {
            if (evalExpr === key) {
                evalExpr = typeof value === 'string' ? `'${value}'` : JSON.stringify(value);
                replacedKeys.add(key);
            } else {
                const regex = new RegExp(`\\b${key}\\b`, 'g');
                if (regex.test(evalExpr)) {
                    evalExpr = evalExpr.replace(regex, typeof value === 'string' ? `'${value}'` : JSON.stringify(value));
                    replacedKeys.add(key);
                }
            }
        }
        
        // FIX: Treat any remaining undefined identifiers as null (like Python's None)
        const idRegex = /\b([a-zA-Z_][a-zA-Z0-9_]*)\b/g;
        let match;
        const remainingIds = new Set();
        while ((match = idRegex.exec(evalExpr)) !== null) {
            const id = match[1];
            if (!replacedKeys.has(id) && !['true', 'false', 'null', 'undefined', 'NaN', 'Infinity', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'abs', 'min', 'max', 'sum', 'round', 'any', 'all'].includes(id)) {
                remainingIds.add(id);
            }
        }
        
        // Build variable declarations for undefined identifiers
        const varDeclarations = Array.from(remainingIds).map(id => `let ${id} = null;`).join(' ');
        
        try {
            return Function(`"use strict"; ${varDeclarations} return (${evalExpr})`)();
        } catch (e) {
            console.warn('Failed to evaluate condition:', expr, '->', evalExpr, e);
            return false;
        }
    }

    _deriveVariables(state) {
        // Derive common Python variables from fetch data
        // This bridges the gap between Python server-side derived variables
        // and client-side state that only has raw fetch data
        const derived = {};
        
        for (const [key, value] of Object.entries(state)) {
            // Only process fetch data keys
            if (!key.startsWith('_fetch_data_')) continue;
            if (value === null || value === undefined || typeof value !== 'object') continue;
            
            // Pattern 1: Direct response like {"user": {...}} from get_me
            // The Python code does: me_data.get("data") or {} then me.get("user")
            // At client-side, _fetch_data_0 IS the raw response (no wrapping)
            // But Python's useFetch wraps it in {"data": raw_response}
            // So _fetch_data_0 = {"data": {"user": {...}}} or {"data": {"user": None}}
            const data = value.data !== undefined ? value.data : value;
            if (data === null || data === undefined || typeof data !== 'object') continue;
            
            // Extract 'user' from get_me response
            if (data.user !== undefined && !derived.user) {
                derived.user = data.user;
                derived.not = data.user ? false : true;
                if (data.user) {
                    derived.is_employer = data.user.role === 'employer';
                    derived.is_jobseeker = data.user.role !== 'employer';
                } else {
                    derived.is_employer = false;
                    derived.is_jobseeker = false;
                }
            }
            
            // Pattern 2: get_my_jobs returns {"data": [...]} or {"data": {"data": [...]}}
            if (Array.isArray(data) && !derived.my_jobs) {
                derived.my_jobs = data;
                derived.has_my_jobs = data.length > 0;
            } else if (data.data && Array.isArray(data.data) && !derived.my_jobs) {
                derived.my_jobs = data.data;
                derived.has_my_jobs = data.data.length > 0;
            } else if (data.jobs && Array.isArray(data.jobs) && !derived.my_jobs) {
                derived.my_jobs = data.jobs;
                derived.has_my_jobs = data.jobs.length > 0;
            }
            
            // Pattern 3: get_my_applications
            if (Array.isArray(data) && !derived.my_apps) {
                derived.my_apps = data;
                derived.has_my_apps = data.length > 0;
            } else if (data.data && Array.isArray(data.data) && !derived.my_apps) {
                derived.my_apps = data.data;
                derived.has_my_apps = data.data.length > 0;
            } else if (data.applications && Array.isArray(data.applications) && !derived.my_apps) {
                derived.my_apps = data.applications;
                derived.has_my_apps = data.applications.length > 0;
            }
        }
        
        return derived;
    }

    _registerConditionalElement(element, componentId) {
        // FIX: Register conditional element and build dependency map
        const condition = element.dataset.ifCondition;
        if (!condition) return;
        
        // FIX: Initialize dependency map for component if not exists
        if (!this.dependencyMap.has(componentId)) {
            this.dependencyMap.set(componentId, {});
        }
        
        const componentDeps = this.dependencyMap.get(componentId);
        const component = this.components.get(componentId);
        
        // Extract state dependencies from condition using exact match or word boundary
        for (const key of Object.keys(component.state)) {
            // Try exact match first, then word boundary
            const exactMatch = condition === key;
            const regex = new RegExp(`\\b${key}\\b`);
            const wordBoundaryMatch = regex.test(condition);
            
            if (exactMatch || wordBoundaryMatch) {
                if (!componentDeps[key]) {
                    componentDeps[key] = [];
                }
                if (!componentDeps[key].includes(element)) {
                    componentDeps[key].push(element);
                }
            }
        }
    }

    _registerBuiltinFunctions() {
        // Register built-in functions
        this.functions.set('len', (obj) => {
            if (Array.isArray(obj)) return obj.length;
            if (typeof obj === 'object') return Object.keys(obj).length;
            if (typeof obj === 'string') return obj.length;
            return 0;
        });

        this.functions.set('str', (obj) => String(obj));
        this.functions.set('int', (obj) => parseInt(obj));
        this.functions.set('float', (obj) => parseFloat(obj));
        this.functions.set('bool', (obj) => Boolean(obj));
        this.functions.set('list', (obj) => Array.from(obj));
        this.functions.set('dict', (obj) => ({ ...obj }));
        this.functions.set('abs', Math.abs);
        this.functions.set('min', Math.min);
        this.functions.set('max', Math.max);
        this.functions.set('sum', (arr) => arr.reduce((a, b) => a + b, 0));
        this.functions.set('any', (arr) => arr.some(Boolean));
        this.functions.set('all', (arr) => arr.every(Boolean));
        this.functions.set('round', Math.round);

        // Console functions
        this.functions.set('console_log', console.log);
        this.functions.set('alert', (msg) => alert(msg));
    }

    _executeForLoop(data, componentId) {
        // Placeholder implementation
        // For loops require more complex execution context
        console.warn('FOR_LOOP not yet implemented in JS runtime');
    }

    _executeWhileLoop(data, componentId) {
        // Placeholder implementation
        // While loops require more complex execution context
        console.warn('WHILE_LOOP not yet implemented in JS runtime');
    }

    _executeBreak() {
        // Placeholder implementation
        // Break requires loop context
        throw new Error('BREAK not yet implemented');
    }

    _executeContinue() {
        // Placeholder implementation
        // Continue requires loop context
        throw new Error('CONTINUE not yet implemented');
    }

    _executeTry(data, componentId) {
        // Placeholder implementation
        // Try/except requires exception handling context
        console.warn('TRY not yet implemented in JS runtime');
    }

    _executeReturn(data) {
        // Placeholder implementation
        // Return requires function context
        const value = this._evaluateExpression(data.value);
        throw { type: 'RETURN', value };
    }

    _executeLambda(data) {
        // Placeholder implementation
        // Lambdas require function creation context
        const { args, body } = data;
        return (...lambdaArgs) => {
            // Create a scope for lambda arguments
            const scope = {};
            args.forEach((arg, i) => {
                scope[arg] = lambdaArgs[i];
            });
            return this._evaluateExpression(body);
        };
    }

    _executeJsxUpdate(data, componentId) {
        // Placeholder implementation
        // JSX updates require DOM manipulation context
        console.warn('JSX_UPDATE not yet implemented in JS runtime');
    }
}

// Global runtime instance
window.NextPyActionRuntime = new NextPyActionRuntime();

// Handler execution function
window.executeNextPyActions = async function(actions, componentId = null) {
    return await window.NextPyActionRuntime.executeActions(actions, componentId);
};

// Component registration function
window.registerNextPyComponent = function(componentId, initialState = {}) {
    return window.NextPyActionRuntime.registerComponent(componentId, initialState);
};

// SPA-style navigation function — called by lambda handlers after actions
window.navigateTo = function(url) {
    if (window.__nextpyNavigate) {
        window.__nextpyNavigate(url);
    } else if (window.htmx) {
        const target = document.getElementById('main-content') || document.querySelector('main');
        if (target) {
            htmx.ajax('GET', url, { target: '#main-content', swap: 'innerHTML' });
            history.pushState({}, '', url);
            return;
        }
        window.location.href = url;
    } else {
        window.location.href = url;
    }
};

// SPA-style reload — re-fetches current page content without full reload
window.spaReload = function() {
    const url = window.location.pathname + window.location.search;
    if (window.__nextpyNavigate) {
        window.__nextpyNavigate(url, true);
    } else if (window.htmx) {
        const target = document.getElementById('main-content') || document.querySelector('main');
        if (target) {
            htmx.ajax('GET', url, { target: '#main-content', swap: 'innerHTML' });
            return;
        }
    }
    window.location.reload();
};

console.log('[NextPy] Action Runtime loaded');
})();
"""
