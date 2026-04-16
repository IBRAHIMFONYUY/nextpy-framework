"""
Test PSX parsing issue with nested elements - Fixed
"""
from nextpy import component

@component
def PSXTestFixed(props=None):
    """Test component to demonstrate PSX parsing fix"""
    
    return (
        <div class="outer">
            <div class="inner1">
                <p>First paragraph</p>
            </div>
            <div class="inner2">
                <p>Second paragraph</p>
            </div>
        </div>
    )

def getServerSideProps(context):
    return {
        "props": {
            "title": "PSX Test Fixed",
            "description": "Testing PSX parsing fix"
        }
    }

# Default export
default = PSXTestFixed
