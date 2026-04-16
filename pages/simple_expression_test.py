"""
Simple test for PSX expression evaluation
"""

@component
def SimpleExpressionTest(props=None):
    """Test component with simple expressions"""
    
    message = "Hello World"
    number = 123
    
    return jsx("""
        <div class="test">
            <h1>{message}</h1>
            <p>Number: {number}</p>
            <p>Double: {number * 2}</p>
        </div>
    """)

def getServerSideProps(context):
    return {
        "props": {
            "title": "Simple Expression Test",
            "description": "Testing PSX expressions"
        }
    }

# Default export
default = SimpleExpressionTest
