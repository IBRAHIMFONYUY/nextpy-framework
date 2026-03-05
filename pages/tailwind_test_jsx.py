"""
Tailwind Test with True JSX
Tests Tailwind CSS classes in JSX components
"""

def TailwindTest(props=None):
    """Tailwind CSS test component with JSX"""
    props = props or {}
    
    return (
        <div class="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600">
            <div class="container mx-auto px-4 py-8">
                <header class="text-center mb-12">
                    <h1 class="text-5xl font-bold text-white mb-4">Tailwind CSS + JSX Test</h1>
                    <p class="text-xl text-blue-100">Testing Tailwind classes in NextPy JSX components</p>
                </header>
                
                <main class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div class="bg-white p-6 rounded-lg shadow-lg">
                        <h2 class="text-2xl font-semibold text-gray-800 mb-4">Typography</h2>
                        <p class="text-gray-600 mb-4">This tests text styling with Tailwind.</p>
                        <span class="inline-block bg-blue-500 text-white px-3 py-1 rounded-full text-sm">Badge</span>
                    </div>
                    
                    <div class="bg-white p-6 rounded-lg shadow-lg">
                        <h2 class="text-2xl font-semibold text-gray-800 mb-4">Colors</h2>
                        <div class="flex space-x-2 mb-4">
                            <div class="w-8 h-8 bg-red-500 rounded"></div>
                            <div class="w-8 h-8 bg-green-500 rounded"></div>
                            <div class="w-8 h-8 bg-blue-500 rounded"></div>
                            <div class="w-8 h-8 bg-yellow-500 rounded"></div>
                        </div>
                        <p class="text-gray-600">Color palette test</p>
                    </div>
                    
                    <div class="bg-white p-6 rounded-lg shadow-lg">
                        <h2 class="text-2xl font-semibold text-gray-800 mb-4">Layout</h2>
                        <div class="flex justify-between items-center mb-4">
                            <span class="text-sm text-gray-500">Flex layout</span>
                            <button class="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded transition-colors">
                                Button
                            </button>
                        </div>
                    </div>
                    
                    <div class="bg-white p-6 rounded-lg shadow-lg">
                        <h2 class="text-2xl font-semibold text-gray-800 mb-4">Spacing</h2>
                        <div class="space-y-2">
                            <div class="bg-gray-100 p-2 rounded">p-2</div>
                            <div class="bg-gray-200 p-4 rounded">p-4</div>
                            <div class="bg-gray-300 p-6 rounded">p-6</div>
                        </div>
                    </div>
                    
                    <div class="bg-white p-6 rounded-lg shadow-lg">
                        <h2 class="text-2xl font-semibold text-gray-800 mb-4">Borders</h2>
                        <div class="border-2 border-blue-500 rounded-lg p-4">
                            <p class="text-blue-600 font-medium">Bordered element</p>
                        </div>
                    </div>
                    
                    <div class="bg-white p-6 rounded-lg shadow-lg">
                        <h2 class="text-2xl font-semibold text-gray-800 mb-4">Transitions</h2>
                        <div class="transform hover:scale-105 transition-transform duration-300 bg-gradient-to-r from-pink-500 to-orange-500 text-white p-4 rounded-lg text-center">
                            <p>Hover me!</p>
                        </div>
                    </div>
                </main>
                
                <footer class="mt-12 text-center">
                    <nav class="flex justify-center space-x-6">
                        <a href="/" class="text-white hover:text-blue-200 transition-colors">Home</a>
                        <a href="/about" class="text-white hover:text-blue-200 transition-colors">About</a>
                        <a href="/tailwind_demo" class="text-white hover:text-blue-200 transition-colors">HTML Demo</a>
                    </nav>
                    <p class="text-white text-sm mt-4">© 2024 NextPy Framework</p>
                </footer>
            </div>
        </div>
    )

def get_server_side_props(context):
    return {
        "props": {}
    }

default = TailwindTest
