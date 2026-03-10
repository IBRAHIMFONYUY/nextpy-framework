"""
NextPy Hooks Demo - useState and useEffect implementation
"""

@component
def HooksDemo(props=None):
    """Component demonstrating useState and useEffect hooks"""

    from nextpy.hooks import useState, useEffect

    props = props or {}

    # -------------------------
    # STATE
    # -------------------------

    count, setCount = useState(0)
    text, setText = useState("Hello NextPy!")
    isVisible, setIsVisible = useState(True)
    data, setData = useState([])
    loading, setLoading = useState(False)

    # -------------------------
    # FUNCTIONS
    # -------------------------

    def simulateDataFetch():
        """Simulate API request"""
        setLoading(True)

        items = [
            {"id": 1, "name": "Item 1", "value": count * 10},
            {"id": 2, "name": "Item 2", "value": count * 20},
            {"id": 3, "name": "Item 3", "value": count * 30},
        ]

        setData(items)
        setLoading(False)
        
    def incrementCount():
        setCount(count + 1)

    def decrementCount():
        setCount(count - 1)

    def resetCount():
        setCount(0)

    def toggleVisibility():
        setIsVisible(not isVisible)

    def handleInput(e):
        setText(e.target.value)

    # -------------------------
    # EFFECTS
    # -------------------------

   

    useEffect(lambda: print("Component mounted!"), [])

    useEffect(
        lambda: print(f"Count changed → {count}"),
        [count]
    )

    # -------------------------
    # COMPONENT
    # -------------------------

    return (
        <div class="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 p-8">
            <div class="max-w-6xl mx-auto">

                <div class="text-center mb-12">
                    <h1 class="text-4xl font-bold text-gray-900 mb-4">
                        NextPy Hooks Demo
                    </h1>
                    <p class="text-xl text-gray-600">
                        useState and useEffect in Action
                    </p>
                </div>

              

                <div class="bg-white rounded-xl shadow-lg p-8 mb-8">

                    <h2 class="text-2xl font-semibold mb-6">
                        🔢 useState Counter
                    </h2>

                    <div class="text-center mb-6">
                        <div class="text-6xl font-bold text-indigo-600">
                            {count}
                        </div>
                    </div>

                    <div class="flex justify-center gap-4">

                        <button
                            onclick={incrementCount}
                            class="px-6 py-3 bg-indigo-600 text-white rounded-lg"
                        >
                            Increment
                        </button>

                        <button
                            onclick={decrementCount}
                            class="px-6 py-3 bg-red-600 text-white rounded-lg"
                        >
                            Decrement
                        </button>

                        <button
                            onclick={resetCount}
                            class="px-6 py-3 bg-gray-600 text-white rounded-lg"
                        >
                            Reset
                        </button>

                    </div>

                </div>

                <div class="bg-white rounded-xl shadow-lg p-8 mb-8">

                    <h2 class="text-2xl font-semibold mb-6">
                        ✏️ useState Text
                    </h2>

                    <input
                        type="text"
                        value={text}
                        oninput={handleInput}
                        class="w-full px-4 py-3 border rounded-lg"
                    />

                    <p class="mt-4 text-indigo-600 font-semibold">
                        {text}
                    </p>

                </div>

                

                <div class="bg-white rounded-xl shadow-lg p-8 mb-8">

                    <h2 class="text-2xl font-semibold mb-6">
                        👁️ Visibility Toggle
                    </h2>

                    <button
                        onclick={toggleVisibility}
                        class="px-6 py-3 bg-purple-600 text-white rounded-lg mb-6"
                    >
                        Toggle
                    </button>

                    { if {{isVisible}}:
                        <div class="p-6 bg-purple-50 rounded-lg">
                            Content is visible
                        </div>
                    else:
                        <div class="p-6 bg-gray-50 rounded-lg">
                            Content is hidden
                        </div>
                    }

                </div>

                

                <div class="bg-white rounded-xl shadow-lg p-8 mb-8">

                    <h2 class="text-2xl font-semibold mb-6">
                        🔄 useEffect Data Fetch
                    </h2>

                    {
                        <div class="text-center py-6">
                            Loading data...
                        </div>
                        if loading else
                        <div class="grid md:grid-cols-3 gap-4">

                            {
                                [
                                    <div
                                        key={item["id"]}
                                        class="p-4 bg-indigo-50 rounded-lg"
                                    >
                                        <h3 class="font-semibold">
                                            {item["name"]}
                                        </h3>

                                        <p class="text-2xl font-bold text-indigo-600">
                                            {item["value"]}
                                        </p>

                                    </div>

                                    for item in data
                                ]
                            }

                        </div>
                    }

                </div>

                

                <div class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl p-8">

                    <h2 class="text-2xl font-bold mb-4">
                        📚 Hook Summary
                    </h2>

                    <ul class="space-y-2">

                        <li>• useState manages local component state</li>
                        <li>• setState triggers re-render</li>
                        <li>• useEffect handles lifecycle events</li>
                        <li>• Dependency arrays control effect execution</li>

                    </ul>

                </div>

            </div>
        </div>
    )


def getServerSideProps(context):

    return {
        "props": {
            "title": "NextPy Hooks Demo",
            "description": "Learn useState and useEffect in NextPy"
        }
    }


default = HooksDemo