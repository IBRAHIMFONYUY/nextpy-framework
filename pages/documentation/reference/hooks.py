"""Hooks API - NextPy Documentation"""

from nextpy.psx import component, Link, register_component, useState, useEffect
from pages.documentation._components.enhanced_codeblock import EnhancedCodeBlock

register_component("EnhancedCodeBlock", EnhancedCodeBlock)


@component
def HooksAPI():
    usestate_example = """from nextpy.psx import component, useState

@component
def Counter():
    [count, set_count] = useState(0)

    def increment():
        set_count(count + 1)

    return (
        <div>
            <p>Count: {count}</p>
            <button onclick={increment}>+1</button>
        </div>
    )"""

    useeffect_example = """from nextpy.psx import component, useState, useEffect

@component
def ScrollSpy():
    [progress, set_progress] = useState(0)

    def setup():
        def on_scroll():
            doc_height = document.documentElement.scrollHeight - window.innerHeight
            if doc_height > 0:
                set_progress((window.scrollY / doc_height) * 100)

        window.addEventListener("scroll", on_scroll)
        on_scroll()
        return lambda: window.removeEventListener("scroll", on_scroll)

    useEffect(setup, [])

    progress_style = f"width: {progress}%; height: 4px; background: blue"
    return <div style={progress_style}></div>"""

    server_effect_example = """useEffect(handle_result, [_server_result])"""

    ref_shape = '{"current": initial}'
    ph_ref = 'ref={"name"}'
    ph_if_cond = "{if cond: ...}"

    useref_example = """from nextpy.psx import interactive_component, useRef, useEffect

@interactive_component
def Drawer():
    # Mutable box that survives re-renders without triggering them
    count = useRef(0)

    def setup():
        # ref={...} renders data-psx-ref; resolve the node via getRef
        el = window.nextpy.getRef(window.nextpy._componentId, "panel")
        if el:
            el.style.maxHeight = "0px"
        return None

    useEffect(setup, [])

    def bump(e):
        count["current"] += 1   # no re-render — read it imperatively
        return None

    return (
        <div>
            <button onclick={bump}>Clicks: {count["current"]}</button>
            <div ref={"panel"} class="overflow-hidden">...</div>
        </div>
    )"""

    derived_example = """from nextpy.psx import interactive_component, useState

@interactive_component
def Search():
    [query, set_query] = useState("")
    [items, set_items] = useState([])

    # Derived values: captured at SSR, re-evaluated on the client
    # whenever a dependency changes. Order matters — define
    # dependencies before dependents.
    q = query.strip().lower()
    has_q = bool(q)
    empty_msg = "No results" if has_q and not items else ""
    input_cls = "border-blue-500" if has_q else "border-zinc-700"

    return (
        <input value={query} oninput={lambda e: set_query(e.target.value)}
               class={input_cls} />
        <p>{empty_msg}</p>
    )"""

    usefetch_example = """from nextpy.psx import component, useFetch

@component
def UserList():
    fetch = useFetch("/api/users")
    data = fetch["data"]

    return (
        <div>
            {fetch["loading"] and <p>Loading...</p>}
            {fetch["error"] and <p>{fetch["error"]}</p>}
            <ul>
                {for user in (data or []):
                    <li>{user["name"]}</li>
                }
            </ul>
        </div>
    )"""

    return (
        <div class="flex flex-col xl:flex-row items-start justify-between gap-2 w-full max-w-6xl mx-auto">
            <article class="flex-1 min-w-0 max-w-4xl antialiased text-zinc-300 selection:bg-blue-500/20 selection:text-blue-300 space-y-12 pb-24 pt-6">
                <div class="flex items-center justify-between border-b border-zinc-800/50 pb-4">
                    <div class="flex items-center gap-2 text-sm font-medium text-zinc-400">
                        <span>Documentation</span>
                        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                        <span>Reference API</span>
                        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                        <span class="text-white">Hooks API</span>
                    </div>
                </div>

                <header id="header" class="mb-12">
                    <h1 class="text-2xl sm:text-2xl font-bold tracking-tight text-white mb-6">Hooks API</h1>
                    <p class="leading-relaxed text-zinc-300">
                        Reference for NextPy hooks: <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">useState</code>, <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">useEffect</code>, and <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">useFetch</code>.
                    </p>
                </header>

                <div id="usestate" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">useState</h2>
                    <p class="text-base leading-7 text-zinc-300">
                        Declares reactive state. Destructure into a value and a setter &mdash; updates re-render only the bound DOM nodes, not the whole page.
                    </p>
                    <EnhancedCodeBlock lang="python" filename="pages/counter.py" snippet={usestate_example} />
                    <ul class="list-disc pl-6 space-y-2 text-base leading-7 text-zinc-300">
                        <li>Initial value can be any JSON-serializable Python value.</li>
                        <li>Setters accept a value or an updater function: <code class="font-mono text-xs">set_count(lambda c: c + 1)</code>.</li>
                        <li>Multiple <code class="font-mono text-xs">useState</code> calls per component are fine &mdash; each is tracked independently.</li>
                    </ul>
                </div>

                <div id="useeffect" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">useEffect</h2>
                    <p class="text-base leading-7 text-zinc-300">
                        Runs side effects after render. Pass a dependency list to control re-runs; return a cleanup function to unsubscribe.
                    </p>
                    <EnhancedCodeBlock lang="python" filename="pages/clock.py" snippet={useeffect_example} />
                    <ul class="list-disc pl-6 space-y-2 text-base leading-7 text-zinc-300">
                        <li><code class="font-mono text-xs">useEffect(fn, [])</code> &mdash; run once on mount.</li>
                        <li><code class="font-mono text-xs">useEffect(fn, [dep])</code> &mdash; re-run when <code class="font-mono text-xs">dep</code> changes.</li>
                        <li>Great for timers, scroll listeners, WebSockets, and DOM measurements.</li>
                    </ul>
                </div>

                <div id="usefetch" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">useFetch</h2>
                    <p class="text-base leading-7 text-zinc-300">
                        Fetches JSON from an API route on mount and stores the response in component state. Returns a dict with <code class="font-mono text-xs">data</code>, <code class="font-mono text-xs">loading</code>, <code class="font-mono text-xs">error</code>, and a <code class="font-mono text-xs">refetch</code> action.
                    </p>
                    <EnhancedCodeBlock lang="python" filename="pages/users.py" snippet={usefetch_example} />
                </div>

                <div id="server-state" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Server state keys</h2>
                    <p class="text-base leading-7 text-zinc-300">
                        Server actions write results into reserved state keys you can bind directly:
                    </p>
                    <ul class="list-disc pl-6 space-y-2 text-base leading-7 text-zinc-300">
                        <li><code class="font-mono text-xs">_server_result</code> &mdash; the JSON payload returned by the last <code class="font-mono text-xs">callServerAction</code>.</li>
                        <li><code class="font-mono text-xs">_server_loading</code> &mdash; boolean, true while the request is in flight.</li>
                    </ul>
                    <EnhancedCodeBlock
                        lang="python"
                        filename="pages/login.py"
                        snippet={server_effect_example}
                    />
                </div>

                <div id="useref" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">useRef</h2>
                    <p class="text-base leading-7 text-zinc-300">
                        <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">useRef(initial)</code> returns a mutable <code class="font-mono text-xs">{ref_shape}</code> box that persists across renders without triggering them — for values you mutate imperatively (counters, caches, previous values). Writing to it never re-renders; reading it in JSX gives you the SSR-time value only.
                    </p>
                    <p class="text-base leading-7 text-zinc-300">
                        For DOM nodes, prefer <code class="font-mono text-xs">{ph_ref}</code> on the element — it renders <code class="font-mono text-xs">data-psx-ref</code>, and the client runtime resolves it through <code class="font-mono text-xs">window.nextpy.getRef(componentId, name)</code> inside effects and handlers.
                    </p>
                    <EnhancedCodeBlock lang="python" filename="components/drawer.py" snippet={useref_example} />
                </div>

                <div id="derived-values" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Derived values</h2>
                    <p class="text-base leading-7 text-zinc-300">
                        Assignments in the component body become <em>derived expressions</em>: evaluated once at SSR, then re-evaluated on the client whenever a state variable they depend on changes — including chains resolved by fixpoint. Use them for anything bound into JSX: class strings, style strings, labels, filtered lists rendered through bindings.
                    </p>
                    <ul class="list-disc pl-6 space-y-2 text-base leading-7 text-zinc-300">
                        <li>Every name in the expression must be state or an <strong class="text-white">earlier</strong> derived variable — order matters.</li>
                        <li>f-string holes must be plain variable names; <code class="font-mono text-xs">props.*</code>, comprehensions and local function calls are server-only and silently drop the binding.</li>
                        <li>For conditional rendering prefer <code class="font-mono text-xs">{ph_if_cond}</code> inline expressions or dedicated conditional components — a skipped derived variable freezes at its SSR value.</li>
                    </ul>
                    <EnhancedCodeBlock lang="python" filename="components/search.py" snippet={derived_example} />
                    <p class="text-base leading-7 text-zinc-300">
                        For the full capture rules, scroll-driven UI patterns and Motion animations, see <Link href="/documentation/concepts/psx-internals" className="text-blue-400 hover:text-blue-300 underline decoration-blue-400/30 hover:decoration-blue-400">PSX Core Internals</Link>.
                    </p>
                </div>

                <footer class="py-12 flex items-center justify-between gap-6 border-t border-zinc-800/50 mt-12">
                    <div class="w-1/2">
                        <Link href="/documentation/reference/components" className="group block p-5 rounded-xl border border-zinc-800/60 bg-zinc-950/20 hover:border-zinc-700 hover:bg-zinc-900/20 transition-all">
                            <span class="block text-xs font-medium text-zinc-500 tracking-wide uppercase mb-1">Previous</span>
                            <span class="text-base font-bold text-white group-hover:text-blue-400 flex items-center gap-1 transition-colors">
                                <svg class="w-4 h-4 text-zinc-500 group-hover:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
                                Components API
                            </span>
                        </Link>
                    </div>
                    <div class="w-1/2 text-right">
                        <Link href="/documentation/reference/data-fetching" className="group block p-5 rounded-xl border border-zinc-800/60 bg-zinc-950/20 hover:border-zinc-700 hover:bg-zinc-900/20 transition-all">
                            <span class="block text-xs font-medium text-zinc-500 tracking-wide uppercase mb-1">Next</span>
                            <span class="text-base font-bold text-white group-hover:text-blue-400 flex items-center justify-end gap-1 transition-colors">
                                Data Fetching
                                <svg class="w-4 h-4 text-zinc-500 group-hover:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                            </span>
                        </Link>
                    </div>
                </footer>
            </article>

            <aside class="hidden xl:block w-64 shrink-0 sticky top-24 pt-4 pl-8 pb-24 h-[calc(100vh-6rem)] overflow-y-auto">
                <div class="text-sm">
                    <h4 class="font-semibold text-white mb-4 tracking-wide">On this page</h4>
                    <ul class="space-y-3 font-medium text-zinc-400 border-l border-zinc-800/50">
                        <li><a href="#usestate" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">useState</a></li>
                        <li><a href="#useeffect" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">useEffect</a></li>
                        <li><a href="#usefetch" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">useFetch</a></li>
                        <li><a href="#server-state" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Server state keys</a></li>
                        <li><a href="#useref" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">useRef</a></li>
                        <li><a href="#derived-values" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Derived values</a></li>
                    </ul>
                </div>
            </aside>
        </div>
    )


def getServerSideProps(context):
    return {"props": {"title": "Hooks API - NextPy Docs"}}


default = HooksAPI

