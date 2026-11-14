"""Utilities API - NextPy Documentation"""

from nextpy.psx import component, Link, register_component
from pages.documentation._components.enhanced_codeblock import EnhancedCodeBlock

register_component("EnhancedCodeBlock", EnhancedCodeBlock)


@component
def UtilitiesAPI():
    db_example = """from nextpy.db import get_session, paginate, apply_filters
from nextpy.db import User, Post, Todo, Job, Application


def getServerSideProps(context):
    db = get_session()
    query = db.query(Post).filter(Post.published == True)
    page = paginate(query, page=1, per_page=10)
    return {"props": {"posts": page["items"], "total": page["total"]}}"""

    cache_example = """from nextpy.cache import cached, invalidate

@cached(ttl=60, key="dashboard_stats")
def expensive_query():
    db = get_session()
    return {"users": db.query(User).count()}

# Later, after a write:
invalidate("dashboard_stats")"""

    actions_example = """from nextpy.server_actions import ServerAction, FormValidator

login_action = ServerAction("login")

@login_action.validator(FormValidator)
def validate(payload):
    if not payload.get("email"):
        raise ValueError("Email is required")
    return payload"""

    return (
        <div class="flex flex-col xl:flex-row items-start justify-between gap-2 w-full max-w-6xl mx-auto">
            <article class="flex-1 min-w-0 max-w-4xl antialiased text-zinc-300 selection:bg-blue-500/20 selection:text-blue-300 space-y-12 pb-24 pt-6">
                <div class="flex items-center justify-between border-b border-zinc-800/50 pb-4">
                    <div class="flex items-center gap-2 text-sm font-medium text-zinc-400">
                        <span>Documentation</span>
                        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                        <span>Reference API</span>
                        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                        <span class="text-white">Utilities</span>
                    </div>
                </div>

                <header id="header" class="mb-12">
                    <h1 class="text-2xl sm:text-2xl font-bold tracking-tight text-white mb-6">Utilities</h1>
                    <p class="leading-relaxed text-zinc-300">
                        Server-side helpers shipped with NextPy: the database session layer, caching, server actions, and security utilities.
                    </p>
                </header>

                <div id="database" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Database (nextpy.db)</h2>
                    <p class="text-base leading-7 text-zinc-300">
                        SQLAlchemy-backed session management with pagination, filtering, and helper queries. Built-in models include <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">User</code>, <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">Post</code>, <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">Todo</code>, <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">Job</code>, and <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">Application</code>.
                    </p>
                    <EnhancedCodeBlock lang="python" filename="pages/index.py" snippet={db_example} />
                    <ul class="list-disc pl-6 space-y-2 text-base leading-7 text-zinc-300">
                        <li><code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">get_session()</code> / <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">session()</code> &mdash; scoped DB session.</li>
                        <li><code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">paginate(query, page, per_page)</code> &mdash; returns <code class="font-mono text-xs">&#123;items, total, page, pages, has_next, has_prev&#125;</code>.</li>
                        <li><code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">apply_filters(query, model, filters, allowed, search, search_fields)</code> &mdash; safe dynamic filtering.</li>
                        <li><code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">get_or_none</code> / <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">get_or_404</code> &mdash; fetch by id with optional 404.</li>
                        <li><code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">transaction()</code> &mdash; context manager for atomic writes.</li>
                    </ul>
                </div>

                <div id="cache" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Caching (nextpy.cache)</h2>
                    <p class="text-base leading-7 text-zinc-300">An in-process TTL cache with decorator and manual invalidation:</p>
                    <EnhancedCodeBlock lang="python" filename="pages/dashboard.py" snippet={cache_example} />
                </div>

                <div id="server-actions" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Server actions (nextpy.server_actions)</h2>
                    <p class="text-base leading-7 text-zinc-300">
                        Named actions invoked from the client via <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">callServerAction</code>. Actions can declare validators and return JSON-safe payloads.
                    </p>
                    <EnhancedCodeBlock lang="python" filename="pages/actions/auth_actions.py" snippet={actions_example} />
                </div>

                <div id="security" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Security & auth helpers</h2>
                    <ul class="list-disc pl-6 space-y-2 text-base leading-7 text-zinc-300">
                        <li><code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">nextpy.security</code> &mdash; password hashing, token helpers, and request guards.</li>
                        <li><code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">nextpy.auth</code> &mdash; session cookies, current-user resolution, and OAuth helpers.</li>
                    </ul>
                </div>

                <footer class="py-12 flex items-center justify-between gap-6 border-t border-zinc-800/50 mt-12">
                    <div class="w-1/2">
                        <Link href="/documentation/reference/typescript" className="group block p-5 rounded-xl border border-zinc-800/60 bg-zinc-950/20 hover:border-zinc-700 hover:bg-zinc-900/20 transition-all">
                            <span class="block text-xs font-medium text-zinc-500 tracking-wide uppercase mb-1">Previous</span>
                            <span class="text-base font-bold text-white group-hover:text-blue-400 flex items-center gap-1 transition-colors">
                                <svg class="w-4 h-4 text-zinc-500 group-hover:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
                                TypeScript
                            </span>
                        </Link>
                    </div>
                    <div class="w-1/2 text-right">
                        <Link href="/documentation" className="group block p-5 rounded-xl border border-zinc-800/60 bg-zinc-950/20 hover:border-zinc-700 hover:bg-zinc-900/20 transition-all">
                            <span class="block text-xs font-medium text-zinc-500 tracking-wide uppercase mb-1">Next</span>
                            <span class="text-base font-bold text-white group-hover:text-blue-400 flex items-center justify-end gap-1 transition-colors">
                                Documentation Home
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
                        <li><a href="#database" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Database</a></li>
                        <li><a href="#cache" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Caching</a></li>
                        <li><a href="#server-actions" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Server actions</a></li>
                        <li><a href="#security" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Security & auth</a></li>
                    </ul>
                </div>
            </aside>
        </div>
    )


def getServerSideProps(context):
    return {"props": {"title": "Utilities - NextPy Docs"}}


default = UtilitiesAPI

