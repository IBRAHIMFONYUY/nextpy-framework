from nextpy.psx import component, Link


@component
def Home(props=None):
    props = props or {}
    title = props.get("title", "NextPy — The Python Web Framework")
    description = props.get(
        "description",
        "NextPy is a full-stack Python framework. Server-rendered pages, "
        "a reactive UI engine, and server actions — in one language."
    )

    counter_code = (
        "from nextpy.psx import component, useState\n\n"
        "@component\n"
        "def Counter():\n"
        "    [count, set_count] = useState(0)\n\n"
        "    def increment():\n"
        "        set_count(count + 1)\n\n"
        "    return (...)\n"
        "\n"
        "# UI updates instantly — no reload, no JS"
    )

    page_code = (
        "from nextpy.psx import component\n"
        "from app.db import db\n\n"
        "@component\n"
        "def Post(props):\n"
        "    post = props['post']\n"
        "    return (...)\n\n"
        "def getServerSideProps(ctx):\n"
        "    post = db.posts.find(ctx.params['slug'])\n"
        "    return {'props': {'post': post}}\n"
    )

    metrics = [
        ("3", "Rendering modes"),
        ("6", "PSX hooks"),
        ("50+", "Docs pages"),
        ("0", "JavaScript to write"),
    ]

    features = [
        ("Server rendering", "SSR, SSG, and incremental revalidation — configured per page.", "/documentation/concepts/rendering", "Rendering guide"),
        ("Reactive UI", "useState, useEffect, useRef — with fine-grained DOM updates.", "/documentation/concepts/psx-internals", "PSX internals"),
        ("Server actions", "Call Python functions from the client with built-in loading states.", "/documentation/reference/server-actions", "Server actions"),
        ("File-based routing", "Drop a file in pages/ and it's a route. Dynamic segments included.", "/documentation/getting-started/layouts-pages", "Layouts & pages"),
        ("Data & auth", "SQLAlchemy models, sessions, and protected routes — built in.", "/documentation/howto/database", "Database guide"),
        ("API routes", "REST endpoints under pages/api plus streaming for AI and real-time.", "/documentation/howto/api", "API guide"),
    ]

    explore = [
        ("Documentation", "Tutorials, guides, and full API reference.", "/documentation"),
        ("Examples", "Interactive demos of state, effects, and animations.", "/examples"),
        ("Templates", "SaaS, blogs, dashboards, and AI apps.", "/templates"),
        ("Animation Playground", "Every Motion primitive — live and interactive.", "/animation-playground"),
    ]

    return (
        <div class="font-sans antialiased text-gray-900">

            {/* ── HERO ─────────────────────────────────────────── */}
            <section class="bg-white border-b border-gray-100">
                <div class="mx-auto max-w-7xl px-6 pt-24 pb-24 sm:pt-32 sm:pb-32 lg:px-8">
                    <div class="grid items-center gap-16 lg:grid-cols-[1.05fr_1fr] lg:gap-20">

                        {/* Left */}
                        <div>
                            <div class="inline-flex items-center gap-2 rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs font-medium text-gray-700">
                                <span class="h-1.5 w-1.5 rounded-full bg-blue-600"></span>
                                v1.0 · Reactive Python UI
                            </div>

                            <h1 class="mt-8 text-5xl font-extrabold leading-[1.05] tracking-tight text-gray-950 sm:text-6xl">
                                Write Python.<br />
                                <span class="text-gray-400">Ship the web.</span>
                            </h1>

                            <p class="mt-8 max-w-xl text-lg leading-relaxed text-gray-600">
                                {description} One language from the database to the DOM — no JavaScript build step.
                            </p>

                            <div class="mt-10 flex flex-wrap items-center gap-3">
                                <Link href="/documentation" class="inline-flex items-center gap-2 rounded-full bg-gray-950 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-gray-800">
                                    Get started
                                    <span aria-hidden="true">→</span>
                                </Link>
                                <Link href="/documentation/tutorials/first-app" class="inline-flex items-center gap-2 rounded-full border border-gray-300 bg-white px-6 py-3 text-sm font-semibold text-gray-900 transition-colors hover:bg-gray-50">
                                    Read the docs
                                </Link>
                            </div>
                        </div>

                        {/* Right — code preview */}
                        <div class="relative">
                            <div class="absolute -inset-4 rounded-3xl bg-gradient-to-tr from-blue-500/10 via-transparent to-indigo-500/10 blur-2xl"></div>
                            <div class="relative overflow-hidden rounded-2xl border border-gray-800 bg-gray-950 shadow-2xl shadow-gray-900/30 ring-1 ring-white/10">
                            <div class="flex items-center justify-between border-b border-gray-800 px-4 py-3">
                                <div class="flex items-center gap-1.5">
                                    <span class="h-2.5 w-2.5 rounded-full bg-gray-700"></span>
                                    <span class="h-2.5 w-2.5 rounded-full bg-gray-700"></span>
                                    <span class="h-2.5 w-2.5 rounded-full bg-gray-700"></span>
                                </div>
                                <span class="font-mono text-xs text-gray-500">pages/counter.py</span>
                            </div>
                            <pre class="overflow-x-auto p-5 font-mono text-[13px] leading-6 text-gray-200"><code>{counter_code}</code></pre>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* ── METRICS ──────────────────────────────────────── */}
            <section class="border-b border-gray-100 bg-gray-50/60">
                <div class="mx-auto max-w-7xl px-6 lg:px-8">
                    <div class="grid grid-cols-2 gap-6 py-8 sm:grid-cols-4 sm:gap-0">
                        {for m in metrics:
                            <div class="sm:border-l sm:border-gray-200 sm:pl-6 sm:first:border-l-0 sm:first:pl-0">
                                <div class="text-4xl font-extrabold tracking-tight text-gray-950">{m[0]}</div>
                                <div class="mt-2 text-xs font-medium uppercase tracking-wider text-gray-500">{m[1]}</div>
                            </div>
                        }
                    </div>
                </div>
            </section>

            {/* ── FEATURES ─────────────────────────────────────── */}
            <section class="bg-white py-24">
                <div class="mx-auto max-w-7xl px-6 lg:px-8">
                    <div class="max-w-2xl">
                        <p class="text-sm font-semibold uppercase tracking-wider text-blue-600">Capabilities</p>
                        <h2 class="mt-3 text-4xl font-bold tracking-tight text-gray-950 sm:text-5xl">
                            One framework. Every layer.
                        </h2>
                        <p class="mt-4 text-lg leading-relaxed text-gray-600">
                            Rendering, reactivity, data, and deployment — no glue code, no context switching.
                        </p>
                    </div>

                    <div class="mt-16 grid overflow-hidden rounded-2xl border border-gray-200 bg-gray-200 sm:grid-cols-2 lg:grid-cols-3 gap-px">
                        {for f in features:
                            <Link href="{f[2]}" class="group relative flex flex-col bg-white p-8 transition-colors hover:bg-gray-50">
                                <span class="absolute inset-x-0 top-0 h-0.5 origin-left scale-x-0 bg-blue-600 transition-transform duration-300 group-hover:scale-x-100"></span>
                                <div class="text-base font-semibold text-gray-950 transition-colors group-hover:text-blue-600">{f[0]}</div>
                                <p class="mt-2 flex-1 text-sm leading-6 text-gray-600">{f[1]}</p>
                                <div class="mt-4 flex items-center gap-1 text-sm font-medium text-gray-500 transition-colors group-hover:text-blue-600">
                                    {f[3]}
                                    <span aria-hidden="true" class="transition-transform group-hover:translate-x-0.5">→</span>
                                </div>
                            </Link>
                        }
                    </div>
                </div>
            </section>

            {/* ── HOW IT WORKS ─────────────────────────────────── */}
            <section class="border-t border-gray-100 bg-gray-50 py-24">
                <div class="mx-auto grid max-w-7xl gap-16 px-6 lg:grid-cols-2 lg:items-center lg:px-8">
                    <div>
                        <p class="text-sm font-semibold uppercase tracking-wider text-blue-600">How it works</p>
                        <h2 class="mt-3 text-4xl font-bold tracking-tight text-gray-950 sm:text-5xl">
                            Python in. Web out.
                        </h2>
                        <p class="mt-6 text-lg leading-relaxed text-gray-600">
                            NextPy compiles your Python components into a reactive client runtime, served by a production-grade FastAPI backend. Write one language — the framework handles the rest.
                        </p>

                        <ol class="mt-10 space-y-6">
                            <li class="flex gap-4">
                                <span class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-gray-950 text-xs font-bold text-white">1</span>
                                <div>
                                    <div class="font-semibold text-gray-950">Write pages and components</div>
                                    <p class="mt-1 text-sm leading-6 text-gray-600">PSX markup and Python logic — in the same file.</p>
                                </div>
                            </li>
                            <li class="flex gap-4">
                                <span class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-gray-950 text-xs font-bold text-white">2</span>
                                <div>
                                    <div class="font-semibold text-gray-950">Fetch data on the server</div>
                                    <p class="mt-1 text-sm leading-6 text-gray-600">getServerSideProps, getStaticProps, getStaticPaths.</p>
                                </div>
                            </li>
                            <li class="flex gap-4">
                                <span class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-gray-950 text-xs font-bold text-white">3</span>
                                <div>
                                    <div class="font-semibold text-gray-950">Ship with one command</div>
                                    <p class="mt-1 text-sm leading-6 text-gray-600">
                                        <code class="rounded bg-gray-200 px-1.5 py-0.5 font-mono text-xs text-gray-800">nextpy build</code> — SSR, static export, and API routes.
                                    </p>
                                </div>
                            </li>
                        </ol>

                        <Link href="/documentation/tutorials/first-app" class="mt-10 inline-flex items-center gap-1 text-sm font-semibold text-blue-600 hover:text-blue-700">
                            Follow the first-app tutorial
                            <span aria-hidden="true">→</span>
                        </Link>
                    </div>

                    <div class="relative">
                        <div class="absolute -inset-4 rounded-3xl bg-gradient-to-tr from-indigo-500/10 via-transparent to-blue-500/10 blur-2xl"></div>
                        <div class="relative overflow-hidden rounded-2xl border border-gray-800 bg-gray-950 shadow-2xl shadow-gray-900/30 ring-1 ring-white/10">
                        <div class="flex items-center justify-between border-b border-gray-800 px-4 py-3">
                            <div class="flex items-center gap-1.5">
                                <span class="h-2.5 w-2.5 rounded-full bg-gray-700"></span>
                                <span class="h-2.5 w-2.5 rounded-full bg-gray-700"></span>
                                <span class="h-2.5 w-2.5 rounded-full bg-gray-700"></span>
                            </div>
                            <span class="font-mono text-xs text-gray-500">pages/blog/[slug].py</span>
                        </div>
                        <pre class="overflow-x-auto p-5 font-mono text-[13px] leading-6 text-gray-200"><code>{page_code}</code></pre>
                        </div>
                    </div>
                </div>
            </section>

            {/* ── EXPLORE ──────────────────────────────────────── */}
            <section class="border-t border-gray-100 bg-white py-24">
                <div class="mx-auto max-w-7xl px-6 lg:px-8">
                    <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                        <div>
                            <p class="text-sm font-semibold uppercase tracking-wider text-blue-600">Explore</p>
                            <h2 class="mt-3 text-3xl font-bold tracking-tight text-gray-950 sm:text-4xl">Go deeper</h2>
                        </div>
                        <p class="max-w-md text-sm text-gray-500">Everything you need to go from install to production.</p>
                    </div>

                    <div class="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        {for item in explore:
                            <Link href="{item[2]}" class="group flex flex-col rounded-xl border border-gray-200 bg-white p-6 transition-all hover:border-gray-300 hover:shadow-sm">
                                <div class="text-base font-semibold text-gray-950 transition-colors group-hover:text-blue-600">{item[0]}</div>
                                <p class="mt-2 flex-1 text-sm leading-6 text-gray-600">{item[1]}</p>
                                <div class="mt-4 flex items-center gap-1 text-sm font-medium text-gray-500 transition-colors group-hover:text-blue-600">
                                    Explore
                                    <span aria-hidden="true" class="transition-transform group-hover:translate-x-0.5">→</span>
                                </div>
                            </Link>
                        }
                    </div>
                </div>
            </section>

            {/* ── CTA ──────────────────────────────────────────── */}
            <section class="bg-gray-950 py-24">
                <div class="mx-auto max-w-4xl px-6 text-center lg:px-8">
                    <h2 class="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                        Ready to write your next app in Python?
                    </h2>
                    <p class="mx-auto mt-6 max-w-xl text-lg leading-relaxed text-gray-400">
                        Install NextPy, scaffold a project, and ship your first full-stack Python app in under a minute.
                    </p>
                    <div class="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
                        <Link href="/documentation" class="inline-flex items-center gap-2 rounded-full bg-white px-6 py-3 text-sm font-semibold text-gray-950 transition-colors hover:bg-gray-200">
                            Get started
                            <span aria-hidden="true">→</span>
                        </Link>
                        <Link href="https://github.com/RAHIMSTUDIOS/nextpy-framework" target="_blank" class="inline-flex items-center gap-2 rounded-full border border-gray-700 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-gray-800">
                            View on GitHub
                        </Link>
                    </div>
                </div>
            </section>
        </div>
    )


def getServerSideProps(context):
    return {
        "props": {
            "title": "NextPy — The Python Web Framework",
            "description": "NextPy is a full-stack Python framework. Server-rendered pages, a reactive UI engine, and server actions — in one language."
        }
    }


default = Home