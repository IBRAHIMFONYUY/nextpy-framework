"""
Simple PSX test without complex Python logic
"""
from fastapi import requests
@component
def SimplePSXTest(props=None):
    

def getServerSideProps(context):
    host='https:localhost:5000'
    response=requests.Request.get(host)
    print(response)
    return {
        "props": {
            "title": "Simple PSX Test",
            "description": "Basic PSX parsing test"
        }
    }

# Default export
default = SimplePSXTest
