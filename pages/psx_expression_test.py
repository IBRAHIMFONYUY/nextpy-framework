"""
Test PSX parser fix for expressions and nested elements
"""

@component
def PSXExpressionTest(props=None):
    """Test component to verify PSX parser handles expressions correctly"""
 
    
    return (
        <div class="test-container">
            <h1>PSX Expression Test</h1>
            <p>Count: {count}</p>
            <div class="items-list">
                
                {for item in items:
                    <div class="item">
                        <span>{item}</span>
                    </div>
                }
            </div>
            <div class="nested-test">
                <div class="inner">
                    <p>Nested content</p>
                    <span>Value: {count * 2}</span>
                </div>
            </div>
        </div>
    )

def getServerSideProps(context):
    return {
        "props": {
            "title": "PSX Expression Test",
            "description": "Testing PSX expression parsing",
            "count": 42,
            "items": ["apple", "banana", "cherry"]
        }
    }

# Default export
default = PSXExpressionTest
