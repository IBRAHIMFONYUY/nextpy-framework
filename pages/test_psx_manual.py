@component
def Home(props=None):
    props = props or {}
    title = props.get("title", "Welcome to NextPy")
    message = props.get("message", "Your Python-powered web framework with True JSX")
   
    
    return (
        <div class="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-500 to-purple-600">
            <div class="text-center text-white">
                <h1 class="mb-4 text-5xl font-bold">{title}</h1>
                <p class="text-xl">{message}</p>
                <a href="/about" class="inline-block px-6 py-3 mt-8 font-semibold text-blue-600 transition-all duration-300 transform bg-white rounded-lg shadow-lg hover:bg-gray-100 hover:text-blue-700 hover:scale-105">
                    Learn More
                </a>
            </div>
            
        </div>
    )

def getServerSideProps(context):
    return {
        "props": {
            "title": "Welcome to NextPy",
            "message": "Your Python-powered web framework with True JSX"
        }
    }

default = Home