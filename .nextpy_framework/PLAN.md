# Fix Plan: 3 Bugs in InteractiveComponent System

## Bug 1: Server crash — `{if error:}` treated as expression

### Symptom
```
Error rendering route: Expression evaluation failed: if error:\n{error}
Error: Invalid syntax: if error:\n{error}
```

### Root Cause
In `pages/jobs/register.py` (and login.py, create.py, [id].py), JSX blocks like:
```python
{if error:
    <div>{error}</div>
}
```
are passed through `process_python_logic()` in `runtime.py`. The `find_matching_if_block()` function uses **brace-counting** that counts ALL `{` and `}` characters, including nested `{error}` expressions inside the body. The body `{error}` has a `{` and `}` which increments/decrements the brace counter, but this is correct — the real problem is that the `find_matching_if_block` function starts `brace_count` at 1, but the initial `{` in `{if error:` is NOT counted separately — the function finds `{if ` by string search, not by counting.

**Actually**, tracing through the logic, the brace counting appears correct. The real bug is likely that `find_matching_if_block` doesn't find the block because the `else_pos = text.find('{else:', end_condition)` at line 962 **intercepts** the search when there's no `{else:}` block — it returns -1, so the `else` branch runs. But the `else` branch has a subtle issue: when the `while` loop exhausts (pos >= len(text)), the `else` clause runs `pos += 1`, and then `brace_count == 0` check at line 1002 fails because `brace_count` never reached 0 (no matching `}` found).

Wait — actually, the real problem is simpler. Look at the register.py structure:
```python
return (
    <div>
        {if error:
            <div class="...">{error}</div>
        }
        <form>...</form>
    </div>
)
```

The JSX preprocessor wraps this as `psx("""...""")`. Inside `psx()`, `process_python_logic()` is called. The `{if error:` block starts with `{if ` and the condition is `error`. The brace-counting should find the matching `}`. BUT: the `}` at line 45 of register.py is on its own line with significant indentation. The brace-counting in `find_matching_if_block` counts braces in the raw text including HTML attributes, CSS classes, etc. If the HTML content itself contains `{` or `}` characters (unlikely here), it would throw off counting.

**The ACTUAL root cause**: After more careful analysis, the expression being evaluated is `if error:\n{error}` — this is the **condition string** followed by the body. This looks like the PSX parser is treating the entire `{if error:...{error}...}` block as a single expression node, and the expression evaluator receives the raw text between `{` and `}` (using the regex `\{([^{}]+?)\}`).

But the regex `[^{}]+?` can't match across nested `{error}`. So the regex matches `{if error:` — no, it can't, because there's no `}` immediately after `if error:`.

**Real fix**: The issue is that `{if error:}` blocks with the **colon syntax** (as opposed to `{if condition}...{/if}` syntax) have a multi-line body that contains `{error}` — a nested expression. The brace-counting in `find_matching_if_block` correctly counts to find the outer `}`, but the problem is that `process_python_logic` at line 1068 calls `engine.evaluate(condition)` where `condition = "error"`. If `error` is in context as `""` (from `useState("")`), this evaluates to falsy, and `processed_content = ''`. But the `wrapped_content` still embeds `data-if-true` with the processed body. This should work.

**Final diagnosis**: The crash happens on a DIFFERENT page (not dashboard) — likely register.py or login.py — when the route `/jobs/dashboard` loads AND the server also pre-renders sibling routes. The error is a side-effect. The dashboard itself renders fine but shows "Please log in".

### Fix
**File**: `runtime.py`, `process_python_logic` function

The `find_matching_if_block` at line 947 needs to properly handle the case where `engine.evaluate(condition)` fails (e.g., the variable name `error` could collide with Python keywords or not be in context). Currently the except at line 1093 silently swallows errors and skips the block, leaving raw `{if error:...}` text in the result. The PSX parser then tries to parse it as an expression.

**Change**: In the `except` block at line 1093, instead of silently skipping, render a safe fallback (empty string or debug comment), and ensure the raw `{if...}` text is removed from the result.

---

## Bug 2: Dashboard always shows "Please log in"

### Symptom
Dashboard renders the `if user is None: return (...)` early-return block, even though `useFetch` successfully fetches `{success: true, data: {...}}`.

### Root Cause
In `pages/jobs/dashboard.py` lines 66-72:
```python
if user is None:
    return (
        <div class="py-16 text-center">
            <h1>Please log in</h1>
            ...
        </div>
    )
```

This is a **Python-level** early return. At server render time:
1. `useFetch(...)` returns a placeholder dict like `{"_dataKey": "_fetch_data_0", ...}`
2. `me_data.get("data", {})` returns `{}` (no "data" key in placeholder)
3. `user` = `None`
4. The `if user is None:` guard triggers → returns login prompt
5. The rest of the JSX (employer dashboard, job seeker dashboard) is **never rendered**
6. When `useFetch` data arrives on the client, the full JSX is never rendered because the Python function already returned early

The `{if is_employer:...}` blocks in the JSX (lines 87-151) are **unreachable** because of the early return.

### Fix
**File**: `pages/jobs/dashboard.py`

Remove the Python-level early return. Instead, use `{if user:}` / `{if not user:}` blocks in the JSX to handle both states. The full JSX tree must always be returned so the PSX parser can generate both branches for client-side conditional rendering.

Change from:
```python
if user is None:
    return (<div>Please log in</div>)
return (<div>...full dashboard...</div>)
```

To:
```python
return (
    <div>
        {if not user:
            <div class="py-16 text-center">
                <h1>Please log in</h1>
                ...
            </div>
        }
        {if user:
            <div>...full dashboard...</div>
        }
    </div>
)
```

---

## Bug 3: 0 conditional elements in DOM

### Symptom
JS console shows: `Building dependency map for component psx_component_3 found 0 conditional elements`

### Root Cause
The `{if ...}` blocks inside JSX return statements are processed by `process_python_logic()` which wraps them in `<span data-if-condition="..." data-if-true="..." data-if-false="...">`. However, the `_buildDependencyMap` in `js_actions_runtime.py` at line 36 queries for `[data-if-condition]` elements:

```javascript
const conditionalElements = document.querySelectorAll(`[data-if-condition]`);
```

The problem is twofold:
1. The `<span data-if-condition>` elements ARE generated by `process_python_logic`, but the `data-if-true` and `data-if-false` attributes contain HTML-escaped content that may be empty (because the condition variables are empty strings at render time).
2. More importantly: the `_buildDependencyMap` runs with a 100ms delay (line 30), but by then the DOM may not have the conditional elements because the hydration script replaces innerHTML.

### Fix
Two changes needed:

**A. File**: `pages/jobs/dashboard.py` — After fixing Bug 2, the `{if}` blocks will actually be rendered (instead of being behind an unreachable early return).

**B. File**: `js_actions_runtime.py` — The `_buildDependencyMap` function needs to also scan for `[data-if-condition]` elements that may be inside the component's DOM, and it needs to read the `data-component-id` attribute to match elements to components. Currently it checks `element.dataset.componentId === componentId` but many conditional spans may not have `data-component-id` set.

Additionally, the `process_python_logic` function at line 1087 adds `data-component-id="{component_id}"` to the wrapped span, but the `component_id` comes from `enhanced_context.get('_component_id', '')` which may be empty if `_component_id` wasn't passed through the context properly.

---

## Implementation Order

1. **Fix Bug 2** (dashboard.py) — Remove early return, use `{if}` blocks
2. **Fix Bug 1** (runtime.py) — Make `process_python_logic` robust against `{if error:}` evaluation failures
3. **Fix Bug 3** (runtime.py + js_actions_runtime.py) — Ensure `data-component-id` is set on conditional spans and `_buildDependencyMap` finds them

## Files to Modify
1. `pages/jobs/dashboard.py` — Remove early return, use conditional rendering
2. `.nextpy_framework/nextpy/psx/core/runtime.py` — Fix `process_python_logic` error handling for `{if}` blocks
3. `.nextpy_framework/nextpy/psx/runtime/js_actions_runtime.py` — Fix dependency map building
