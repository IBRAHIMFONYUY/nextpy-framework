"""
Test PSX parsing issue with nested elements - Fixed
"""

@component
def PSXTestFixed(props=None):
    """Test component to demonstrate PSX parsing fix"""
    
    return jsx("""
        <div class="outer">
            <div class="inner1">
                <p>First paragraph</p>
            </div>
            <div class="inner2">
                <p>Second paragraph</p>
            </div>
        </div>
    """)

def getServerSideProps(context):
    return {
        "props": {
            "title": "PSX Test Fixed",
            "description": "Testing PSX parsing fix"
        }
    }

# Default export
default = PSXTestFixed
