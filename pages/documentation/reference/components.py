"""Components API - NextPy Documentation"""

from nextpy.psx import component, Link, register_component
from pages.documentation._components.enhanced_codeblock import EnhancedCodeBlock

register_component("EnhancedCodeBlock", EnhancedCodeBlock)


@component
def ComponentsAPI():
    builtins_example = """from nextpy.psx import (
    component, Link, Head, Meta, Title, Script, Image,
    Motion, AnimatePresence, Form, Input, Button, Card,
)

@component
def Example():
    return (
        <div>
            <Head>
                <Title>My Page</Title>
                <Meta name="description" content="..." />
            </Head>
            <Link href="/about">About</Link>
            <Motion initial={{"opacity": 0}} animate={{"opacity": 1}}>
                <Card>Hello</Card>
            </Motion>
        </div>
    )"""

    custom_example = """from nextpy.psx import component, register_component, Props

@component
def Badge(props):
    return <span class="badge">{props.get("label", "")} </span>

register_component("Badge", Badge)"""

    return (
        <div class="flex flex-col xl:flex-row items-start justify-between gap-2 w-full max-w-6xl mx-auto">
            <article class="flex-1 min-w-0 max-w-4xl antialiased text-zinc-300 selection:bg-blue-500/20 selection:text-blue-300 space-y-12 pb-24 pt-6">
                <div class="flex items-center justify-between border-b border-zinc-800/50 pb-4">
                    <div class="flex items-center gap-2 text-sm font-medium text-zinc-400">
                        <span>Documentation</span>
                        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                        <span>Reference API</span>
                        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                        <span class="text-white">Components API</span>
                    </div>
                </div>

                <header id="header" class="mb-12">
                    <h1 class="text-2xl sm:text-2xl font-bold tracking-tight text-white mb-6">Components API</h1>
                    <p class="leading-relaxed text-zinc-300">
                        Reference for NextPy built-in components, custom components, and the hooks they expose.
                    </p>
                </header>

                <div id="builtins" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Built-in components</h2>
                    <p class="text-base leading-7 text-zinc-300">
                        Import everything from <code class="font-mono text-xs">nextpy.psx</code>. All HTML elements are available as tags; these are the framework-provided components:
                    </p>
                    <div class="overflow-x-auto rounded-xl border border-zinc-800/60">
                        <table class="w-full text-sm">
                            <thead class="bg-zinc-900/60 text-zinc-300">
                                <tr>
                                    <th class="text-left px-4 py-3 font-semibold">Component</th>
                                    <th class="text-left px-4 py-3 font-semibold">Purpose</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-zinc-800/60 text-zinc-400">
                                <tr><td class="px-4 py-3 font-mono text-xs text-zinc-200">Link</td><td class="px-4 py-3">Client-side navigation with prefetching and SPA routing.</td></tr>
                                <tr><td class="px-4 py-3 font-mono text-xs text-zinc-200">Head / Title / Meta</td><td class="px-4 py-3">Per-page metadata injected into the document head.</td></tr>
                                <tr><td class="px-4 py-3 font-mono text-xs text-zinc-200">Script / Image</td><td class="px-4 py-3">Script tags and optimized image rendering.</td></tr>
                                <tr><td class="px-4 py-3 font-mono text-xs text-zinc-200">Motion / AnimatePresence</td><td class="px-4 py-3">Declarative animations and exit transitions.</td></tr>
                                <tr><td class="px-4 py-3 font-mono text-xs text-zinc-200">Form / Input / Button</td><td class="px-4 py-3">Form primitives wired to the event system.</td></tr>
                                <tr><td class="px-4 py-3 font-mono text-xs text-zinc-200">Card / Navbar / NavItem</td><td class="px-4 py-3">Layout and navigation helpers.</td></tr>
                                <tr><td class="px-4 py-3 font-mono text-xs text-zinc-200">Conditional / Loop / ErrorBoundary / Suspense</td><td class="px-4 py-3">Control-flow and resilience primitives.</td></tr>
                            </tbody>
                        </table>
                    </div>
                    <EnhancedCodeBlock lang="python" filename="pages/example.py" snippet={builtins_example} />
                </div>

                <div id="custom-components" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Custom components</h2>
                    <p class="text-base leading-7 text-zinc-300">
                        Define components with <code class="font-mono text-xs">@component</code>, receive props as a dict, and register them for use in JSX:
                    </p>
                    <EnhancedCodeBlock lang="python" filename="components/badge.py" snippet={custom_example} />
                </div>

                <div id="hooks" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Hooks</h2>
                    <p class="text-base leading-7 text-zinc-300">
                        React-style hooks are exported from <code class="font-mono text-xs">nextpy.psx</code>:
                    </p>
                    <ul class="list-disc pl-6 space-y-2 text-base leading-7 text-zinc-300">
                        <li><strong class="text-zinc-200">Core:</strong> <code class="font-mono text-xs">useState</code>, <code class="font-mono text-xs">useEffect</code>, <code class="font-mono text-xs">useRef</code>, <code class="font-mono text-xs">useMemo</code>, <code class="font-mono text-xs">useCallback</code>, <code class="font-mono text-xs">useReducer</code>, <code class="font-mono text-xs">useContext</code></li>
                        <li><strong class="text-zinc-200">Custom:</strong> <code class="font-mono text-xs">useCounter</code>, <code class="font-mono text-xs">useToggle</code>, <code class="font-mono text-xs">useLocalStorage</code>, <code class="font-mono text-xs">useFetch</code>, <code class="font-mono text-xs">useAction</code>, <code class="font-mono text-xs">useDebounce</code>, <code class="font-mono text-xs">useInterval</code>, <code class="font-mono text-xs">usePrevious</code>, <code class="font-mono text-xs">useAsync</code>, <code class="font-mono text-xs">useMediaQuery</code>, <code class="font-mono text-xs">useGeolocation</code>, <code class="font-mono text-xs">usePerformance</code></li>
                    </ul>
                    <p class="text-base leading-7 text-zinc-300">
                        See the <Link href="/documentation/reference/hooks" className="text-blue-400 hover:text-blue-300 underline underline-offset-4">Hooks API</Link> page for details.
                    </p>
                </div>

                <footer class="py-12 flex items-center justify-between gap-6 border-t border-zinc-800/50 mt-12">
                    <div class="w-1/2">
                        <Link href="/documentation/reference/config" className="group block p-5 rounded-xl border border-zinc-800/60 bg-zinc-950/20 hover:border-zinc-700 hover:bg-zinc-900/20 transition-all">
                            <span class="block text-xs font-medium text-zinc-500 tracking-wide uppercase mb-1">Previous</span>
                            <span class="text-base font-bold text-white group-hover:text-blue-400 flex items-center gap-1 transition-colors">
                                <svg class="w-4 h-4 text-zinc-500 group-hover:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
                                Configuration
                            </span>
                        </Link>
                    </div>
                    <div class="w-1/2 text-right">
                        <Link href="/documentation/reference/hooks" className="group block p-5 rounded-xl border border-zinc-800/60 bg-zinc-950/20 hover:border-zinc-700 hover:bg-zinc-900/20 transition-all">
                            <span class="block text-xs font-medium text-zinc-500 tracking-wide uppercase mb-1">Next</span>
                            <span class="text-base font-bold text-white group-hover:text-blue-400 flex items-center justify-end gap-1 transition-colors">
                                Hooks API
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
                        <li><a href="#builtins" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Built-in components</a></li>
                        <li><a href="#custom-components" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Custom components</a></li>
                        <li><a href="#hooks" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Hooks</a></li>
                    </ul>
                </div>
            </aside>
        </div>
    )


def getServerSideProps(context):
    return {"props": {"title": "Components API - NextPy Docs"}}


default = ComponentsAPI

