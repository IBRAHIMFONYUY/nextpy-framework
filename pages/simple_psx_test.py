"""
Simple PSX test without complex Python logic
"""

@component
def SimplePSXTest(props=None):
    """Simple test component to verify basic PSX parsing works"""
    
    return jsx("""
        <div class="simple-test">
            <h1>Simple PSX Test</h1>
            <p>This is a basic PSX component</p>
            <div class="nested">
                <span>Nested content</span>
            </div>
        </div>
    """)

def getServerSideProps(context):
    return {
        "props": {
            "title": "Simple PSX Test",
            "description": "Basic PSX parsing test"
        }
    }

# Default export
default = SimplePSXTest
