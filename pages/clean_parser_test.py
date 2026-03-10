"""
Test the clean PSX parser
"""

@component
def CleanParserTest(props=None):
    """Test component for the clean tokenizer + stack parser"""
    
    count = 42
    items = ["apple", "banana", "cherry"]
    
    return jsx("""
        <div class="clean-test">
            <h1>Clean Parser Test</h1>
            <p>Count: {count}</p>
            <div class="nested-test">
                <div class="inner">
                    <span>Nested content: {count * 2}</span>
                </div>
            </div>
        </div>
    """)

def getServerSideProps(context):
    return {
        "props": {
            "title": "Clean Parser Test",
            "description": "Testing the clean PSX parser"
        }
    }

# Default export
default = CleanParserTest
