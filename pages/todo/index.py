"""Realtime todo application page."""

from nextpy.psx import component


@component
def TodoPage(props=None):
    return (
        <main class="min-h-screen bg-slate-100 px-4 py-12 text-slate-900">
            <section class="mx-auto max-w-2xl rounded-xl bg-white p-6 shadow-sm">
                <div class="mb-6 flex items-center justify-between">
                    <div>
                        <p class="text-sm font-semibold uppercase tracking-wide text-blue-600">NextPy</p>
                        <h1 class="text-3xl font-bold">Shared Todos</h1>
                    </div>
                    <span id="todo-status" class="text-sm text-slate-500">Connecting...</span>
                </div>
                <form id="todo-form" class="mb-6 flex gap-2">
                    <input id="todo-title" name="title" required maxlength="255" placeholder="What needs doing?" class="min-w-0 flex-1 rounded-lg border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none" />
                    <button type="submit" class="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700">Add</button>
                </form>
                <p id="todo-error" class="mb-4 hidden rounded-lg bg-red-50 p-3 text-sm text-red-700"></p>
                <ul id="todo-list" class="space-y-2"></ul>
                <p id="todo-empty" class="py-8 text-center text-slate-500">Loading todos...</p>
            </section>
            <script src="/static/todo.js"></script>
        </main>
    )


def getServerSideProps(context):
    return {"props": {"title": "Shared Todos"}}


def get_template():
    return "todo/index.html"


def default(props=None):
    return TodoPage(props)
