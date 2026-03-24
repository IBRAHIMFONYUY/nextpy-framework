from nextpy.psx import component, class_component, useState, useEffect, map_list, conditional, and_condition, register_component
from nextpy.psx.components import PSXComponent, ChildrenComponent, EventHandlers



@component
def HomeWithChildren(props=None):
    features = [
        "✅ True PSX Syntax",
        "✅ Component-Based Architecture", 
        "✅ Server-Side Rendering",
        "✅ Hot Reload Support"
    ]
    
    def render_feature(feature):
        return <li>{feature}</li>
    
    feature_items = map_list(features, render_feature)
    
    return (
        <div class="container">
            <h1>NextPy Features</h1>
            <ul>
                {feature_items}
            </ul>
        </div>
    )

def getServerSideProps(context):
    count, setCount = useState(0)
    message, setMessage = useState("Click the button!")
    
    def check_count():
        if count > 5:
            setMessage("You're clicking a lot!")
    
    useEffect(check_count, [count])
  
    return{
        'props':{
            "name":'world',
            'message':message,
            'count':count
            
        }
    }
    
default = HomeWithChildren
