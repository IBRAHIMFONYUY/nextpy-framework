from nextpy.psx import component as interactive_component, Link


@interactive_component
def AboutPage(props=None):
    props = props or {}
    title = props.get('title')

    return (
        <div>

        <div class="px-4 py-20 bg-gradient-to-br from-blue-50 to-indigo-50">
            <div class="max-w-6xl mx-auto text-center">
                <h1 class="mb-6 text-5xl font-bold text-transparent md:text-6xl bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text">{title}</h1>
                <p class="max-w-3xl mx-auto text-xl text-gray-600">Bridging Python's power with modern web development. Build production-ready applications faster — frontend and backend in one language.</p>
            </div>
        </div>

        <div class="max-w-6xl px-4 py-16 mx-auto">

            <div class="mb-20">
                <h2 class="mb-6 text-4xl font-bold text-gray-900">Our Mission</h2>
                <div class="grid items-center gap-12 md:grid-cols-2">
                    <div>
                        <p class="mb-4 text-xl text-gray-700">NextPy was created to solve a fundamental problem: Python developers shouldn't have to abandon their preferred language or ecosystem to build modern web applications.</p>
                        <p class="mb-4 text-lg text-gray-600">We combined the rendering model of modern meta-frameworks with Python's elegance, creating a framework that lets you:</p>
                        <ul class="space-y-3">
                            <li class="flex items-center gap-3">
                                <div class="flex items-center justify-center w-10 h-10 text-white rounded-lg shadow-lg bg-gradient-to-br from-blue-600 to-indigo-600">
                                    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                                    </svg>
                                </div>
                                <span class="text-gray-700">Write frontend and backend in one language</span>
                            </li>
                            <li class="flex items-center gap-3">
                                <div class="flex items-center justify-center w-10 h-10 text-white rounded-lg shadow-lg bg-gradient-to-br from-emerald-600 to-teal-600">
                                    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
                                    </svg>
                                </div>
                                <span class="text-gray-700">Ship SSR, SSG and ISR pages with one routing model</span>
                            </li>
                            <li class="flex items-center gap-3">
                                <div class="flex items-center justify-center w-10 h-10 text-white rounded-lg shadow-lg bg-gradient-to-br from-violet-600 to-purple-600">
                                    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 22.5 12 13.5H3.75z" />
                                    </svg>
                                </div>
                                <span class="text-gray-700">Get reactive UI with PSX — no JavaScript build step</span>
                            </li>
                            <li class="flex items-center gap-3">
                                <div class="flex items-center justify-center w-10 h-10 text-white rounded-lg shadow-lg bg-gradient-to-br from-amber-500 to-orange-600">
                                    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M21 11.25v8.25a1.5 1.5 0 01-1.5 1.5H5.25a1.5 1.5 0 01-1.5-1.5v-8.25M12 4.875A2.625 2.625 0 109.375 7.5H12m0-2.625V7.5m0-2.625A2.625 2.625 0 1114.625 7.5H12m0 0V21m-8.625-9.75h18c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125h-18c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
                                    </svg>
                                </div>
                                <span class="text-gray-700">Leverage Python's rich ecosystem — FastAPI, SQLAlchemy, Pydantic</span>
                            </li>
                        </ul>
                    </div>
                    <div class="p-8 text-white bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl">
                        <h3 class="mb-4 text-2xl font-bold">Why NextPy?</h3>
                        <div class="space-y-4">
                            <div class="p-4 bg-white rounded-lg bg-opacity-20">
                                <strong>For Python Developers</strong>
                                <p class="mt-2 text-sm opacity-90">Build complete web apps in Python without learning a second ecosystem</p>
                            </div>
                            <div class="p-4 bg-white rounded-lg bg-opacity-20">
                                <strong>For Teams</strong>
                                <p class="mt-2 text-sm opacity-90">One language across frontend, backend and tooling reduces context switching</p>
                            </div>
                            <div class="p-4 bg-white rounded-lg bg-opacity-20">
                                <strong>For Startups</strong>
                                <p class="mt-2 text-sm opacity-90">Ship faster with file-based routing, hot reload and built-in auth</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="p-12 mb-20 bg-gray-50 rounded-2xl">
                <h2 class="mb-12 text-4xl font-bold text-gray-900">Tech Stack</h2>
                <div class="grid gap-8 md:grid-cols-3">
                    <div class="p-6 transition bg-white shadow-sm rounded-xl hover:shadow-lg">
                        <div class="flex items-center justify-center w-16 h-16 mb-4 text-white shadow-lg bg-gradient-to-br from-emerald-600 to-teal-600 rounded-xl">
                            <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <h3 class="mb-2 text-xl font-bold">Backend</h3>
                        <p class="mb-3 text-gray-600">FastAPI + Uvicorn</p>
                        <p class="text-sm text-gray-500">High-performance async framework with automatic OpenAPI documentation.</p>
                    </div>

                    <div class="p-6 transition bg-white shadow-sm rounded-xl hover:shadow-lg">
                        <div class="flex items-center justify-center w-16 h-16 mb-4 text-white shadow-lg bg-gradient-to-br from-violet-600 to-purple-600 rounded-xl">
                            <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <h3 class="mb-2 text-xl font-bold">Frontend</h3>
                        <p class="mb-3 text-gray-600">PSX + Tailwind CSS</p>
                        <p class="text-sm text-gray-500">Reactive Python UI compiled to the browser — no JavaScript toolchain.</p>
                    </div>

                    <div class="p-6 transition bg-white shadow-sm rounded-xl hover:shadow-lg">
                        <div class="flex items-center justify-center w-16 h-16 mb-4 text-white shadow-lg bg-gradient-to-br from-sky-600 to-blue-600 rounded-xl">
                            <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
                            </svg>
                        </div>
                        <h3 class="mb-2 text-xl font-bold">Database</h3>
                        <p class="mb-3 text-gray-600">SQLAlchemy ORM</p>
                        <p class="text-sm text-gray-500">Support for SQLite, PostgreSQL, MySQL</p>
                    </div>

                    <div class="p-6 transition bg-white shadow-sm rounded-xl hover:shadow-lg">
                        <div class="flex items-center justify-center w-16 h-16 mb-4 text-white shadow-lg bg-gradient-to-br from-rose-600 to-pink-600 rounded-xl">
                            <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                            </svg>
                        </div>
                        <h3 class="mb-2 text-xl font-bold">Auth</h3>
                        <p class="mb-3 text-gray-600">Session Auth + Guards</p>
                        <p class="text-sm text-gray-500">Cookie sessions, login actions and protected routes</p>
                    </div>

                    <div class="p-6 transition bg-white shadow-sm rounded-xl hover:shadow-lg">
                        <div class="flex items-center justify-center w-16 h-16 mb-4 text-white shadow-lg bg-gradient-to-br from-cyan-600 to-sky-600 rounded-xl">
                            <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M8.288 15.038a5.25 5.25 0 017.424 0M5.106 11.856a9 9 0 0112.788 0M1.924 8.674a13.125 13.125 0 0116.152 0M12.53 18.22l-.53.53-.53-.53a.75.75 0 011.06 0zM12 12h.008v.008H12V12z" />
                            </svg>
                        </div>
                        <h3 class="mb-2 text-xl font-bold">Real-time</h3>
                        <p class="mb-3 text-gray-600">WebSocket + Streaming</p>
                        <p class="text-sm text-gray-500">Live updates, pub/sub channels and streaming responses</p>
                    </div>

                    <div class="p-6 transition bg-white shadow-sm rounded-xl hover:shadow-lg">
                        <div class="flex items-center justify-center w-16 h-16 mb-4 text-white shadow-lg bg-gradient-to-br from-indigo-600 to-blue-600 rounded-xl">
                            <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17L17.25 21A2.652 2.652 0 0021 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 11-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 004.486-6.336l-3.276 3.277a3.004 3.004 0 01-2.25-2.25l3.276-3.276a4.5 4.5 0 00-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437l1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008z" />
                            </svg>
                        </div>
                        <h3 class="mb-2 text-xl font-bold">Utilities</h3>
                        <p class="mb-3 text-gray-600">CLI + Tooling</p>
                        <p class="text-sm text-gray-500">nextpy create, dev, build — plus caching, metadata and SEO helpers</p>
                    </div>
                </div>
            </div>

            <div class="grid gap-12 mb-20 lg:grid-cols-2">
                <div>
                    <h2 class="mb-8 text-4xl font-bold text-gray-900">Shipped in NextPy</h2>
                    <ul class="space-y-4">
                        <li class="flex items-start gap-3">
                            <div class="flex items-center justify-center flex-shrink-0 w-6 h-6 mt-0.5 text-white rounded-full bg-emerald-600">
                                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                            </div>
                            <div>
                                <strong class="text-gray-900">PSX engine</strong>
                                <p class="text-sm text-gray-600">Signal-based reactivity, selective hydration, WAAPI animations and FLIP transitions — all from Python.</p>
                            </div>
                        </li>
                        <li class="flex items-start gap-3">
                            <div class="flex items-center justify-center flex-shrink-0 w-6 h-6 mt-0.5 text-white rounded-full bg-emerald-600">
                                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                            </div>
                            <div>
                                <strong class="text-gray-900">SSR, SSG, ISR & SPA router</strong>
                                <p class="text-sm text-gray-600">Three rendering modes with client-side navigation, prefetching and per-layout asset loading.</p>
                            </div>
                        </li>
                        <li class="flex items-start gap-3">
                            <div class="flex items-center justify-center flex-shrink-0 w-6 h-6 mt-0.5 text-white rounded-full bg-emerald-600">
                                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                            </div>
                            <div>
                                <strong class="text-gray-900">Server actions & API routes</strong>
                                <p class="text-sm text-gray-600">Secure RPC-style actions plus REST endpoints and streaming responses.</p>
                            </div>
                        </li>
                        <li class="flex items-start gap-3">
                            <div class="flex items-center justify-center flex-shrink-0 w-6 h-6 mt-0.5 text-white rounded-full bg-emerald-600">
                                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                            </div>
                            <div>
                                <strong class="text-gray-900">Auth, ORM & CLI</strong>
                                <p class="text-sm text-gray-600">Cookie sessions, SQLAlchemy models, route guards and a scaffolding CLI.</p>
                            </div>
                        </li>
                        <li class="flex items-start gap-3">
                            <div class="flex items-center justify-center flex-shrink-0 w-6 h-6 mt-0.5 text-white rounded-full bg-emerald-600">
                                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                            </div>
                            <div>
                                <strong class="text-gray-900">Documentation site</strong>
                                <p class="text-sm text-gray-600">50+ pages covering tutorials, concepts, how-to guides and the full API reference.</p>
                            </div>
                        </li>
                    </ul>
                </div>

                <div>
                    <h2 class="mb-8 text-4xl font-bold text-gray-900">On the roadmap</h2>
                    <div class="p-8 bg-gray-50 border border-gray-200 rounded-2xl">
                        <ul class="space-y-4">
                            <li class="flex items-center gap-3 text-gray-700">
                                <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
                                First-class file uploads
                            </li>
                            <li class="flex items-center gap-3 text-gray-700">
                                <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
                                Built-in internationalization (i18n)
                            </li>
                            <li class="flex items-center gap-3 text-gray-700">
                                <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
                                Pytest-style app testing API
                            </li>
                            <li class="flex items-center gap-3 text-gray-700">
                                <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
                                Plugin & template ecosystem
                            </li>
                            <li class="flex items-center gap-3 text-gray-700">
                                <span class="w-2 h-2 bg-gray-400 rounded-full"></span>
                                Page-level WebSocket hooks
                            </li>
                        </ul>
                        <p class="mt-6 text-sm text-gray-500">Roadmap items are prioritized by community need — vote on GitHub Discussions.</p>
                    </div>
                </div>
            </div>

            <div class="p-12 text-center text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl">
                <h2 class="mb-6 text-4xl font-bold">Join the Community</h2>
                <p class="mb-8 text-xl opacity-90">NextPy is open-source. Contribute, report issues, or just say hello!</p>
                <div class="flex flex-wrap justify-center gap-4">
                    <Link href="https://github.com/RAHIMSTUDIOS/nextpy-framework" target="_blank" className="px-8 py-3 font-semibold text-blue-600 transition bg-white rounded-lg hover:bg-gray-100">GitHub</Link>
                    <Link href="/documentation" className="px-8 py-3 font-semibold text-white transition border-2 border-white rounded-lg hover:bg-white hover:text-blue-600">Docs</Link>
                    <Link href="/templates" className="px-8 py-3 font-semibold text-white transition border-2 border-white rounded-lg hover:bg-white hover:text-blue-600">Templates</Link>
                    <Link href="https://github.com/RAHIMSTUDIOS/nextpy-framework/discussions" target="_blank" className="px-8 py-3 font-semibold text-white transition border-2 border-white rounded-lg hover:bg-white hover:text-blue-600">Discussions</Link>
                </div>
            </div>
        </div>
        </div>

    )


def getServerSideProps(context):
    # Fetch any necessary data for the About page here
    return {
        'props': {
            'title': 'About NextPy'
        }
    }

default = AboutPage
