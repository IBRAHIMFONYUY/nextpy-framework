"""
Example: Interactive Counter Component with Hydration Engine

This example demonstrates how to use the NextPy Hydration Engine
to create an interactive component with client-side state management.
"""

from nextpy.psx import component, useState, create_onclick
from nextpy.psx.hydration import interactive_component, create_interactive_page


# Example 1: Basic Interactive Counter
@interactive_component
def InteractiveCounter(props=None):
    """A simple interactive counter component"""
    [count, setCount] = useState(0)
    [message, setMessage] = useState("Hello, NextPy!")
    
    props = props or {}
    title = props.get("title", "Interactive Counter")
    
    return psx("""
        <div class="container mx-auto p-8">
            <h1 class="text-4xl font-bold mb-4">{title}</h1>
            <p class="text-xl mb-4">{message}</p>
            
            <div class="bg-gray-100 p-6 rounded-lg">
                <h2 class="text-2xl font-bold mb-4">Count: {count}</h2>
                
                <div class="flex gap-4">
                    <button onclick={lambda e: setCount(count + 1)} 
                            class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">
                        Increment
                    </button>
                    
                    <button onclick={lambda e: setCount(count - 1)} 
                            class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded">
                        Decrement
                    </button>
                    
                    <button onclick={lambda e: setCount(0)} 
                            class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded">
                        Reset
                    </button>
                </div>
            </div>
        </div>
    """)


# Example 2: Form with Interactive Validation
@interactive_component
def InteractiveForm(props=None):
    """A form with interactive validation"""
    [name, setName] = useState("")
    [email, setEmail] = useState("")
    [submitted, setSubmitted] = useState(False)
    [errors, setErrors] = useState({})
    
    def handleNameChange(e):
        # In actual implementation, would be called from event listener
        pass
    
    def handleEmailChange(e):
        # In actual implementation, would be called from event listener
        pass
    
    def handleSubmit(e):
        # Validate form
        new_errors = {}
        if not name:
            new_errors['name'] = 'Name is required'
        if not email or '@' not in email:
            new_errors['email'] = 'Valid email is required'
        
        if new_errors:
            setErrors(new_errors)
        else:
            setSubmitted(True)
    
    return psx("""
        <div class="container mx-auto p-8 max-w-md">
            <h1 class="text-3xl font-bold mb-6">Contact Form</h1>
            
            {if submitted:
                <div class="bg-green-100 border border-green-400 text-green-700 p-4 rounded mb-4">
                    ✓ Form submitted successfully!
                </div>
            {/if}}
            
            <form onsubmit={handleSubmit}>
                <div class="mb-4">
                    <label class="block text-gray-700 font-bold mb-2">Name</label>
                    <input type="text" 
                           onchange={handleNameChange}
                           class="w-full px-3 py-2 border border-gray-300 rounded"
                           placeholder="Your name">
                    {if errors.get('name'):
                        <p class="text-red-500 text-sm mt-1">{errors['name']}</p>
                    {/if}}
                </div>
                
                <div class="mb-6">
                    <label class="block text-gray-700 font-bold mb-2">Email</label>
                    <input type="email"
                           onchange={handleEmailChange}
                           class="w-full px-3 py-2 border border-gray-300 rounded"
                           placeholder="your@email.com">
                    {if errors.get('email'):
                        <p class="text-red-500 text-sm mt-1">{errors['email']}</p>
                    {/if}}
                </div>
                
                <button type="submit" 
                        class="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded">
                    Submit
                </button>
            </form>
        </div>
    """)


# Example 3: Using with getServerSideProps
def getServerSideProps(context):
    """Server-side data fetching"""
    return {
        "props": {
            "title": "My Interactive App",
            "initialMessage": "Welcome to NextPy Hydration Engine!",
        }
    }


# Export the main component
default = InteractiveCounter
