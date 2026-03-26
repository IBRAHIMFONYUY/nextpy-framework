"""
PSX Language Demo - NO IMPORTS NEEDED!
This demonstrates PSX as a complete language with auto-completion and built-in utilities.
"""

# NO IMPORTS! PSX automatically provides everything!

def PSXLanguageDemo(props=None):
    """Demonstrating PSX as a complete language - NO IMPORTS NEEDED!"""
    props = props or {}
    
    # Sample data using built-in utilities
    users = [
        {"id": 1, "name": "Alice", "age": 25, "active": True},
        {"id": 2, "name": "Bob", "age": 30, "active": False},
        {"id": 3, "name": "Charlie", "age": 35, "active": True}
    ]
    me='rahim'

    
    return (
       
    <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    
        <header class="bg-white border-b border-gray-200 shadow-sm">
            <div class="px-4 py-6 mx-auto max-w-7xl sm:px-6 lg:px-8">
                <h1 class="text-3xl font-bold text-gray-900">
                    PSX Language Demo - No Imports Needed!
                </h1>
                <p class="mt-2 text-gray-600">
                    Everything is automatically available: map, filter, console, Math, etc.
                </p>
            </div>
        </header>
        
        <main class="px-4 py-12 mx-auto max-w-7xl sm:px-6 lg:px-8">
            {/* Array Methods - AUTO-AVAILABLE! */}
            <section class="mb-12">
                <h2 class="mb-6 text-2xl font-semibold text-gray-900">
                    Pure Python Array Methods (No Imports!)
                </h2>
                
                <div class="p-6 mb-6 bg-white rounded-lg shadow-md">
                    <h3 class="mb-4 text-lg font-medium text-gray-900">Active Users:</h3>
                    <ul class="space-y-2">
                        {list(filter(lambda user: user['active'], users)).map(lambda user: (
                            <li key={user['id']} class="flex items-center justify-between p-3 rounded-md bg-green-50">
                                <span class="font-medium text-green-900">{user['name']}</span>
                                <span class="text-green-700">Age: {user['age']}</span>
                            </li>
                        ))}
                    </ul>
                </div>
                
                <div class="p-6 bg-white rounded-lg shadow-md">
                    <h3 class="mb-4 text-lg font-medium text-gray-900">All Users (with reduce):</h3>
                    <div class="text-gray-700">
                        Total users: {len(users)} | 
                        Average age: {round(sum(user['age'] for user in users) / len(users))} | 
                        Active users: {len(list(filter(lambda user: user['active'], users)))}
                    </div>
                </div>
            </section>
            
            {/* String Methods - AUTO-AVAILABLE! */}
            <section class="mb-12">
                <h2 class="mb-6 text-2xl font-semibold text-gray-900">
                    String Methods (No Imports!)
                </h2>
                
                <div class="p-6 bg-white rounded-lg shadow-md">
                    <div class="space-y-3">
                        <div class="p-3 rounded bg-blue-50">
                            <code class="text-blue-900">upper:</code> 
                            <span class="ml-2 text-blue-700">{"hello world".upper()}</span>
                        </div>
                        <div class="p-3 rounded bg-purple-50">
                            <code class="text-purple-900">split & join:</code> 
                            <span class="ml-2 text-purple-700">{" ".join(["a", "b", "c"])}</span>
                        </div>
                        <div class="p-3 rounded bg-indigo-50">
                            <code class="text-indigo-900">in:</code> 
                            <span class="ml-2 text-indigo-700">
                                {"Py" in "NextPy" and "Contains 'Py'" or "No 'Py' found"}
                            </span>
                        </div>
                    </div>
                </div>
            </section>
            
            {/* Math Utilities - AUTO-AVAILABLE! */}
            <section class="mb-12">
                <h2 class="mb-6 text-2xl font-semibold text-gray-900">
                    Math Utilities (No Imports!)
                </h2>
                
                <div class="p-6 bg-white rounded-lg shadow-md">
                    <div class="grid grid-cols-2 gap-4 md:grid-cols-4">
                        <div class="p-4 text-center rounded bg-gray-50">
                            <div class="text-2xl font-bold text-gray-900">{math.pi}</div>
                            <div class="text-sm text-gray-600">math.pi</div>
                        </div>
                        <div class="p-4 text-center rounded bg-gray-50">
                            <div class="text-2xl font-bold text-gray-900">{math.e}</div>
                            <div class="text-sm text-gray-600">math.e</div>
                        </div>
                        <div class="p-4 text-center rounded bg-gray-50">
                            <div class="text-2xl font-bold text-gray-900">{round(3.7)}</div>
                            <div class="text-sm text-gray-600">round(3.7)</div>
                        </div>
                        <div class="p-4 text-center rounded bg-gray-50">
                            <div class="text-2xl font-bold text-gray-900">{max(1, 5, 3)}</div>
                            <div class="text-sm text-gray-600">max(1,5,3)</div>
                        </div>
                    </div>
                </div>
            </section>
            
            {/* Console Utilities - AUTO-AVAILABLE! */}
            <section class="mb-12">
                <h2 class="mb-6 text-2xl font-semibold text-gray-900">
                    Console Utilities (No Imports!)
                </h2>
                
                <div class="p-6 bg-white rounded-lg shadow-md">
                    <div class="space-y-4">
                        <button 
                            onClick={() => print("Hello from PSX!", users)}
                            class="px-4 py-2 text-white transition-colors bg-blue-600 rounded-md hover:bg-blue-700"
                        >
                            print Users
                        </button>
                        <button 
                            onClick={() => print("This is a warning!")}
                            class="px-4 py-2 ml-2 text-white transition-colors bg-yellow-600 rounded-md hover:bg-yellow-700"
                        >
                            print Warning
                        </button>
                        <button 
                            onClick={() => print("This is an error!")}
                            class="px-4 py-2 ml-2 text-white transition-colors bg-red-600 rounded-md hover:bg-red-700"
                        >
                            print Error
                        </button>
                        <button 
                            onClick={() => print(json.dumps(users, indent=2))}
                            class="px-4 py-2 ml-2 text-white transition-colors bg-purple-600 rounded-md hover:bg-purple-700"
                        >
                            print JSON
                        </button>
                    </div>
                </div>
            </section>
            
            {/* Type Utilities - AUTO-AVAILABLE! */}
            <section class="mb-12">
                <h2 class="mb-6 text-2xl font-semibold text-gray-900">
                    Type Utilities (No Imports!)
                </h2>
                
                <div class="p-6 bg-white rounded-lg shadow-md">
                    <div class="space-y-2">
                        <div class="p-2 rounded bg-gray-50">
                            <span class="font-mono">type("hello") = </span>
                            <span class="font-bold text-blue-600">{type("hello").__name__}</span>
                        </div>
                        <div class="p-2 rounded bg-gray-50">
                            <span class="font-mono">isinstance([1,2,3], list) = </span>
                            <span class="font-bold text-green-600">{str(isinstance([1,2,3], list))}</span>
                        </div>
                        <div class="p-2 rounded bg-gray-50">
                            <span class="font-mono">isinstance({{}}, dict) = </span>
                            <span class="font-bold text-purple-600">{str(isinstance({}, dict))}</span>
                        </div>
                        <div class="p-2 rounded bg-gray-50">
                            <span class="font-mono">callable(lambda: None) = </span>
                            <span class="font-bold text-orange-600">{str(callable(lambda: None))}</span>
                        </div>
                    </div>
                </div>
            </section>
            
            {/* Conditional Rendering - AUTO-AVAILABLE! */}
            <section class="mb-12">
                <h2 class="mb-6 text-2xl font-semibold text-gray-900">
                    Conditional Utilities (No Imports!)
                </h2>
                
                <div class="p-6 bg-white rounded-lg shadow-md">
                    <div class="space-y-4">
                        <div class="p-3 rounded bg-green-50">
                            <code class="text-green-900">ternary:</code>
                            <span class="ml-2 text-green-700">
                                {ternary(True, "This is true", "This is false")}
                            </span>
                        </div>
                        <div class="p-3 rounded bg-blue-50">
                            <code class="text-blue-900">and:</code>
                            <span class="ml-2 text-blue-700">
                                {True and "Both true"} vs {False and "Won't show"}
                            </span>
                        </div>
                        <div class="p-3 rounded bg-purple-50">
                            <code class="text-purple-900">or:</code>
                            <span class="ml-2 text-purple-700">
                                {False or "This shows because first is false"}
                            </span>
                        </div>
                    </div>
                </div>
            </section>
            
            {/* JSON Utilities - AUTO-AVAILABLE! */}
            <section class="mb-12">
                <h2 class="mb-6 text-2xl font-semibold text-gray-900">
                    JSON Utilities (No Imports!)
                </h2>
                
                <div class="p-6 bg-white rounded-lg shadow-md">
                    <div class="space-y-4">
                        <div>
                            <h3 class="mb-2 text-lg font-medium text-gray-900">json.dumps:</h3>
                            <pre class="p-3 overflow-x-auto text-sm bg-gray-100 rounded">
                                {json.dumps(users, indent=2)}
                            </pre>
                        </div>
                        <div>
                            <h3 class="mb-2 text-lg font-medium text-gray-900">json.loads:</h3>
                            <pre class="p-3 overflow-x-auto text-sm bg-gray-100 rounded">
                                {json.dumps(json.loads('{"name": "PSX", "version": "1.0"}'), indent=2)}
                            </pre>
                        </div>
                    </div>
                </div>
            </section>
            
            {/* Date Utilities - AUTO-AVAILABLE! */}
            <section class="mb-12">
                <h2 class="mb-6 text-2xl font-semibold text-gray-900">
                    Date Utilities (No Imports!)
                </h2>
                
                <div class="p-6 bg-white rounded-lg shadow-md">
                    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <div class="p-3 rounded bg-blue-50">
                            <code class="text-blue-900">now():</code>
                            <div class="mt-1 text-blue-700">{int(time.time() * 1000)}</div>
                        </div>
                        <div class="p-3 rounded bg-green-50">
                            <code class="text-green-900">datetime.now():</code>
                            <div class="mt-1 text-green-700">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
                        </div>
                    </div>
                </div>
            </section>
            
            {/* Summary */}
            <section class="mb-12">
                <div class="p-8 text-white rounded-lg shadow-lg bg-gradient-to-r from-blue-500 to-purple-600">
                    <h2 class="mb-4 text-3xl font-bold">PSX is a Complete Language! 🚀</h2>
                    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                        <div>
                            <h3 class="mb-2 text-xl font-semibold">✅ No Imports Needed</h3>
                            <p class="text-blue-100">Everything is automatically available when you write PSX</p>
                        </div>
                        <div>
                            <h3 class="mb-2 text-xl font-semibold">✅ Pure Python Methods</h3>
                            <p class="text-blue-100">map, filter, reduce, split, join, upper, lower, etc.</p>
                        </div>
                        <div>
                            <h3 class="mb-2 text-xl font-semibold">✅ Built-in Utilities</h3>
                            <p class="text-blue-100">math, json, datetime, type, isinstance, etc.</p>
                        </div>
                        <div>
                            <h3 class="mb-2 text-xl font-semibold">✅ Auto-completion</h3>
                            <p class="text-blue-100">IntelliSense for tags, attributes, utilities</p>
                        </div>
                        <div>
                            <h3 class="mb-2 text-xl font-semibold">✅ Real-time Validation</h3>
                            <p class="text-blue-100">Syntax checking and error reporting</p>
                        </div>
                        <div>
                            <h3 class="mb-2 text-xl font-semibold">✅ Language Server</h3>
                            <p class="text-blue-100">VS Code-like language support</p>
                        </div>
                    </div>
                    
                    <div class="p-4 mt-8 bg-white rounded-lg bg-opacity-20">
                        <p class="text-lg font-medium">
                            PSX is now a TRUE language like JSX but in pure Python - just write PSX and everything works!
                        </p>
                    </div>
                </div>
            </section>
        </main>
    </div>
)


def get_server_side_props(context):
    """Server-side props with no imports needed!"""
    return {
        "props": {
            "title": "PSX Language Demo - No Imports Needed!",
            "description": "Complete PSX language with auto-completion, IntelliSense, and built-in utilities",
            "features": [
                "Auto-completion for HTML tags",
                "JavaScript-style array methods",
                "Built-in Math, console, JSON utilities",
                "Real-time syntax validation",
                "Language server support",
                "No imports required!"
            ]
        }
    }

