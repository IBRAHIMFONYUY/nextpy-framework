"""Fetching Data - NextPy Documentation"""

from nextpy.psx import component, Link, register_component
from pages.documentation.components.enhanced_codeblock import EnhancedCodeBlock

register_component("EnhancedCodeBlock", EnhancedCodeBlock)

@component
def FetchingDataGuide():
    return (
        <div class="flex flex-col xl:flex-row items-start justify-between gap-12 w-full max-w-6xl mx-auto">
            <article class="flex-1 min-w-0 max-w-4xl antialiased text-zinc-300 selection:bg-blue-500/20 selection:text-blue-300 space-y-16 pb-24 pt-6">
                <div class="flex items-center justify-between border-b border-zinc-800/50 pb-6">
                    <div class="flex items-center gap-2 text-sm font-medium text-zinc-400">
                        <span>Documentation</span>
                        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                        <span>Getting Started</span>
                        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                        <span class="text-white">Fetching Data</span>
                    </div>
                </div>

                <header id="header" class="mb-12">
                    <h1 class="text-4xl sm:text-5xl font-bold tracking-tight text-white mb-6">
                        Fetching Data
                    </h1>
                    <p class="text-lg leading-relaxed text-zinc-400">
                        Learn how to fetch data in NextPy using server-side rendering, client-side fetching, and server actions.
                    </p>
                </header>

                <div id="overview" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Overview</h2>
                    <p class="text-base leading-7 text-zinc-400">
                        NextPy provides multiple ways to fetch data depending on your use case. You can fetch data on the server for SEO and performance, or on the client for interactivity.
                    </p>
                </div>

                <div id="server-side-fetching" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Server-Side Fetching</h2>
                    <p class="text-base leading-7 text-zinc-400">
                        Use <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">getServerSideProps</code> to fetch data on the server before rendering the page:
                    </p>
                    
                    <EnhancedCodeBlock 
                        language="python"
                        code='import httpx
from nextpy.psx import component

@component
def UserProfile(props):
    user = props.get("user", {})
    return (
        <div class="p-6">
            <h1 class="text-2xl font-bold">{user.get("name")}</h1>
            <p class="text-zinc-400">{user.get("email")}</p>
        </div>
    )

def getServerSideProps(context):
    response = httpx.get("https://api.example.com/user/1")
    return {"props": {"user": response.json()}}'
                    />
                </div>

                <div id="client-side-fetching" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Client-Side Fetching</h2>
                    <p class="text-base leading-7 text-zinc-400">
                        For interactive data, fetch on the client using hooks:
                    </p>
                    
                    <EnhancedCodeBlock 
                        language="python"
                        code='from nextpy.psx import interactive_component, useState

@interactive_component
def UserSearch():
    [query, setQuery] = useState("")
    [results, setResults] = useState([])
    [loading, setLoading] = useState(False)
    
    def handle_search(e):
        setQuery(e.target.value)
        # Add fetch logic here
    
    return (
        <div class="p-6">
            <input value={query} oninput={handle_search} placeholder="Search users..." />
            {if loading:
                <p class="text-zinc-400">Loading...</p>
            }
        </div>
    )
                    />
                </div>

                <footer class="py-12 flex items-center justify-between gap-6 border-t border-zinc-800/50 mt-12">
                    <div class="w-1/2">
                        <Link href="/documentation/getting-started/linking" className="group block p-5 rounded-xl border border-zinc-800/60 bg-zinc-950/20 hover:border-zinc-700 hover:bg-zinc-900/20 transition-all">
                            <span class="block text-xs font-medium text-zinc-500 tracking-wide uppercase mb-1">Previous</span>
                            <span class="text-base font-bold text-white group-hover:text-blue-400 flex items-center gap-1 transition-colors">
                                <svg class="w-4 h-4 text-zinc-500 group-hover:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
                                Linking and Navigation
                            </span>
                        </Link>
                    </div>
                    <div class="w-1/2 text-right">
                        <Link href="/documentation/getting-started/caching" className="group block p-5 rounded-xl border border-zinc-800/60 bg-zinc-950/20 hover:border-zinc-700 hover:bg-zinc-900/20 transition-all">
                            <span class="block text-xs font-medium text-zinc-500 tracking-wide uppercase mb-1">Next</span>
                            <span class="text-base font-bold text-white group-hover:text-blue-400 flex items-center justify-end gap-1 transition-colors">
                                Caching & Revalidation
                                <svg class="w-4 h-4 text-zinc-500 group-hover:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                            </span>
                        </Link>
                    </div>
                </footer>
            </article>

            <aside class="hidden xl:block w-64 shrink-0 sticky top-24 pt-6 pb-24 h-[calc(100vh-6rem)] overflow-y-auto">
                <div class="text-sm">
                    <h4 class="font-semibold text-white mb-4 tracking-wide">On this page</h4>
                    <ul class="space-y-3 font-medium text-zinc-400 border-l border-zinc-800/50">
                        <li><a href="#overview" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Overview</a></li>
                        <li><a href="#server-side-fetching" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Server-Side Fetching</a></li>
                        <li><a href="#client-side-fetching" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Client-Side Fetching</a></li>
                    </ul>
                </div>
            </aside>
        </div>
    )

def getServerSideProps(context):
    return {"props": {"title": "Fetching Data - NextPy Docs"}}

default = FetchingDataGuide
