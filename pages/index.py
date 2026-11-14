from nextpy.psx import component, Link


@component
def Home(props=None):
    props = props or {}
    title = props.get("title", "NextPy - The Python Framework")

    description = props.get(
        "description",
        "NextPy is a modern Python web framework that combines server-side rendering, "
        "a reactive Python UI engine, and server actions into a single framework."
    )

    counter_code = (
        "from nextpy.psx import component, useState\n\n"
        "@component\n"
        "def Counter():\n"
        "    [count, set_count] = useState(0)\n\n"
        "    def increment():\n"
        "        set_count(count + 1)\n\n"
        "    return (...)\n"
        "# UI updates instantly — no reload, no JS"
    )

    return (
        <div class="font-sans antialiased">

            {/* Hero */}
            <section class="relative overflow-hidden bg-white">
                <div class="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_4px)] [background-size:16px_16px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
                <div class="relative px-4 mx-auto max-w-7xl pt-20 pb-16 sm:pt-28 sm:pb-20 lg:px-8">
                    <div class="max-w-4xl mx-auto text-center">
                        <Link href="/documentation/concepts/psx-internals" className="inline-flex items-center gap-2 px-4 py-1.5 mb-8 text-xs font-semibold tracking-wide text-blue-700 uppercase transition-colors bg-blue-50 border border-blue-100 rounded-full hover:bg-blue-100">
                            <span class="w-1.5 h-1.5 bg-blue-600 rounded-full"></span>
                            New: PSX reactive engine
                        </Link>
                        <h1 class="text-5xl font-extrabold tracking-tight text-gray-950 sm:text-7xl">
                            The Python framework<br />
                            <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">for the modern web</span>
                        </h1>
                        <p class="max-w-2xl mx-auto mt-6 text-lg leading-8 text-gray-600 sm:text-xl">
                            {description} Write pages, components, API routes and server logic in Python — no JavaScript build step required.
                        </p>
                        <div class="flex flex-col items-center justify-center mt-10 gap-y-4 sm:flex-row sm:gap-x-6">
                            <Link href="/documentation" className="w-full px-8 py-4 text-sm font-bold text-white transition-all bg-gray-950 rounded-full shadow-xl sm:w-auto hover:bg-gray-800">
                                Get Started →
                            </Link>
                            <Link href="/templates" className="w-full px-8 py-4 text-sm font-bold text-gray-900 transition-all bg-white border border-gray-300 rounded-full sm:w-auto hover:bg-gray-50">
                                Explore Templates
                            </Link>
                        </div>
                    </div>

                    {/* Terminal card */}
                    <div class="max-w-2xl mx-auto mt-16">
                        <div class="overflow-hidden text-left bg-gray-950 border border-gray-800 shadow-2xl rounded-2xl">
                            <div class="flex items-center gap-2 px-5 py-3.5 border-b border-gray-800">
                                <span class="w-3 h-3 bg-red-500 rounded-full"></span>
                                <span class="w-3 h-3 bg-yellow-500 rounded-full"></span>
                                <span class="w-3 h-3 bg-green-500 rounded-full"></span>
                                <span class="ml-3 text-xs font-mono text-gray-500">terminal</span>
                            </div>
                            <div class="p-6 space-y-3 font-mono text-sm">
                                <p><span class="text-green-400">$</span> <span class="text-gray-200">pip install nextpy</span></p>
                                <p><span class="text-green-400">$</span> <span class="text-gray-200">nextpy create my-app</span></p>
                                <p><span class="text-green-400">$</span> <span class="text-gray-200">cd my-app && nextpy dev</span></p>
                                <p class="pt-2 text-gray-500">→ Server running at <span class="text-blue-400">http://localhost:8000</span></p>
                            </div>
                        </div>
                        <p class="mt-4 text-sm text-gray-500">From zero to a running full-stack app in under a minute.</p>
                    </div>
                </div>
            </section>

            {/* Features */}
            <section class="py-24 bg-gray-50/60 border-y border-gray-100">
                <div class="px-6 mx-auto max-w-7xl lg:px-8">
                    <div class="max-w-2xl mx-auto lg:text-center">
                        <p class="text-sm font-semibold tracking-wider text-blue-600 uppercase">Everything included</p>
                        <h2 class="mt-3 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">One framework, every layer</h2>
                        <p class="mt-4 text-lg text-gray-600">NextPy covers rendering, reactivity, data and deployment — so you can focus on product, not plumbing.</p>
                    </div>

                    <div class="grid max-w-5xl grid-cols-1 gap-6 mx-auto mt-16 sm:grid-cols-2 lg:grid-cols-3">
                        <Link href="/documentation/concepts/rendering" className="block p-8 transition-all bg-white border border-gray-200 rounded-2xl hover:shadow-lg hover:-translate-y-1">
                            <div class="flex items-center justify-center w-12 h-12 text-white rounded-xl shadow-lg bg-gradient-to-br from-blue-600 to-indigo-600">
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
                                </svg>
                            </div>
                            <h3 class="mt-6 text-lg font-bold text-gray-900">SSR, SSG & ISR</h3>
                            <p class="mt-2 text-sm leading-6 text-gray-600">Server rendering, static generation and incremental revalidation — pick per page with getServerSideProps, getStaticProps and getStaticPaths.</p>
                            <span class="inline-block mt-4 text-sm font-semibold text-blue-600">Rendering guide →</span>
                        </Link>

                        <Link href="/documentation/concepts/psx-internals" className="block p-8 transition-all bg-white border border-gray-200 rounded-2xl hover:shadow-lg hover:-translate-y-1">
                            <div class="flex items-center justify-center w-12 h-12 text-white rounded-xl shadow-lg bg-gradient-to-br from-indigo-600 to-violet-600">
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 22.5 12 13.5H3.75z" />
                                </svg>
                            </div>
                            <h3 class="mt-6 text-lg font-bold text-gray-900">PSX Reactive UI</h3>
                            <p class="mt-2 text-sm leading-6 text-gray-600">useState, useEffect and useRef with fine-grained DOM updates, FLIP animations and AnimatePresence exits — all from Python.</p>
                            <span class="inline-block mt-4 text-sm font-semibold text-blue-600">PSX internals →</span>
                        </Link>

                        <Link href="/documentation/reference/server-actions" className="block p-8 transition-all bg-white border border-gray-200 rounded-2xl hover:shadow-lg hover:-translate-y-1">
                            <div class="flex items-center justify-center w-12 h-12 text-white rounded-xl shadow-lg bg-gradient-to-br from-violet-600 to-purple-600">
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />
                                </svg>
                            </div>
                            <h3 class="mt-6 text-lg font-bold text-gray-900">Server Actions</h3>
                            <p class="mt-2 text-sm leading-6 text-gray-600">callServerAction invokes Python functions securely from the client with built-in loading, result and error state — no API boilerplate.</p>
                            <span class="inline-block mt-4 text-sm font-semibold text-blue-600">Server actions →</span>
                        </Link>

                        <Link href="/documentation/getting-started/layouts-pages" className="block p-8 transition-all bg-white border border-gray-200 rounded-2xl hover:shadow-lg hover:-translate-y-1">
                            <div class="flex items-center justify-center w-12 h-12 text-white rounded-xl shadow-lg bg-gradient-to-br from-sky-600 to-blue-600">
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
                                </svg>
                            </div>
                            <h3 class="mt-6 text-lg font-bold text-gray-900">File-Based Routing</h3>
                            <p class="mt-2 text-sm leading-6 text-gray-600">Drop a file in pages/ and it becomes a route. Dynamic segments like [slug] and nested layouts included.</p>
                            <span class="inline-block mt-4 text-sm font-semibold text-blue-600">Layouts & pages →</span>
                        </Link>

                        <Link href="/documentation/howto/database" className="block p-8 transition-all bg-white border border-gray-200 rounded-2xl hover:shadow-lg hover:-translate-y-1">
                            <div class="flex items-center justify-center w-12 h-12 text-white rounded-xl shadow-lg bg-gradient-to-br from-emerald-600 to-teal-600">
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                                </svg>
                            </div>
                            <h3 class="mt-6 text-lg font-bold text-gray-900">ORM, Auth & Guards</h3>
                            <p class="mt-2 text-sm leading-6 text-gray-600">SQLAlchemy models, cookie sessions, login and registration actions, and protected routes — authentication included.</p>
                            <span class="inline-block mt-4 text-sm font-semibold text-blue-600">Database guide →</span>
                        </Link>

                        <Link href="/documentation/howto/api" className="block p-8 transition-all bg-white border border-gray-200 rounded-2xl hover:shadow-lg hover:-translate-y-1">
                            <div class="flex items-center justify-center w-12 h-12 text-white rounded-xl shadow-lg bg-gradient-to-br from-amber-500 to-orange-600">
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
                                </svg>
                            </div>
                            <h3 class="mt-6 text-lg font-bold text-gray-900">API Routes & Streaming</h3>
                            <p class="mt-2 text-sm leading-6 text-gray-600">REST endpoints under pages/api plus streaming responses for AI and real-time features — all typed Python.</p>
                            <span class="inline-block mt-4 text-sm font-semibold text-blue-600">API guide →</span>
                        </Link>
                    </div>
                </div>
            </section>

            {/* Code split */}
            <section class="py-24 bg-white">
                <div class="grid items-center max-w-7xl grid-cols-1 gap-16 px-6 mx-auto lg:grid-cols-2 lg:px-8">
                    <div>
                        <p class="text-sm font-semibold tracking-wider text-blue-600 uppercase">How it works</p>
                        <h2 class="mt-3 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">Python in. Web out.</h2>
                        <p class="mt-6 text-lg leading-8 text-gray-600">
                            NextPy compiles your Python components into a reactive client runtime and serves them with a production-grade FastAPI backend. You write one language — the framework handles the rest.
                        </p>
                        <ul class="mt-8 space-y-4">
                            <li class="flex items-start gap-3">
                                <div class="flex items-center justify-center flex-shrink-0 w-6 h-6 mt-0.5 text-white rounded-full bg-blue-600">
                                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                                </div>
                                <span class="text-gray-700">Write pages and components in Python with PSX markup</span>
                            </li>
                            <li class="flex items-start gap-3">
                                <div class="flex items-center justify-center flex-shrink-0 w-6 h-6 mt-0.5 text-white rounded-full bg-blue-600">
                                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                                </div>
                                <span class="text-gray-700">Fetch data with getServerSideProps, getStaticProps and getStaticPaths</span>
                            </li>
                            <li class="flex items-start gap-3">
                                <div class="flex items-center justify-center flex-shrink-0 w-6 h-6 mt-0.5 text-white rounded-full bg-blue-600">
                                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                                </div>
                                <span class="text-gray-700">Ship with nextpy build — SSR, static export and API routes included</span>
                            </li>
                        </ul>
                        <Link href="/documentation/tutorials/first-app" className="inline-flex items-center mt-8 text-sm font-bold text-blue-600 transition-colors hover:text-blue-700">
                            Follow the first-app tutorial →
                        </Link>
                    </div>

                    <div class="overflow-hidden bg-gray-950 border border-gray-800 shadow-2xl rounded-2xl">
                        <div class="flex items-center gap-2 px-5 py-3.5 border-b border-gray-800">
                            <span class="w-3 h-3 bg-red-500 rounded-full"></span>
                            <span class="w-3 h-3 bg-yellow-500 rounded-full"></span>
                            <span class="w-3 h-3 bg-green-500 rounded-full"></span>
                            <span class="ml-3 text-xs font-mono text-gray-500">pages/counter.py</span>
                        </div>
                        <pre class="p-6 overflow-x-auto text-sm font-mono leading-7 text-gray-200"><code>{counter_code}</code></pre>
                    </div>
                </div>
            </section>

            {/* Tech strip */}
            <section class="py-16 bg-gray-50 border-y border-gray-100">
                <div class="px-6 mx-auto max-w-7xl lg:px-8">
                    <p class="mb-8 text-sm font-semibold tracking-wider text-center text-gray-500 uppercase">Powered by proven technology</p>
                    <div class="flex flex-wrap items-center justify-center gap-4">
                        <span class="px-5 py-2.5 text-sm font-semibold text-gray-800 bg-white border border-gray-200 rounded-full shadow-sm">FastAPI</span>
                        <span class="px-5 py-2.5 text-sm font-semibold text-gray-800 bg-white border border-gray-200 rounded-full shadow-sm">Uvicorn</span>
                        <span class="px-5 py-2.5 text-sm font-semibold text-gray-800 bg-white border border-gray-200 rounded-full shadow-sm">Tailwind CSS</span>
                        <span class="px-5 py-2.5 text-sm font-semibold text-gray-800 bg-white border border-gray-200 rounded-full shadow-sm">SQLAlchemy</span>
                        <span class="px-5 py-2.5 text-sm font-semibold text-gray-800 bg-white border border-gray-200 rounded-full shadow-sm">PSX Runtime</span>
                        <span class="px-5 py-2.5 text-sm font-semibold text-gray-800 bg-white border border-gray-200 rounded-full shadow-sm">Python 3.10+</span>
                    </div>
                </div>
            </section>

            {/* Stats */}
            <section class="py-20 bg-white">
                <div class="max-w-6xl px-4 mx-auto sm:px-6 lg:px-8">
                    <div class="grid gap-12 text-center md:grid-cols-4">
                        <div>
                            <div class="mb-2 text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">3</div>
                            <p class="font-semibold text-gray-600">Rendering modes — SSR, SSG, ISR</p>
                        </div>
                        <div>
                            <div class="mb-2 text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">6</div>
                            <p class="font-semibold text-gray-600">PSX hooks — state, effects, refs</p>
                        </div>
                        <div>
                            <div class="mb-2 text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-purple-600">50+</div>
                            <p class="font-semibold text-gray-600">Documentation pages & guides</p>
                        </div>
                        <div>
                            <div class="mb-2 text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-600">0</div>
                            <p class="font-semibold text-gray-600">Lines of JavaScript required</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Explore */}
            <section class="py-24 bg-gray-50">
                <div class="max-w-6xl px-4 mx-auto sm:px-6 lg:px-8">
                    <div class="max-w-2xl mx-auto mb-16 text-center">
                        <h2 class="text-4xl font-bold tracking-tight text-gray-900">Explore NextPy</h2>
                        <p class="mt-4 text-lg text-gray-600">Everything you need to go from install to production.</p>
                    </div>

                    <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                        <Link href="/documentation" className="block p-8 transition-all bg-white border border-gray-200 rounded-2xl hover:shadow-lg hover:-translate-y-1">
                            <div class="flex items-center justify-center w-12 h-12 text-white rounded-xl shadow-lg bg-gradient-to-br from-blue-600 to-indigo-600">
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18c-2.305 0-4.408.867-6 2.292m0-14.25v14.25" /></svg>
                            </div>
                            <h3 class="mt-5 text-lg font-bold text-gray-900">Documentation</h3>
                            <p class="mt-1 text-sm text-gray-600">Tutorials, guides and full API reference</p>
                        </Link>

                        <Link href="/features" className="block p-8 transition-all bg-white border border-gray-200 rounded-2xl hover:shadow-lg hover:-translate-y-1">
                            <div class="flex items-center justify-center w-12 h-12 text-white rounded-xl shadow-lg bg-gradient-to-br from-indigo-600 to-violet-600">
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" /></svg>
                            </div>
                            <h3 class="mt-5 text-lg font-bold text-gray-900">Features</h3>
                            <p class="mt-1 text-sm text-gray-600">Every capability the framework ships with</p>
                        </Link>

                        <Link href="/examples" className="block p-8 transition-all bg-white border border-gray-200 rounded-2xl hover:shadow-lg hover:-translate-y-1">
                            <div class="flex items-center justify-center w-12 h-12 text-white rounded-xl shadow-lg bg-gradient-to-br from-violet-600 to-purple-600">
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" /></svg>
                            </div>
                            <h3 class="mt-5 text-lg font-bold text-gray-900">PSX Examples</h3>
                            <p class="mt-1 text-sm text-gray-600">Interactive demos of state, effects and animations</p>
                        </Link>

                        <Link href="/components-showcase" className="block p-8 transition-all bg-white border border-gray-200 rounded-2xl hover:shadow-lg hover:-translate-y-1">
                            <div class="flex items-center justify-center w-12 h-12 text-white rounded-xl shadow-lg bg-gradient-to-br from-sky-600 to-blue-600">
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 4.5h6v6h-6v-6zm9 0h6v6h-6v-6zm-9 9h6v6h-6v-6zm9 0h6v6h-6v-6z" /></svg>
                            </div>
                            <h3 class="mt-5 text-lg font-bold text-gray-900">Components</h3>
                            <p class="mt-1 text-sm text-gray-600">UI component showcase and patterns</p>
                        </Link>

                        <Link href="/templates" className="block p-8 transition-all bg-white border border-gray-200 rounded-2xl hover:shadow-lg hover:-translate-y-1">
                            <div class="flex items-center justify-center w-12 h-12 text-white rounded-xl shadow-lg bg-gradient-to-br from-emerald-600 to-teal-600">
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" /></svg>
                            </div>
                            <h3 class="mt-5 text-lg font-bold text-gray-900">Templates</h3>
                            <p class="mt-1 text-sm text-gray-600">Starter patterns for SaaS, blogs, dashboards and AI apps</p>
                        </Link>

                        <Link href="/jobs" className="block p-8 transition-all bg-white border border-gray-200 rounded-2xl hover:shadow-lg hover:-translate-y-1">
                            <div class="flex items-center justify-center w-12 h-12 text-white rounded-xl shadow-lg bg-gradient-to-br from-amber-500 to-orange-600">
                                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M20.25 14.15v4.25c0 1.094-.787 2.036-1.872 2.18-2.087.277-4.216.42-6.378.42s-4.291-.143-6.378-.42c-1.085-.144-1.872-1.086-1.872-2.18v-4.25m16.5 0a2.18 2.18 0 00.75-1.661V8.706c0-1.081-.768-2.015-1.837-2.175a48.114 48.114 0 00-3.413-.387m4.5 8.006c-.194.165-.42.295-.673.38A23.978 23.978 0 0112 15.75c-2.648 0-5.195-.429-7.577-1.22a2.016 2.016 0 01-.673-.38m0 0A2.18 2.18 0 013 12.489V8.706c0-1.081.768-2.015 1.837-2.175a48.111 48.111 0 013.413-.387m7.5 0V5.25A2.25 2.25 0 0013.5 3h-3a2.25 2.25 0 00-2.25 2.25v.894m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
                            </div>
                            <h3 class="mt-5 text-lg font-bold text-gray-900">Jobs App</h3>
                            <p class="mt-1 text-sm text-gray-600">A real full-stack app: auth, CRUD, dashboards and animations</p>
                        </Link>
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section class="relative px-6 py-24 overflow-hidden bg-gray-950 sm:py-28">
                <div class="absolute inset-0 bg-[radial-gradient(#1f2937_1px,transparent_4px)] [background-size:16px_16px] opacity-40"></div>
                <div class="relative max-w-2xl mx-auto text-center">
                    <h2 class="text-3xl font-bold tracking-tight text-white sm:text-4xl">Ready to build something serious?</h2>
                    <p class="max-w-xl mx-auto mt-6 text-lg leading-8 text-gray-400">
                        Install NextPy, scaffold an app, and ship your first full-stack Python application today.
                    </p>
                    <div class="flex flex-col items-center justify-center mt-10 gap-y-4 sm:flex-row sm:gap-x-6">
                        <Link href="/documentation" className="w-full px-8 py-3.5 text-sm font-bold text-gray-950 transition-all bg-white rounded-full sm:w-auto hover:bg-gray-200">
                            Get Started
                        </Link>
                        <Link href="https://github.com/RAHIMSTUDIOS/nextpy-framework" target="_blank" className="w-full px-8 py-3.5 text-sm font-bold text-white transition-all border border-gray-700 rounded-full sm:w-auto hover:bg-gray-800">
                            View on GitHub →
                        </Link>
                    </div>
                </div>
            </section>
        </div>
    )


def getServerSideProps(context):
    return {
        "props": {
            "title": "NextPy by RahimStudios - The Python Web Framework",
            "description": "NextPy is a modern Python web framework that combines server-side rendering, a reactive Python UI engine, and server actions into a single framework."
        }
    }


default = Home
