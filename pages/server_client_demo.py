"""
Server & Client Components Demo
Shows the complete Next.js App Router pattern implementation
"""

from nextpy.psx.server_client_components import component, server_component

# Server Component - rendered exclusively on server
@server_component
def ServerSection():
    return (
    <section class="py-16 bg-blue-50 border-b border-blue-100">
        <div class="max-w-6xl px-4 mx-auto sm:px-6 lg:px-8">
            <div class="text-center mb-12">
                <h2 class="text-3xl font-bold text-blue-900 mb-4">
                    🖥️ Server Component
                </h2>
                <p class="text-lg text-blue-700 max-w-3xl mx-auto">
                    Rendered exclusively on the server. Zero JavaScript sent to client.
                    Direct access to databases, file systems, and server-side APIs.
                </p>
            </div>
            
            <div class="grid gap-8 md:grid-cols-3">
                <div class="bg-white p-6 rounded-lg shadow-md border border-blue-200">
                    <div class="text-2xl mb-3">🗄️</div>
                    <h3 class="font-semibold text-blue-900 mb-2">Database Access</h3>
                    <p class="text-sm text-gray-600">
                        Direct PostgreSQL, MySQL, SQLite connections
                    </p>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow-md border border-blue-200">
                    <div class="text-2xl mb-3">🔐</div>
                    <h3 class="font-semibold text-blue-900 mb-2">Security</h3>
                    <p class="text-sm text-gray-600">
                        API keys and secrets never leave the server
                    </p>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow-md border border-blue-200">
                    <div class="text-2xl mb-3">⚡</div>
                    <h3 class="font-semibold text-blue-900 mb-2">Performance</h3>
                    <p class="text-sm text-gray-600">
                        No client-side JavaScript bundle size
                    </p>
                </div>
            </div>
            
            <div class="mt-8 p-4 bg-blue-100 rounded-lg border border-blue-200">
                <p class="text-sm text-blue-800">
                    <strong>Rendering:</strong> This section was rendered on the server at {str(__import__('datetime').datetime.now())}
                </p>
            </div>
        </div>
    </section>
    )

# Client Component - interactive
"use client"  # This directive makes it a Client Component

@component  
def ClientSection():
    return (
    <section class="py-16 bg-green-50">
        <div class="max-w-6xl px-4 mx-auto sm:px-6 lg:px-8">
            <div class="text-center mb-12">
                <h2 class="text-3xl font-bold text-green-900 mb-4">
                    🌐 Client Component
                </h2>
                <p class="text-lg text-green-700 max-w-3xl mx-auto">
                    Pre-rendered on server for fast load, then hydrated on client for interactivity.
                    Supports state, effects, and browser APIs.
                </p>
            </div>
            
            <div class="bg-white rounded-xl shadow-lg p-8 border border-green-200">
                <h3 class="text-xl font-semibold text-gray-900 mb-6 text-center">
                    Interactive Demo
                </h3>
                
                <div class="space-y-6">
                    <!-- Interactive Counter -->
                    <div class="text-center">
                        <p class="text-sm text-gray-600 mb-3">Click Counter (Client-side State)</p>
                        <div class="flex items-center justify-center space-x-4">
                            <button 
                                class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                                onclick="window.demoCounter.decrement()"
                            >
                                −
                            </button>
                            <div class="text-3xl font-bold text-green-600 min-w-[60px]" 
                                 id="counter-value">
                                0
                            </div>
                            <button 
                                class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                                onclick="window.demoCounter.increment()"
                            >
                                +
                            </button>
                        </div>
                    </div>
                    
                    <!-- Interactive Input -->
                    <div class="text-center">
                        <p class="text-sm text-gray-600 mb-3">Live Text Input (Browser API)</p>
                        <input 
                            type="text" 
                            placeholder="Type something..." 
                            class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 w-64"
                            oninput="window.demoInput.update(this.value)"
                            id="text-input"
                        />
                        <p class="mt-2 text-sm text-gray-600">
                            You typed: <span id="output-text" class="font-semibold text-green-600"></span>
                        </p>
                    </div>
                    
                    <!-- Mouse Tracker -->
                    <div class="text-center">
                        <p class="text-sm text-gray-600 mb-3">Mouse Position (Event Handling)</p>
                        <div 
                            class="h-32 bg-gray-100 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300"
                            onmousemove="window.demoMouse.update(event)"
                            id="mouse-area"
                        >
                            <span id="mouse-position" class="text-sm text-gray-600">
                                Move mouse over this area
                            </span>
                        </div>
                    </div>
                </div>
                
                <div class="mt-8 grid gap-4 md:grid-cols-2">
                    <div class="p-4 bg-gray-50 rounded-lg">
                        <h4 class="font-semibold text-gray-900 mb-2">Client Features:</h4>
                        <ul class="space-y-1 text-sm text-gray-600">
                            <li>• useState for state management</li>
                            <li>• useEffect for side effects</li>
                            <li>• Event handlers (onclick, oninput)</li>
                            <li>• Browser API access</li>
                        </ul>
                    </div>
                    
                    <div class="p-4 bg-green-50 rounded-lg">
                        <h4 class="font-semibold text-green-900 mb-2">Rendering Flow:</h4>
                        <ul class="space-y-1 text-sm text-green-700">
                            <li>• Server: Pre-render to HTML</li>
                            <li>• Client: Download minimal JS</li>
                            <li>• Client: Hydration process</li>
                            <li>• Client: Handle interactions</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="mt-8 p-4 bg-green-100 rounded-lg border border-green-200">
                <p class="text-sm text-green-800">
                    <strong>Client Component:</strong> This section uses "use client" directive, 
                    enabling full interactivity after server pre-rendering.
                </p>
            </div>
        </div>
        
        <script>
        // Client-side interactivity scripts
        window.demoCounter = {
            value: 0,
            element: null,
            
            init() {
                this.element = document.getElementById('counter-value');
                this.update();
            },
            
            increment() {
                this.value++;
                this.update();
            },
            
            decrement() {
                this.value--;
                this.update();
            },
            
            update() {
                if (this.element) {
                    this.element.textContent = this.value;
                }
            }
        };
        
        window.demoInput = {
            element: null,
            output: null,
            
            init() {
                this.element = document.getElementById('text-input');
                this.output = document.getElementById('output-text');
            },
            
            update(value) {
                if (this.output) {
                    this.output.textContent = value || '(nothing)';
                }
            }
        };
        
        window.demoMouse = {
            element: null,
            position: null,
            
            init() {
                this.element = document.getElementById('mouse-area');
                this.position = document.getElementById('mouse-position');
            },
            
            update(event) {
                if (this.position && this.element) {
                    const rect = this.element.getBoundingClientRect();
                    const x = Math.round(event.clientX - rect.left);
                    const y = Math.round(event.clientY - rect.top);
                    this.position.textContent = `Position: (${x}, ${y})`;
                }
            }
        };
        
        // Initialize all client components when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            window.demoCounter.init();
            window.demoInput.init();
            window.demoMouse.init();
        });
        </script>
    </section>
    )

