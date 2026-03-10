"""
PSX Test Page - Testing NextPy PSX functionality with JSX-like syntax
"""

from nextpy.psx import component


@component
def Page(props=None):
    """PSX test page demonstrating various features"""
    props = props or {}
    
    return (
        <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
            <div class="max-w-4xl mx-auto">
                <h1 class="text-4xl font-bold text-gray-800 mb-4">PSX Test Page</h1>
                <p class="text-lg text-gray-600 mb-8">Testing NextPy PSX functionality with various features</p>
                
                <div class="bg-white rounded-lg shadow-md p-6 mb-8">
                    <h2 class="text-2xl font-semibold text-indigo-600 mb-3">Basic PSX Elements</h2>
                    <p class="text-gray-700 mb-4">This is a paragraph with <span class="text-red-500 font-bold">styled text</span>.</p>
                    <button class="bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded transition-colors" onClick="alert('PSX is working!')">
                        Click Me!
                    </button>
                </div>

                <div class="bg-white rounded-lg shadow-md p-6 mb-8">
                    <h2 class="text-2xl font-semibold text-green-600 mb-3">List Example</h2>
                    <ul class="list-disc list-inside text-gray-700 space-y-2">
                        <li>First item with <strong>bold text</strong></li>
                        <li>Second item with <em>italic text</em></li>
                        <li>Third item with <a href="#" class="text-blue-500 hover:underline">link</a></li>
                    </ul>
                </div>

                <div class="bg-white rounded-lg shadow-md p-6">
                    <h2 class="text-2xl font-semibold text-purple-600 mb-4">Form Example</h2>
                    <form class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Name:</label>
                            <input type="text" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="Enter your name" />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Message:</label>
                            <textarea class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500" rows="3" placeholder="Enter your message"></textarea>
                        </div>
                        <button type="submit" class="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-md transition-colors" onClick="alert('Form submitted!')">
                            Submit Form
                        </button>
                    </form>
                </div>

                <div class="mt-8 text-center text-gray-600">
                    <p>✨ PSX is working perfectly! This page demonstrates JSX-like syntax in Python.</p>
                </div>
            </div>
        </div>
    )
default=Page
