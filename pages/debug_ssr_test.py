def Home(props=None):
    props = props or {}
    title = props.get("title", "Welcome to NextPy!")
    message = props.get("message", "Build amazing web apps with Python and True JSX")

    return (
        <div className="p-4">
            <h1>{title}</h1>
            <p>{message}</p>
        </div>
    )


def getServerSideProps(context):
    return {"props": {"title": "Welcome from SSR", "message": "Rendered on the server"}}


default = Home
