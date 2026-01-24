def TailwindTest(props=None):
    """Test page for Tailwind CSS integration"""
    return (
        <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
            <div class="container mx-auto px-4 py-8">
                <header class="text-center mb-12">
                    <h1 class="text-4xl font-bold text-gray-900 mb-4">
                        Tailwind CSS Integration Test
                    </h1>
                    <p class="text-xl text-gray-600 max-w-2xl mx-auto">
                        This page tests various Tailwind CSS classes to verify integration works correctly.
                    </p>
                </header>

                <main class="space-y-12">
                    <!-- Layout Tests -->
                    <section class="bg-white rounded-lg shadow-lg p-6">
                        <h2 class="text-2xl font-semibold mb-4 text-blue-600">Layout Tests</h2>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div class="bg-blue-100 p-4 rounded-lg">
                                <h3 class="font-semibold text-blue-800 mb-2">Flexbox</h3>
                                <div class="flex justify-between items-center">
                                    <span class="text-blue-600">Left</span>
                                    <span class="text-blue-800">Center</span>
                                    <span class="text-blue-600">Right</span>
                                </div>
                            </div>
                            <div class="bg-green-100 p-4 rounded-lg">
                                <h3 class="font-semibold text-green-800 mb-2">Grid</h3>
                                <div class="grid grid-cols-2 gap-2">
                                    <div class="bg-green-200 p-2 rounded text-center text-green-700">1</div>
                                    <div class="bg-green-200 p-2 rounded text-center text-green-700">2</div>
                                    <div class="bg-green-200 p-2 rounded text-center text-green-700">3</div>
                                    <div class="bg-green-200 p-2 rounded text-center text-green-700">4</div>
                                </div>
                            </div>
                            <div class="bg-purple-100 p-4 rounded-lg">
                                <h3 class="font-semibold text-purple-800 mb-2">Spacing</h3>
                                <div class="space-y-2">
                                    <div class="bg-purple-200 p-2 rounded">m-2</div>
                                    <div class="bg-purple-300 p-3 rounded">p-3</div>
                                    <div class="bg-purple-400 p-4 rounded text-white">p-4</div>
                                </div>
                            </div>
                        </div>
                    </section>

                    <!-- Typography Tests -->
                    <section class="bg-white rounded-lg shadow-lg p-6">
                        <h2 class="text-2xl font-semibold mb-4 text-green-600">Typography Tests</h2>
                        <div class="space-y-4">
                            <h3 class="text-3xl font-bold text-gray-900">Heading 1</h3>
                            <h4 class="text-2xl font-semibold text-gray-800">Heading 2</h4>
                            <h5 class="text-xl font-medium text-gray-700">Heading 3</h5>
                            <p class="text-base text-gray-600">Paragraph text with normal size</p>
                            <p class="text-sm text-gray-500">Small text for captions</p>
                            <p class="text-xs text-gray-400">Extra small text</p>
                        </div>
                    </section>

                    <!-- Color Tests -->
                    <section class="bg-white rounded-lg shadow-lg p-6">
                        <h2 class="text-2xl font-semibold mb-4 text-purple-600">Color Tests</h2>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div class="bg-red-500 text-white p-4 rounded text-center">Red 500</div>
                            <div class="bg-blue-500 text-white p-4 rounded text-center">Blue 500</div>
                            <div class="bg-green-500 text-white p-4 rounded text-center">Green 500</div>
                            <div class="bg-yellow-500 text-black p-4 rounded text-center">Yellow 500</div>
                            <div class="bg-purple-500 text-white p-4 rounded text-center">Purple 500</div>
                            <div class="bg-pink-500 text-white p-4 rounded text-center">Pink 500</div>
                            <div class="bg-gray-500 text-white p-4 rounded text-center">Gray 500</div>
                            <div class="bg-indigo-500 text-white p-4 rounded text-center">Indigo 500</div>
                        </div>
                    </section>

                    <!-- Button Tests -->
                    <section class="bg-white rounded-lg shadow-lg p-6">
                        <h2 class="text-2xl font-semibold mb-4 text-orange-600">Button Tests</h2>
                        <div class="flex flex-wrap gap-4">
                            <button class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded transition-colors">
                                Primary Button
                            </button>
                            <button class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded transition-colors">
                                Success Button
                            </button>
                            <button class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded transition-colors">
                                Danger Button
                            </button>
                            <button class="bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded transition-colors">
                                Secondary Button
                            </button>
                        </div>
                    </section>

                    <!-- Form Tests -->
                    <section class="bg-white rounded-lg shadow-lg p-6">
                        <h2 class="text-2xl font-semibold mb-4 text-teal-600">Form Tests</h2>
                        <form class="space-y-4 max-w-md">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
                                <input type="text" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="Enter your name" />
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                <input type="email" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="Enter your email" />
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">Message</label>
                                <textarea class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" rows="4" placeholder="Enter your message"></textarea>
                            </div>
                            <button type="submit" class="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors">
                                Submit Form
                            </button>
                        </form>
                    </section>

                    <!-- Responsive Tests -->
                    <section class="bg-white rounded-lg shadow-lg p-6">
                        <h2 class="text-2xl font-semibold mb-4 text-indigo-600">Responsive Tests</h2>
                        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                            <div class="bg-indigo-100 p-4 rounded text-center">
                                <div class="text-indigo-800 font-semibold">Mobile</div>
                                <div class="text-indigo-600 text-sm">1 column</div>
                            </div>
                            <div class="bg-indigo-200 p-4 rounded text-center sm:hidden lg:block">
                                <div class="text-indigo-800 font-semibold">Tablet</div>
                                <div class="text-indigo-600 text-sm">2 columns</div>
                            </div>
                            <div class="bg-indigo-300 p-4 rounded text-center hidden sm:block lg:hidden">
                                <div class="text-indigo-800 font-semibold">Tablet</div>
                                <div class="text-indigo-600 text-sm">2 columns</div>
                            </div>
                            <div class="bg-indigo-400 p-4 rounded text-center hidden lg:block">
                                <div class="text-indigo-800 font-semibold">Desktop</div>
                                <div class="text-indigo-600 text-sm">4 columns</div>
                            </div>
                        </div>
                    </section>
                </main>

                <footer class="mt-12 text-center text-gray-600">
                    <p class="mb-4">
                        If you can see this page with proper styling, Tailwind CSS integration is working! 🎉
                    </p>
                    <div class="flex justify-center space-x-4">
                        <a href="/" class="text-blue-600 hover:text-blue-800 transition-colors">
                            Back to Home
                        </a>
                        <a href="/about" class="text-blue-600 hover:text-blue-800 transition-colors">
                            About Page
                        </a>
                    </div>
                </footer>
            </div>
        </div>
    )

default = TailwindTest
