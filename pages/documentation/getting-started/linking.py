"""Linking and Navigation - NextPy Documentation"""

from nextpy.psx import component, Link, register_component
from pages.documentation.components.enhanced_codeblock import EnhancedCodeBlock

register_component("EnhancedCodeBlock", EnhancedCodeBlock)

@component
def LinkingGuide():
    return (
        <div class="flex flex-col xl:flex-row items-start justify-between gap-12 w-full max-w-6xl mx-auto">
            <article class="flex-1 min-w-0 max-w-4xl antialiased text-zinc-300 selection:bg-blue-500/20 selection:text-blue-300 space-y-16 pb-24 pt-6">
                <div class="flex items-center justify-between border-b border-zinc-800/50 pb-6">
                    <div class="flex items-center gap-2 text-sm font-medium text-zinc-400">
                        <span>Documentation</span>
                        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                        <span>Getting Started</span>
                        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                        <span class="text-white">Linking and Navigation</span>
                    </div>
                </div>

                <header id="header" class="mb-12">
                    <h1 class="text-4xl sm:text-5xl font-bold tracking-tight text-white mb-6">
                        Linking and Navigation
                    </h1>
                    <p class="text-lg leading-relaxed text-zinc-400">
                        Learn how to navigate between pages in your NextPy application using the Link component and programmatic navigation.
                    </p>
                </header>

                <div id="overview" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Overview</h2>
                    <p class="text-base leading-7 text-zinc-400">
                        NextPy provides a powerful navigation system that allows you to move between pages seamlessly. The framework uses a file-based routing system where each file in the <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">pages/</code> directory becomes a route.
                    </p>
                </div>

                <div id="link-component" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">The Link Component</h2>
                    <p class="text-base leading-7 text-zinc-400">
                        The <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">Link</code> component is the primary way to navigate between pages in NextPy. It extends the HTML <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">&lt;a&gt;</code> tag with optimized client-side navigation.
                    </p>
                    
                    <EnhancedCodeBlock 
                        language="python"
                        code='from nextpy.psx import component, Link

@component
def Navigation():
    return (
        <nav class="flex gap-4">
            <Link href="/" class="text-white hover:text-blue-400">Home</Link>
            <Link href="/about" class="text-white hover:text-blue-400">About</Link>
            <Link href="/contact" class="text-white hover:text-blue-400">Contact</Link>
        </nav>
    )
                    />
                </div>

                <div id="dynamic-links" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Dynamic Links</h2>
                    <p class="text-base leading-7 text-zinc-400">
                        You can create dynamic links by using variables in your href:
                    </p>
                    
                    <EnhancedCodeBlock 
                        language="python"
                        code='from nextpy.psx import component, Link

@component
def UserList(users):
    return (
        <div class="space-y-2">
            {users.map((user) => (
                <Link href={f"/users/{user.id}"} class="block p-2 hover:bg-zinc-800 rounded">
                    {user.name}
                </Link>
            ))}
        </div>
    )
                    />
                </div>

                <div id="programmatic-navigation" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Programmatic Navigation</h2>
                    <p class="text-base leading-7 text-zinc-400">
                        For navigation triggered by events (like form submissions), you can use the router programmatically:
                    </p>
                    
                    <EnhancedCodeBlock 
                        language="python"
                        code='from nextpy.psx import component
from nextpy.core.router import useRouter

@component
def LoginForm():
    router = useRouter()
    
    def handle_login(event):
        # Perform login logic
        router.push("/dashboard")
    
    return (
        <form on_submit={handle_login}>
            <button type="submit">Login</button>
        </form>
    )
                    />
                </div>

                <div id="active-links" class="space-y-6 pt-8 border-t border-zinc-800/50">
                    <h2 class="text-2xl font-semibold text-white tracking-tight">Active Link States</h2>
                    <p class="text-base leading-7 text-zinc-400">
                        You can highlight the active link using the <code class="text-zinc-200 font-mono text-sm px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">usePathname</code> hook:
                    </p>
                    
                    <EnhancedCodeBlock 
                        language="python"
                        code='from nextpy.psx import component, Link
from nextpy.core.router import usePathname

@component
def Navigation():
    pathname = usePathname()
    
    links = [
        {href: "/", label: "Home"},
        {href: "/about", label: "About"},
        {href: "/contact", label: "Contact"}
    ]
    
    return (
        <nav class="flex gap-4">
            {links.map((link) => (
                <Link 
                    href={link.href}
                    class={
                        f"text-white hover:text-blue-400 {pathname == link.href and 'font-bold text-blue-400'}"
                    }
                >
                    {link.label}
                </Link>
            ))}
        </nav>
    )
                    />
                </div>

                <footer class="py-12 flex items-center justify-between gap-6 border-t border-zinc-800/50 mt-12">
                    <div class="w-1/2">
                        <Link href="/documentation/getting-started/layouts-pages" className="group block p-5 rounded-xl border border-zinc-800/60 bg-zinc-950/20 hover:border-zinc-700 hover:bg-zinc-900/20 transition-all">
                            <span class="block text-xs font-medium text-zinc-500 tracking-wide uppercase mb-1">Previous</span>
                            <span class="text-base font-bold text-white group-hover:text-blue-400 flex items-center gap-1 transition-colors">
                                <svg class="w-4 h-4 text-zinc-500 group-hover:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
                                Layouts and Pages
                            </span>
                        </Link>
                    </div>
                    <div class="w-1/2 text-right">
                        <Link href="/documentation/getting-started/fetching-data" className="group block p-5 rounded-xl border border-zinc-800/60 bg-zinc-950/20 hover:border-zinc-700 hover:bg-zinc-900/20 transition-all">
                            <span class="block text-xs font-medium text-zinc-500 tracking-wide uppercase mb-1">Next</span>
                            <span class="text-base font-bold text-white group-hover:text-blue-400 flex items-center justify-end gap-1 transition-colors">
                                Fetching Data
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
                        <li><a href="#link-component" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Link Component</a></li>
                        <li><a href="#dynamic-links" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Dynamic Links</a></li>
                        <li><a href="#programmatic-navigation" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Programmatic Navigation</a></li>
                        <li><a href="#active-links" class="block pl-4 -ml-px border-l border-transparent hover:text-white hover:border-zinc-500 transition-colors">Active Link States</a></li>
                    </ul>
                </div>
            </aside>
        </div>
    )

def getServerSideProps(context):
    return {"props": {"title": "Linking and Navigation - NextPy Docs"}}

default = LinkingGuide
