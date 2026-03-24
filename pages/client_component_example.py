"""
Client Component Example
Client Components use "use client" directive and support interactivity
They are pre-rendered on server and hydrated on client
"""

"use client"  # This directive makes it a Client Component

from nextpy.psx.server_client_components import component, mark_interactive

@component
def ClientInteractiveCounter(props=None):
    """Client Component with interactive state"""
    props = props or {}
    
    # This would use useState hook in a full implementation
    # For now, we'll simulate interactivity with data attributes
    mark_interactive()  # Mark this component as interactive
    
    return (
    <section class="py-16 bg-gradient-to-br from-purple-50 to-pink-50">
        <div class="max-w-4xl px-4 mx-auto sm:px-6 lg:px-8">
            <h2 class="text-3xl font-bold text-center text-gray-900 mb-12">
                Client Component Interactivity
            </h2>
            
            <div class="bg-white rounded-xl shadow-lg p-8 border border-purple-100">
                <h3 class="text-xl font-semibold text-gray-900 mb-6">
                    Interactive Counter Component
                </h3>
                
                <!-- Interactive elements that require client-side JavaScript -->
                <div class="flex items-center justify-center space-x-4 mb-8">
                    <button 
                        class="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
                        onclick="window.counterComponent.decrement()"
                        data-counter-action="decrement"
                    >
                        − Decrease
                    </button>
                    
                    <div class="text-4xl font-bold text-purple-600 min-w-[100px] text-center" 
                         data-counter-value="0">
                        0
                    </div>
                    
                    <button 
                        class="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
                        onclick="window.counterComponent.increment()"
                        data-counter-action="increment"
                    >
                        Increase +
                    </button>
                </div>
                
                <div class="grid gap-4 md:grid-cols-2">
                    <div class="p-4 bg-gray-50 rounded-lg">
                        <h4 className="font-semibold text-gray-900 mb-2">Client Features:</h4>
                        <ul class="space-y-1 text-sm text-gray-600">
                            <li>• Event handlers (onclick, onchange)</li>
                            <li>• State management with hooks</li>
                            <li>• Browser API access</li>
                            <li>• Real-time updates</li>
                        </ul>
                    </div>
                    
                    <div class="p-4 bg-purple-50 rounded-lg">
                        <h4 className="font-semibold text-purple-900 mb-2">Rendering Flow:</h4>
                        <ul class="space-y-1 text-sm text-purple-700">
                            <li>• Server: Pre-render to HTML</li>
                            <li>• Client: Download JavaScript</li>
                            <li>• Client: Hydration (make interactive)</li>
                            <li>• Client: Handle interactions</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="mt-8 p-4 bg-purple-100 border border-purple-200 rounded-lg">
                <p class="text-sm text-purple-800">
                    <strong>Client Component:</strong> This component uses the "use client" directive, 
                    is pre-rendered on server for fast load, then hydrated on client for interactivity.
                </p>
            </div>
        </div>
        
        <!-- JavaScript for client-side interactivity -->
        <script>
        window.counterComponent = {
            value: 0,
            element: null,
            
            init() {
                this.element = document.querySelector('[data-counter-value]');
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
        
        // Initialize when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            window.counterComponent.init();
        });
        </script>
    </section>
    )


def get_server_side_props(context):
    """Server-side pre-rendering data"""
    return {
        "props": {
            "title": "Client Components Demo",
            "description": "Interactive Client Components with hydration and state management"
        }
    }

default = ClientInteractiveCounter