# Main page component mixing Server and Client Components
@component
def ServerClientDemo(props=None):
    props = props or {}
    
    return (
    <div class="min-h-screen bg-white">
        <!-- Hero Section -->
        <section class="py-16 bg-gradient-to-br from-blue-600 to-purple-600 text-white">
            <div class="max-w-6xl px-4 mx-auto sm:px-6 lg:px-8 text-center">
                <h1 class="text-4xl font-bold mb-4">
                    Server & Client Components
                </h1>
                <p class="text-xl opacity-90 max-w-3xl mx-auto">
                    NextPy implements the Next.js App Router pattern with Server Components by default 
                    and Client Components as opt-in.
                </p>
            </div>
        </section>
        
        <!-- Server Component Section -->
        <ServerSection />
        
        <!-- Client Component Section -->  
        <ClientSection />
        
        <!-- Architecture Comparison -->
        <section class="py-16 bg-gray-50">
            <div class="max-w-6xl px-4 mx-auto sm:px-6 lg:px-8">
                <h2 class="text-3xl font-bold text-center text-gray-900 mb-12">
                    Architecture Comparison
                </h2>
                
                <div class="grid gap-8 lg:grid-cols-2">
                    <div class="bg-white p-8 rounded-xl shadow-lg border border-blue-200">
                        <h3 class="text-xl font-semibold text-blue-900 mb-4">
                            🖥️ Server Components (Default)
                        </h3>
                        <ul class="space-y-3 text-gray-700">
                            <li class="flex items-start">
                                <span class="text-blue-600 mr-2">✓</span>
                                <span>Rendered exclusively on server</span>
                            </li>
                            <li class="flex items-start">
                                <span class="text-blue-600 mr-2">✓</span>
                                <span>Zero JavaScript footprint on client</span>
                            </li>
                            <li class="flex items-start">
                                <span class="text-blue-600 mr-2">✓</span>
                                <span>Direct database and file system access</span>
                            </li>
                            <li class="flex items-start">
                                <span class="text-blue-600 mr-2">✓</span>
                                <span>Secure API key handling</span>
                            </li>
                            <li class="flex items-start">
                                <span class="text-blue-600 mr-2">✓</span>
                                <span>Automatic by default (no directive needed)</span>
                            </li>
                        </ul>
                    </div>
                    
                    <div class="bg-white p-8 rounded-xl shadow-lg border border-green-200">
                        <h3 class="text-xl font-semibold text-green-900 mb-4">
                            🌐 Client Components (Opt-in)
                        </h3>
                        <ul class="space-y-3 text-gray-700">
                            <li class="flex items-start">
                                <span class="text-green-600 mr-2">✓</span>
                                <span>Pre-rendered on server, hydrated on client</span>
                            </li>
                            <li class="flex items-start">
                                <span class="text-green-600 mr-2">✓</span>
                                <span>Interactive with useState, useEffect</span>
                            </li>
                            <li class="flex items-start">
                                <span class="text-green-600 mr-2">✓</span>
                                <span>Browser API access</span>
                            </li>
                            <li class="flex items-start">
                                <span class="text-green-600 mr-2">✓</span>
                                <span>Event handlers and user interactions</span>
                            </li>
                            <li class="flex items-start">
                                <span class="text-green-600 mr-2">✓</span>
                                <span>Requires "use client" directive</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>
    </div>
    )


def get_server_side_props(context):
    return {
        "props": {
            "title": "Server & Client Components Demo",
            "description": "Complete demonstration of NextPy Server and Client Components following Next.js App Router pattern"
        }
    }

default = ServerClientDemo
