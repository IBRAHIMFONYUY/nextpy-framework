"""
JobHub - Dashboard page. Uses useFetch + useCrudEvent + callServerAction.
Employer sees their posted jobs + applications. Job seeker sees their applications.
"""

from nextpy.psx import interactive_component, useState, callServerAction, useFetch, useCrudEvent


@interactive_component
def DashboardPage(props=None):
    me_data = useFetch("/__nextpy/actions/execute", {
        "method": "POST",
        "headers": {"Content-Type": "application/json", "Accept": "application/json"},
        "body": '{"action":"get_me","params":{}}',
    })
    me = me_data.get("data") or {}
    user = me.get("user") if isinstance(me, dict) else None

    is_employer = user and user.get("role") == "employer"

    jobs_data = useFetch("/__nextpy/actions/execute", {
        "method": "POST",
        "headers": {"Content-Type": "application/json", "Accept": "application/json"},
        "body": '{"action":"get_my_jobs","params":{}}',
    })
    my_jobs = jobs_data.get("data", []) or []
    if isinstance(my_jobs, dict) and "data" in my_jobs:
        my_jobs = my_jobs["data"]
    if not isinstance(my_jobs, list):
        my_jobs = []

    apps_data = useFetch("/__nextpy/actions/execute", {
        "method": "POST",
        "headers": {"Content-Type": "application/json", "Accept": "application/json"},
        "body": '{"action":"get_my_applications","params":{}}',
    })
    my_apps = apps_data.get("data", []) or []
    if isinstance(my_apps, dict) and "data" in my_apps:
        my_apps = my_apps["data"]
    if not isinstance(my_apps, list):
        my_apps = []

    [confirming_delete, setConfirmingDelete] = useState(0)
    [deleting, setDeleting] = useState(False)

    def handle_delete_job(job_id):
        setDeleting(True)
        callServerAction("delete_job", {"job_id": job_id})
        window.spaReload()

    def handle_update_status(app_id, new_status):
        callServerAction("update_application_status", {"application_id": app_id, "status": new_status})
        window.spaReload()

    return (
        <div>
            {if not user:
                <div class="py-16 text-center">
                    <h1 class="text-2xl font-bold text-gray-900">Please log in</h1>
                    <a href="/jobs/login" class="inline-block mt-4 text-indigo-600 hover:text-indigo-500">Go to login</a>
                </div>
            }

            {if user:
                <div>
                    <div class="mb-8">
                        <h1 class="text-3xl font-bold text-gray-900">
                            Welcome, {user.get("full_name", user.get("username", ""))}
                        </h1>
                        <p class="mt-1 text-gray-600">
                            {("Employer Dashboard" if is_employer else "Job Seeker Dashboard")}
                            {" - "}
                            {user.get("email", "")}
                        </p>
                    </div>

                    {if is_employer:
                        <section>
                            <div class="flex items-center justify-between mb-6">
                                <h2 class="text-xl font-semibold text-gray-900">My Job Listings</h2>
                                <a href="/jobs/create" class="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700">
                                    + Post a Job
                                </a>
                            </div>

                            {if len(my_jobs) == 0:
                                <div class="p-12 text-center bg-white border border-gray-300 border-dashed rounded-xl">
                                    <p class="text-gray-500">You haven't posted any jobs yet.</p>
                                    <a href="/jobs/create" class="inline-block mt-3 text-sm font-medium text-indigo-600">Post your first job</a>
                                </div>
                            }

                            <div class="space-y-4">
                                {for job in my_jobs:
                                    <div class="p-6 bg-white border border-gray-200 shadow-sm rounded-xl">
                                        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                                            <div class="flex-1">
                                                <div class="flex items-center gap-2">
                                                    <h3 class="font-semibold text-gray-900">
                                                        <a href={f"/jobs/{job['id']}"} class="hover:text-indigo-600">{job["title"]}</a>
                                                    </h3>
                                                    <span class={"rounded-full px-2 py-0.5 text-xs font-medium " + (
                                                        "bg-green-100 text-green-700" if job.get("is_active") else "bg-gray-100 text-gray-500"
                                                    )}>
                                                        {"Active" if job.get("is_active") else "Closed"}
                                                    </span>
                                                </div>
                                                <p class="mt-1 text-sm text-gray-500">{job["company"]} - {job.get("location") or "Remote"}</p>
                                            </div>
                                            <div class="flex items-center gap-3">
                                                <span class="text-sm text-gray-500">
                                                    {job.get("app_count", 0)} application{"s" if job.get("app_count", 0) != 1 else ""}
                                                </span>
                                                {if job.get("is_active"):
                                                    <button onclick={lambda e, jid=job["id"]: setConfirmingDelete(jid)} class="text-sm font-medium text-red-600 hover:text-red-800">
                                                        Delete
                                                    </button>
                                                }
                                            </div>
                                        </div>
                                    </div>
                                }
                            </div>
                        </section>
                    }

                    {if not is_employer:
                        <section>
                            <h2 class="mb-6 text-xl font-semibold text-gray-900">My Applications</h2>

                            {if len(my_apps) == 0:
                                <div class="p-12 text-center bg-white border border-gray-300 border-dashed rounded-xl">
                                    <p class="text-gray-500">You haven't applied to any jobs yet.</p>
                                    <a href="/jobs/browse" class="inline-block mt-3 text-sm font-medium text-indigo-600">Browse jobs</a>
                                </div>
                            }

                            <div class="space-y-3">
                                {for app in my_apps:
                                    <div class="flex items-center justify-between p-5 bg-white border border-gray-200 shadow-sm rounded-xl">
                                        <div>
                                            {if app.get("job"):
                                                <a href={f"/jobs/{app['job']['id']}"} class="font-semibold text-gray-900 hover:text-indigo-600">
                                                    {app["job"]["title"]}
                                                </a>
                                            }
                                            <p class="text-sm text-gray-500">
                                                {app.get("job", {}).get("company", "")}
                                                {" - Applied "}
                                                {(app.get("created_at") or "")[:10]}
                                            </p>
                                        </div>
                                        <span class={"rounded-full px-3 py-1 text-xs font-medium " + (
                                            "bg-yellow-100 text-yellow-700" if app["status"] == "pending"
                                            else "bg-green-100 text-green-700" if app["status"] == "accepted"
                                            else "bg-red-100 text-red-700"
                                        )}>
                                            {app["status"].title()}
                                        </span>
                                    </div>
                                }
                            </div>
                        </section>
                    }
                </div>
            }
        </div>
    )


default = DashboardPage
