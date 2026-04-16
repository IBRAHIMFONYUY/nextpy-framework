"""
Simple NextPy Hooks Demo - Basic useState and useEffect
"""

@component
def SimpleHooksDemo(props=None):
    """Simple component demonstrating basic hooks"""
    from nextpy.hooks import useState
    
    # Simple useState
    count, setCount = useState(0)
    message, setMessage = useState("Hello from NextPy!")
    
    def increment():
        setCount(count + 1)
    
    def updateMessage():
        setMessage(f"Count is now {count}")
    
    return jsx("""
        <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
            <div class="max-w-4xl mx-auto">
                <div class="text-center mb-12">
                    <h1 class="text-4xl font-bold text-gray-900 mb-4">Simple Hooks Demo</h1>
                    <p class="text-xl text-gray-600">Basic useState in NextPy</p>
                </div>
                
                <div class="bg-white rounded-xl shadow-lg p-8 mb-8">
                    <h2 class="text-2xl font-semibold text-gray-900 mb-6">Counter Demo</h2>
                    
                    <div class="text-center mb-6">
                        <div class="text-6xl font-bold text-blue-600 mb-4">{count}</div>
                        <p class="text-gray-600 mb-4">{message}</p>
                    </div>
                    
                    <div class="flex justify-center gap-4">
                        <button 
                            onclick={increment}
                            class="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                        >
                            Increment
                        </button>
                        <button 
                            onclick={updateMessage}
                            class="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors"
                        >
                            Update Message
                        </button>
                    </div>
                </div>
                
                <div class="bg-white rounded-xl shadow-lg p-8">
                    <h2 class="text-2xl font-semibold text-gray-900 mb-4">How it Works</h2>
                    <div class="space-y-3 text-gray-700">
                        <p>• <strong>useState(0)</strong> - Initializes count to 0</p>
                        <p>• <strong>setCount()</strong> - Updates count and triggers re-render</p>
                        <p>• <strong>jsx()</strong> - Wraps HTML for proper rendering</p>
                        <p>• <strong>onclick</strong> - Calls Python functions on button clicks</p>
                    </div>
                </div>
            </div>
        </div>
    """)

def getServerSideProps(context):
    return {
        "props": {
            "title": "Simple Hooks Demo",
            "description": "Basic useState demonstration"
        }
    }

# Default export
default = SimpleHooksDemo
