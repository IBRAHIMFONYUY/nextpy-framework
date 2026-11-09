"""Routing Engine - NextPy Documentation"""

from nextpy.psx import component, Link, register_component
from pages.documentation.components.enhanced_codeblock import EnhancedCodeBlock

register_component("EnhancedCodeBlock", EnhancedCodeBlock)

@component
def RoutingEngine():
    return (
        <div class="flex flex-col xl:flex-row items-start justify-between gap-12 w-full max-w-6xl mx-auto">
            <article class="flex-1 min-w-0 max-w-4xl antialiased text-zinc-300 selection:bg-blue-500/20 selection:text-blue-300 space-y-16 pb-24 pt-6">
                <div class="flex items-center justify-between border-b border-zinc-800/50 pb-6">
                    <div class="flex items-center gap-2 text-sm font-medium text-zinc-400">
                        <span>Documentation</span>
                        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                        <span>Core Concepts</span>
                        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                        <span class="text-white">Routing Engine</span>
                    </div>
                </div>

                <header id="header" class="mb-12">
                    <h1 class="text-4xl sm:text-5xl font-bold tracking-tight text-white mb-6">
                        Routing Engine
                    </h1>
                    <p class="text-lg leading-relaxed text-zinc-400">
                        Learn about NextPy's file-based routing system.
                    </p>
                </header>

                <div id="overview" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Overview</h2>
                    <p class="text-base leading-7 text-zinc-400">
                        NextPy uses a file-based routing system where files in the pages/ directory automatically become routes.
                    </p>
                </div>

                <div id="file-based-routing" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">File-Based Routing</h2>
                    <p class="text-base leading-7 text-zinc-400">
                        Create routes by adding files to the pages directory:
                    </p>
                    
                    <EnhancedCodeBlock 
                        language="bash"
                        code='pages/
  index.py          -> /
  about.py          -> /about
  blog/
    index.py        -> /blog
    [slug].py       -> /blog/[slug]'
                    />
                </div>

                <footer class="py-12 flex items-center justify-between gap-6 border-t border-zinc-800/50 mt-12">
                    <div class="w-1/2">
                        <Link href="/documentation/concepts/psx-internals" className="group block p-5 rounded-xl border border-zinc-800/60 bg-zinc-950/20 hover:border-zinc-700 hover:bg-zinc-900/20 transition-all">
                            <span class="block text-xs font-medium text-zinc-500 tracking-wide uppercase mb-1">Previous</span>
                            <span class="text-base font-bold text-white group-hover:text-blue-400 flex items-center gap-1 transition-colors">
                                <svg class="w-4 h-4 text-zinc-500 group-hover:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
                                PSX Core Internals
                            </span>
                        </Link>
                    </div>
                    <div class="w-1/2 text-right">
                        <Link href="/documentation/concepts/rendering" className="group block p-5 rounded-xl border border-zinc-800/60 bg-zinc-950/20 hover:border-zinc-700 hover:bg-zinc-900/20 transition-all">
                            <span class="block text-xs font-medium text-zinc-500 tracking-wide uppercase mb-1">Next</span>
                            <span class="text-base font-bold text-white group-hover:text-blue-400 flex items-center justify-end gap-1 transition-colors">
                                Rendering (SSR, SSG, ISR)
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
                        <li><a href="#file-based-routing" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">File-Based Routing</a></li>
                    </ul>
                </div>
            </aside>
        </div>
    )

def getServerSideProps(context):
    return {"props": {"title": "Routing Engine - NextPy Docs"}}

default = RoutingEngine
