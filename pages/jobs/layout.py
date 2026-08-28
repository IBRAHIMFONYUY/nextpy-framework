"""
JobHub - Root layout. Wraps all /jobs pages with nav + footer.
Uses useFetch to call get_me server action for auth state.
"""

from nextpy.psx import component, useFetch
from nextpy.db import get_session, User
from nextpy.auth import get_user_id_from_request


@component
def JobsLayout(props):
    children = props.get("children", "")
    me = useFetch("/__nextpy/actions/execute", {
        "method": "POST",
        "headers": {"Content-Type": "application/json", "Accept": "application/json"},
        "body": '{"action":"get_me","params":{}}',
    })
    me_key = me["_dataKey"]
    user_data = me.get("data", {})
    user = user_data.get("user") if isinstance(user_data, dict) else None

    return (
        <html lang="en">
            <head>
                <meta charset="UTF-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                <title>JobHub</title>
                <link href="/tailwind.css" rel="stylesheet" />
            </head>
            <body class="min-h-screen bg-gray-50">
                <nav class="sticky top-0 z-40 border-b border-gray-200 bg-white/80 backdrop-blur-md">
                    <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
                        <a href="/jobs" class="flex items-center gap-2 text-xl font-bold text-indigo-600">
                            JobHub
                        </a>
                        <div class="hidden items-center gap-6 text-sm font-medium text-gray-700 sm:flex">
                            <a href="/jobs" class="hover:text-indigo-600">Browse Jobs</a>
                            <a href="/jobs/dashboard" class="hover:text-indigo-600">Dashboard</a>
                        </div>
                        <div class="flex items-center gap-3">
                            {if user:
                                <span class="text-sm text-gray-600">Hi, {user.get("full_name", user.get("username", ""))}</span>
                            }
                            {if user:
                                <a href="/jobs/logout" class="rounded-md px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50">
                                    Logout
                                </a>
                            }
                            {if not user:
                                <a href="/jobs/login" class="rounded-md px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100">
                                    Log in
                                </a>
                            }
                            {if not user:
                                <a href="/jobs/register" class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">
                                    Sign up
                                </a>
                            }
                        </div>
                    </div>
                </nav>
                <main class="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                    {children}
                </main>
                <footer class="mt-16 border-t border-gray-200 bg-white">
                    <div class="mx-auto max-w-7xl px-4 py-8 text-center text-sm text-gray-500">
                        Built with NextPyVision - JobHub
                    </div>
                </footer>
            </body>
        </html>
    )


def getServerSideProps(context):
    return {"props": {}}


default = JobsLayout
