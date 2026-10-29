from nextpy.psx import component, psx


@component
def FirstAppTutorial():
    return psx("""
        <div class="mx-auto max-w-4xl">
            <div class="mb-8 pb-6 border-b border-gray-800">
                <div class="flex items-center gap-3 mb-4">
                    <span class="px-2 py-1 text-xs font-medium border rounded bg-blue-500/20 text-blue-400 border-blue-500">
                        Tutorial
                    </span>
                    <span class="px-2 py-1 text-xs font-medium border rounded bg-green-500/20 text-green-400 border-green-500">
                        Beginner
                    </span>
                    <span class="px-2 py-1 text-xs font-medium border rounded bg-gray-700 text-gray-300 border-gray-600">
                        NextPy 5.0.0
                    </span>
                    <span class="ml-auto text-sm text-gray-400">
                        ⏱ 10 minutes
                    </span>
                </div>
                
                <h1 class="text-4xl font-bold text-white">
                    Build Your First NextPy App
                </h1>
                
                <p class="mt-4 text-lg text-gray-400">
                    Learn the basics of NextPy by creating your first application from scratch in just 10 minutes.
                </p>
            </div>
            
            <div class="my-6 p-4 border border-gray-700 bg-gray-800 rounded-lg">
                <div class="flex items-start gap-3">
                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-gray-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                    <div class="flex-1">
                        <h4 class="font-semibold text-gray-200">Prerequisites</h4>
                        <ul class="mt-2 space-y-1 text-sm text-gray-400">
                            <li class="flex items-center gap-2">
                                <svg class="w-3 h-3 text-green-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                                </svg>
                                Python 3.11 or higher installed
                            </li>
                            <li class="flex items-center gap-2">
                                <svg class="w-3 h-3 text-green-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                                </svg>
                                Basic Python knowledge
                            </li>
                            <li class="flex items-center gap-2">
                                <svg class="w-3 h-3 text-green-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                                </svg>
                                Terminal/command line access
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <section id="overview" class="my-12 scroll-mt-20">
                <h2 class="text-3xl font-bold text-white mb-6">
                    What You'll Build
                </h2>
                <p class="text-gray-300 mb-4">
                    In this tutorial, you'll build a simple NextPy application with:
                </p>
                <ul class="list-disc list-inside space-y-2 text-gray-300 ml-4">
                    <li>A component-based UI using PSX</li>
                    <li>Interactive state with hooks</li>
                    <li>Styling with Tailwind CSS</li>
                    <li>Hot-reload development server</li>
                </ul>
            </section>
            
            <section id="installation" class="my-12 scroll-mt-20">
                <h2 class="text-3xl font-bold text-white mb-6">
                    Step 1: Install NextPy
                </h2>
                <p class="text-gray-300 mb-4">
                    First, install NextPy using pip:
                </p>
                
                <div class="my-6 overflow-hidden rounded-lg border border-gray-700 bg-gray-900">
                    <div class="flex items-center justify-between px-4 py-2 border-b border-gray-700 bg-gray-800">
                        <span class="px-2 py-0.5 text-xs font-medium text-gray-300 uppercase bg-gray-700 rounded">
                            bash
                        </span>
                    </div>
                    <pre class="p-4 overflow-x-auto text-sm leading-relaxed">
                        <code class="language-bash">pip install nextpy-framework</code>
                    </pre>
                </div>
            </section>
            
            <section id="create-project" class="my-12 scroll-mt-20">
                <h2 class="text-3xl font-bold text-white mb-6">
                    Step 2: Create Your Project
                </h2>
                <p class="text-gray-300 mb-4">
                    Use the NextPy CLI to create a new project:
                </p>
                
                <div class="my-6 overflow-hidden rounded-lg border border-gray-700 bg-gray-900">
                    <div class="flex items-center justify-between px-4 py-2 border-b border-gray-700 bg-gray-800">
                        <span class="px-2 py-0.5 text-xs font-medium text-gray-300 uppercase bg-gray-700 rounded">
                            bash
                        </span>
                    </div>
                    <pre class="p-4 overflow-x-auto text-sm leading-relaxed">
                        <code class="language-bash">nextpy create my-first-app</code>
                    </pre>
                </div>
                
                <p class="text-gray-300 mb-4">
                    Navigate into your project directory:
                </p>
                
                <div class="my-6 overflow-hidden rounded-lg border border-gray-700 bg-gray-900">
                    <div class="flex items-center justify-between px-4 py-2 border-b border-gray-700 bg-gray-800">
                        <span class="px-2 py-0.5 text-xs font-medium text-gray-300 uppercase bg-gray-700 rounded">
                            bash
                        </span>
                    </div>
                    <pre class="p-4 overflow-x-auto text-sm leading-relaxed">
                        <code class="language-bash">cd my-first-app</code>
                    </pre>
                </div>
            </section>
            
            <section id="first-component" class="my-12 scroll-mt-20">
                <h2 class="text-3xl font-bold text-white mb-6">
                    Step 3: Create Your First Component
                </h2>
                <p class="text-gray-300 mb-4">
                    Open pages/index.py and create your first component:
                </p>
                
                <div class="my-6 overflow-hidden rounded-lg border border-gray-700 bg-gray-900">
                    <div class="flex items-center justify-between px-4 py-2 border-b border-gray-700 bg-gray-800">
                        <span class="text-sm text-gray-400 font-mono">pages/index.py</span>
                        <span class="px-2 py-0.5 text-xs font-medium text-gray-300 uppercase bg-gray-700 rounded">
                            python
                        </span>
                    </div>
                    <pre class="p-4 overflow-x-auto text-sm leading-relaxed">
                        <code class="language-python">from nextpy.psx import component

@component
def Home():
    return (
        &lt;div class="p-8 bg-gray-900 min-h-screen"&gt;
            &lt;h1 class="text-4xl font-bold text-white"&gt;
                Hello, NextPy!
            &lt;/h1&gt;
            &lt;p class="mt-4 text-gray-300"&gt;
                Welcome to your first NextPy application.
            &lt;/p&gt;
        &lt;/div&gt;
    )

default = Home</code>
                    </pre>
                </div>
            </section>
            
            <section id="run-app" class="my-12 scroll-mt-20">
                <h2 class="text-3xl font-bold text-white mb-6">
                    Step 4: Run Your Application
                </h2>
                <p class="text-gray-300 mb-4">
                    Start the development server:
                </p>
                
                <div class="my-6 overflow-hidden rounded-lg border border-gray-700 bg-gray-900">
                    <div class="flex items-center justify-between px-4 py-2 border-b border-gray-700 bg-gray-800">
                        <span class="px-2 py-0.5 text-xs font-medium text-gray-300 uppercase bg-gray-700 rounded">
                            bash
                        </span>
                    </div>
                    <pre class="p-4 overflow-x-auto text-sm leading-relaxed">
                        <code class="language-bash">nextpy dev</code>
                    </pre>
                </div>
                
                <div class="my-6 p-4 border-l-4 border-green-500 bg-green-900/20 rounded-r-lg">
                    <div class="flex items-start gap-3">
                        <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div class="flex-1">
                            <h4 class="font-semibold text-green-400">Success!</h4>
                            <div class="mt-1 text-sm text-gray-300">
                                Open your browser and visit http://localhost:8000. You should see your NextPy application!
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            
            <section id="next-steps" class="my-12 scroll-mt-20">
                <h2 class="text-3xl font-bold text-white mb-6">
                    What's Next?
                </h2>
                <p class="text-gray-300 mb-4">
                    Congratulations! You've built your first NextPy application. Here's what to explore next:
                </p>
                
                <ul class="space-y-2 text-gray-300">
                    <li>Learn about file-based routing</li>
                    <li>Explore PSX syntax</li>
                    <li>Build a Todo app tutorial</li>
                    <li>Add Tailwind CSS styling</li>
                </ul>
            </section>
        </div>
    """)


default = FirstAppTutorial
