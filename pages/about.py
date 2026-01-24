"""About page with True JSX"""

def About(props=None):
    """About page component"""
    props = props or {}
    
    title = props.get("title", "About NextPy")
    description = props.get("description", "Learn about NextPy framework")
    
    return (
        <div class="max-w-4xl px-4 py-12 mx-auto">
            <h1 class="mb-6 text-4xl font-bold text-gray-900">{title}</h1>
            <p class="mb-4 text-lg text-gray-600">{description}</p>
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h2 class="mb-4 text-2xl font-semibold text-blue-600">Features</h2>
                <ul class="space-y-2 text-gray-700">
                    <li class="flex items-center"><span class="mr-2">✅</span> True JSX in Python</li>
                    <li class="flex items-center"><span class="mr-2">✅</span> File-based routing</li>
                    <li class="flex items-center"><span class="mr-2">✅</span> Server-side rendering</li>
                    <li class="flex items-center"><span class="mr-2">✅</span> Tailwind CSS integration</li>
                    <li class="flex items-center"><span class="mr-2">✅</span> Hot reload development</li>
                    <li class="flex items-center"><span class="mr-2">✅</span> Plugin system</li>
                </ul>
            </div>
            <div class="mt-8 text-center">
                <a href="/" class="text-blue-600 hover:text-blue-800 font-medium">
                    ← Back to Home
                </a>
            </div>
        </div>
    )

def getServerSideProps(context):
    return {
        "props": {
            "title": "About NextPy",
            "description": "Learn about NextPy framework"
        }
    }

default = About
