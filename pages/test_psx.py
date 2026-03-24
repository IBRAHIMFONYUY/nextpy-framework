from nextpy.hooks import useState, useEffect
@component
def Home(props=None):
    [count, setCount] = useState(0)
    [message, setMessage] = useState("Click the button!")
    
    useEffect(effect=message )
    
    return (
        <div class="container">
            <h1>{message}</h1>
            <p>Count: {count}</p>
            <button onClick={setCount}>
                Click Me
            </button>
        </div>
    )
    
def getServerSideProps(context):
    [count, setCount] = useState(0)
    print(count)
    return{
        'props':{
            'count': count,
            'setCount':setCount(count + 1)
        }
    }

default = Home