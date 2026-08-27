"""
JobHub - Logout page. Calls logout server action, then redirects to home.
"""

from nextpy.psx import component, interactive_component, useState, callServerAction, useEffect


@interactive_component
def LogoutPage(props=None):
    [logged_out, setLogged_out] = useState(False)
    [loading, setLoading] = useState(True)
    [_server_result, _setServerResult] = useState(None)

    def handle_logout():
        setLoading(True)
        callServerAction("logout", {})
        setLogged_out(True)
        setLoading(False)
        window.location.href = "/jobs"

    useEffect(handle_logout, [])

    if logged_out:
        return (
            <div class="py-16 text-center">
                <p class="text-gray-600">Logged out. Redirecting...</p>
            </div>
        )

    return (
        <div class="py-16 text-center">
            <p class="text-gray-600">Logging out...</p>
        </div>
    )


default = LogoutPage
