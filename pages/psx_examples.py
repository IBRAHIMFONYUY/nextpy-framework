"""
Complete PSX Component Examples - All styles you requested
Demonstrates every React-like pattern with pure Python
"""

from nextpy.psx import component, class_component, useState, useEffect, map_list, conditional, and_condition, register_component
from nextpy.psx.components import PSXComponent, ChildrenComponent, EventHandlers


# 🎯 Style 1: Simple Function (Recommended)
@component
def Home(props=None):
    props = props or {}
    return (
        <div class="container">
            <h1>Hello {props.get("name", "World")}</h1>
            <button onClick="alert('Hello!')">Click Me</button>
        </div>
    )


# 🎯 Style 2: With Server-Side Props
@component
def HomeWithSSR(props=None):
    return (
        <div class="container">
            <h1>{props.get("title", "Welcome")}</h1>
            <p>{props.get("message", "Hello NextPy!")}</p>
        </div>
    )

def getServerSideProps(context):
    return {
        "props": {
            "title": "Dynamic Title",
            "message": "Server-rendered content!"
        }
    }


# 🎯 Style 3: Functional with Hooks
@component
def HomeWithHooks(props=None):
    count, setCount = useState(0)
    message, setMessage = useState("Click the button!")
    
    def check_count():
        if count > 5:
            setMessage("You're clicking a lot!")
    
    useEffect(check_count, [count])
    
    return (
        <div class="container">
            <h1>{message}</h1>
            <p>Count: {count}</p>
            <button onClick={lambda: setCount(count + 1)}>
                Click Me
            </button>
        </div>
    )


# 🎯 Style 5: Mixed Class + Function
class HomeComponent:
    def __init__(self, props=None):
        self.props = props or {}
    
    def render(self):
        return (
            <div class="container">
                <h1>{self.props.get("title", "Welcome")}</h1>
            </div>
        )

@class_component
class HomeClassComponent(HomeComponent):
    pass

def HomeMixed(props=None):
    component = HomeClassComponent(props)
    return component.render()


# 🎯 Style 6: With Children Components
class Card(ChildrenComponent):
    def render(self):
        return (
            <div class="p-6 bg-white rounded-lg shadow-lg">
                {self.render_children()}
            </div>
        )

class Button(ChildrenComponent):
    def render(self):
        return (
            <button 
                class={self.props.get("className", "bg-blue-500 text-white px-4 py-2 rounded")}
                onClick={self.props.get("onClick", None)}
            >
                {self.render_children()}
            </button>
        )

@component
def HomeWithChildren(props=None):
    def handle_click():
        return EventHandlers.alert("Hello from PSX!")
    
    return (
        <div class="container">
            <Card>
                <h1>Welcome to NextPy</h1>
                <Button onClick={handle_click}>
                    Click Me!
                </Button>
            </Card>
        </div>
    )


# 🎯 Style 7: Conditional Rendering
@component
def HomeWithConditional(props=None):
    is_logged_in = props.get("isLoggedIn", False)
    user_name = props.get("userName", "Guest")
    
    return (
        <div class="container">
            <h1>Welcome {user_name}!</h1>
            
            {and_condition(is_logged_in, (
                <div>
                    <a href="/dashboard">Dashboard</a>
                    <a href="/profile">Profile</a>
                </div>
            ))}
            
            {and_condition(not is_logged_in, (
                <div>
                    <a href="/login">Login</a>
                    <a href="/register">Register</a>
                </div>
            ))}
        </div>
    )


# 🎯 Style 8: Lists and Mapping
@component
def HomeWithList(props=None):
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


# 🎯 Style 9: Complex Layout
class Layout(ChildrenComponent):
    def render(self):
        return (
            <div class="min-h-screen bg-gray-100">
                <nav class="bg-white shadow">
                    <div class="px-4 mx-auto max-w-7xl">
                        <div class="flex justify-between h-16">
                            <div class="flex items-center">
                                <h1 class="text-xl font-bold text-blue-600">NextPy</h1>
                            </div>
                            <div class="flex space-x-4">
                                {self.props.get("nav_items", "")}
                            </div>
                        </div>
                    </div>
                </nav>
                
                <main class="py-6 mx-auto max-w-7xl">
                    {self.render_children()}
                </main>
            </div>
        )

@component
def Navigation(props=None):
    return (
        <div class="flex space-x-4">
            <a href="/">Home</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </div>
    )

@component
def HomeWithLayout(props=None):
    return (
        <Layout nav_items={<Navigation />}>
            <div class="text-center">
                <h1>Welcome to NextPy</h1>
                <p>Build modern web apps with Python!</p>
            </div>
        </Layout>
    )


# Reusable Components Example
@component
def UserCard(props=None):
    user = props.get("user", {})
    
    def handle_edit():
        return EventHandlers.alert(f"Editing user: {user.get('name', 'Unknown')}")
    
    return (
        <div class="border rounded-lg p-4 shadow-md">
            <h3 class="font-bold text-lg">{user.get("name", "Unknown")}</h3>
            <p class="text-gray-600">{user.get("email", "")}</p>
            <button 
                class="mt-2 bg-blue-500 text-white px-3 py-1 rounded text-sm"
                onClick={handle_edit}
            >
                Edit
            </button>
        </div>
    )

@component
def UserList(props=None):
    users = props.get("users", [])
    
    def render_user(user):
        return <UserCard user={user} />
    
    user_cards = map_list(users, render_user)
    
    return (
        <div class="container">
            <h2 class="text-2xl font-bold mb-4">Users</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {user_cards}
            </div>
        </div>
    )


# Advanced Example: Form Component
@component
def ContactForm(props=None):
    name, setName = useState("")
    email, setEmail = useState("")
    message, setMessage = useState("")
    
    def handle_submit():
        return EventHandlers.alert(f"Form submitted: {name}, {email}")
    
    return (
        <div class="max-w-md mx-auto">
            <h2 class="text-2xl font-bold mb-4">Contact Form</h2>
            <form>
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2">
                        Name:
                    </label>
                    <input 
                        type="text" 
                        value={name}
                        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        onChange={lambda e: setName(e.target.value)}
                    />
                </div>
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2">
                        Email:
                    </label>
                    <input 
                        type="email" 
                        value={email}
                        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        onChange={lambda e: setEmail(e.target.value)}
                    />
                </div>
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2">
                        Message:
                    </label>
                    <textarea 
                        value={message}
                        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-32"
                        onChange={lambda e: setMessage(e.target.value)}
                    />
                </div>
                <button 
                    type="button"
                    class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                    onClick={handle_submit}
                >
                    Submit
                </button>
            </form>
        </div>
    )


# Register components for reuse
register_component("UserCard", UserCard)
register_component("UserList", UserList)
register_component("ContactForm", ContactForm)


# Export all examples
__all__ = [
    'Home', 'HomeWithSSR', 'HomeWithHooks', 'HomeMixed', 'HomeWithChildren',
    'HomeWithConditional', 'HomeWithList', 'HomeWithLayout',
    'UserCard', 'UserList', 'ContactForm',
    'Card', 'Button', 'Layout', 'Navigation'
]
