"""
JobHub — Browse / search jobs page. Uses useFetch + useCrudEvent.
"""

from nextpy.psx import component, useFetch, useCrudEvent


@component
def JobsBrowse(props=None):
    props = props or {}
    search = props.get("search", "")
    job_type = props.get("job_type", "")
    experience_level = props.get("experience_level", "")

    params = {}
    if search: params["search"] = search
    if job_type: params["job_type"] = job_type
    if experience_level: params["experience_level"] = experience_level

    import json
    body = json.dumps({"action": "list_jobs", "params": params})

    jobs_data = useFetch("/__nextpy/actions/execute", {
        "method": "POST",
        "headers": {"Content-Type": "application/json", "Accept": "application/json"},
        "body": body,
    })
    jobs_key = jobs_data["_dataKey"]
    jobs = jobs_data.get("data", [])
    if isinstance(jobs, dict) and "data" in jobs:
        jobs = jobs["data"]
    if not isinstance(jobs, list):
        jobs = []

    event = useCrudEvent(resource="jobs")
    event_key = event["_eventKey"]

    JOB_TYPES = [
        ("", "All Types"),
        ("full_time", "Full-time"),
        ("part_time", "Part-time"),
        ("contract", "Contract"),
        ("internship", "Internship"),
    ]
    LEVELS = [
        ("", "All Levels"),
        ("entry", "Entry"),
        ("mid", "Mid"),
        ("senior", "Senior"),
        ("lead", "Lead"),
    ]

    def job_type_label(jt):
        labels = {"full_time": "Full-time", "part_time": "Part-time", "contract": "Contract", "internship": "Internship"}
        return labels.get(jt, jt)

    job_type_options = "".join(
        f'<option value="{val}" {"selected" if val == job_type else ""}>{label}</option>'
        for val, label in JOB_TYPES
    )
    level_options = "".join(
        f'<option value="{val}" {"selected" if val == experience_level else ""}>{label}</option>'
        for val, label in LEVELS
    )

    return (
        <div>
            <div class="mb-8">
                <h1 class="text-3xl font-bold text-gray-900">Browse Jobs</h1>
                <p class="mt-1 text-gray-600">{len(jobs)} positions available</p>
            </div>

            <form method="GET" action="/jobs/browse" class="p-6 mb-8 bg-white border border-gray-200 shadow-sm rounded-xl">
                <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <div class="sm:col-span-2">
                        <label class="block mb-1 text-sm font-medium text-gray-700">Search</label>
                        <input name="search"  placeholder="Job title, company..."
                            class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
                    </div>
                    <div>
                        <label class="block mb-1 text-sm font-medium text-gray-700">Job Type</label>
                        <select name="job_type"
                            class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20">
                            {job_type_options}
                        </select>
                    </div>
                    <div>
                        <label class="block mb-1 text-sm font-medium text-gray-700">Experience</label>
                        <select name="experience_level"
                            class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20">
                            {level_options}
                        </select>
                    </div>
                </div>
                <div class="flex items-center gap-3 mt-4">
                    <button type="submit" class="rounded-lg bg-indigo-600 px-5 py-2.5 font-semibold text-white hover:bg-indigo-700">Search</button>
                    <a href="/jobs/browse" class="rounded-lg px-5 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-100">Clear filters</a>
                </div>
            </form>

            {if len(jobs) == 0:
                <div class="p-12 text-center bg-white border border-gray-300 border-dashed rounded-xl">
                    <p class="text-lg font-medium text-gray-500">No jobs match your filters.</p>
                    <a href="/jobs/browse" class="inline-block mt-3 text-sm font-medium text-indigo-600 hover:text-indigo-500">Clear filters</a>
                </div>
            }

            <div class="space-y-4">
                {for job in jobs:
                    <a href={f"/jobs/{job['id']}"}
                        class="block p-6 transition bg-white border border-gray-200 shadow-sm group rounded-xl hover:shadow-md hover:border-indigo-300">
                        <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                            <div class="flex-1">
                                <div class="flex flex-wrap items-center gap-2 mb-2">
                                    <span class="inline-block rounded-full bg-indigo-100 px-2.5 py-0.5 text-xs font-medium text-indigo-700">
                                        {job_type_label(job.get("job_type", "full_time"))}
                                    </span>
                                    <span class="inline-block rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700">
                                        {job.get("experience_level", "mid").title()}
                                    </span>
                                </div>
                                <h3 class="text-lg font-semibold text-gray-900 group-hover:text-indigo-600">{job["title"]}</h3>
                                <p class="mt-1 text-sm text-gray-600">{job["company"]}</p>
                                <p class="mt-2 text-sm text-gray-500 line-clamp-2">{job.get("description", "")[:150]}</p>
                            </div>
                            <div class="flex flex-col items-end gap-2 text-sm text-gray-500 sm:min-w-[140px]">
                                <span>{job.get("location") or "Remote"}</span>
                            </div>
                        </div>
                    </a>
                }
            </div>
        </div>
    )


def getServerSideProps(context):
    query_params = context.get("query", {})
    return {
        "props": {
            "search": query_params.get("search", ""),
            "job_type": query_params.get("job_type", ""),
            "experience_level": query_params.get("experience_level", ""),
        }
    }


default = JobsBrowse
