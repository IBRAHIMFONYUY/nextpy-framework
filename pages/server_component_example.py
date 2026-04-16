"""
Server Component Example
Server Components are rendered exclusively on the server
They have access to server-side resources and don't send JavaScript to client
"""

from nextpy.psx.server_client_components import server_component

@server_component
def ServerFeatureList(props=None):
    """Server Component - can access databases, file system, etc."""
    props = props or {}
    
    # Simulate server-side data fetching
    server_features = [
        {
            "icon": "database",
            "title": "Database Access",
            "description": "Direct access to PostgreSQL, MySQL, SQLite databases",
        },
        {
            "icon": "shield",
            "title": "Secure Operations", 
            "description": "Environment variables and API keys stay on server",
        },
        {
            "icon": "file",
            "title": "File System",
            "description": "Read and write files directly on the server",
        }
    ]
    
    return (
    <section class="py-16 bg-gray-50">
        <div class="max-w-6xl px-4 mx-auto sm:px-6 lg:px-8">
            <h2 class="text-3xl font-bold text-center text-gray-900 mb-12">
                Server Component Features
            </h2>
            
            <div class="grid gap-8 md:grid-cols-3">
                {server_features.map(feature => (
                <div class="p-6 bg-white rounded-lg shadow-md border border-gray-200">
                    <div class="flex items-center mb-4">
                        <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                            <span class="text-2xl">⚙️</span>
                        </div>
                        <h3 class="ml-4 text-xl font-semibold text-gray-900">
                            {feature['title']}
                        </h3>
                    </div>
                    <p class="text-gray-600">{feature['description']}</p>
                </div>
                ))}
            </div>
            
            <div class="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p class="text-sm text-blue-800">
                    <strong>Server Component:</strong> This component is rendered exclusively on the server 
                    and has zero JavaScript footprint on the client.
                </p>
            </div>
        </div>
    </section>
    )


def get_server_side_props(context):
    """Server-side data fetching for Server Components"""
    return {
        "props": {
            "title": "Server Components Demo",
            "description": "Demonstrating NextPy Server Components with zero client-side JavaScript"
        }
    }

default = ServerFeatureList
