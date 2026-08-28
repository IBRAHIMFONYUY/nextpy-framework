"""
CrudEventLog Component
useCrudEvent demo - listens for CRUD events and displays a live log
of create/update/delete operations.
"""



from nextpy.psx import component, useCrudEvent


@component
def CrudEventLog(props=None):
    event = useCrudEvent(resource="todos")
    event_key = event["_eventKey"]

    return(
        <div class="p-6 bg-white rounded-lg shadow">
            <h3 class="mb-3 font-semibold text-gray-900">Event Log (useCrudEvent)</h3>
            <p class="mb-4 text-sm text-gray-500">
                Listens for <code>nextpy:crud:changed</code> events via <code>useCrudEvent</code>
            </p>
            <div data-bind="textContent:{event_key}" class="text-sm text-gray-600">
                No events yet. Try adding, toggling, or deleting a todo above.
            </div>
        </div>
    )
default=CrudEventLog
