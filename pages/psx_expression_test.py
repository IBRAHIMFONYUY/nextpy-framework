"""
Test PSX parser fix for expressions and nested elements
"""

@component
def PSXExpressionTest(props=None):
    """Test component to verify PSX parser handles expressions correctly"""
    
    # Local variables that should be automatically captured
    count = 42
    items = ["apple", "banana", "cherry"]
    user_data = {
        "name": "John Doe",
        "age": 30,
        "active": True
    }
    
    return (
        <div class="test-container">
            <h1>PSX Expression Test</h1>
            <p>Count: {count}</p>
            <p>Double Count: {count * 2}</p>
            <p>User: {user_data['name']} (Age: {user_data['age']})</p>
            
            <div class="items-list">
                <h3>Simple For Loop:</h3>
                {for item in items:
                    <div class="item">
                        <span>{item}</span>
                    </div>
                }
            </div>
            
            <div class="enumerated-list">
                <h3>Enumerated For Loop:</h3>
                {for i, item in enumerate(items):
                    <div class="enumerated-item">
                        <span>{i + 1}. {item}</span>
                    </div>
                }
            </div>
            
            <div class="conditional-test">
                <h3>Conditional:</h3>
                {if user_data['active']:
                    <p class="active">User is active!</p>
                }
                {if count > 50:
                    <p>Count is greater than 50</p>
                else:
                    <p>Count is {count} (not greater than 50)</p>
                }
            </div>
            
            <div class="nested-test">
                <div class="inner">
                    <p>Nested content</p>
                    <span>Value: {count * 2}</span>
                    <div class="deep-nest">
                        {for i in range(3):
                            <div class="level-{i}">
                                Level {i}: {items[i] if i < len(items) else 'N/A'}
                            </div>
                        }
                    </div>
                </div>
            </div>
        </div>
    )

def getServerSideProps(context):
    return {
        "props": {
            "title": "PSX Expression Test",
            "description": "Testing PSX expression parsing",
            
            
        }
    }

# Default export
default = PSXExpressionTest
