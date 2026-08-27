"""
JobHub - Create job listing page. Uses interactive_component with callServerAction.
"""

from nextpy.psx import component, interactive_component, useState, callServerAction


@interactive_component
def CreateJobForm(props=None):
    [title, setTitle] = useState("")
    [company, setCompany] = useState("")
    [location, setLocation] = useState("")
    [description, setDescription] = useState("")
    [salaryMin, setSalaryMin] = useState("")
    [salaryMax, setSalaryMax] = useState("")
    [jobType, setJobType] = useState("full_time")
    [experienceLevel, setExperienceLevel] = useState("mid")
    [error, setError] = useState("")
    [loading, setLoading] = useState(False)
    [_server_result, _setServerResult] = useState(None)

    def handle_create(e):
        setLoading(True)
        setError("")
        params = {
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "salary_min": int(salaryMin) if salaryMin else 0,
            "salary_max": int(salaryMax) if salaryMax else 0,
            "job_type": jobType,
            "experience_level": experienceLevel,
        }
        callServerAction("create_job", params)
        if _server_result and _server_result.get("success"):
            window.location.href = "/jobs/dashboard"
        else:
            setError(_server_result.get("error", "Failed to create job.") if _server_result else "Failed to create job.")
            setLoading(False)

    return (
        <div class="max-w-2xl mx-auto">
            <div class="mb-8">
                <h1 class="text-3xl font-bold text-gray-900">Post a New Job</h1>
                <p class="mt-1 text-gray-600">Fill out the details below to list your job opening.</p>
            </div>
            <div class="p-8 bg-white border border-gray-200 shadow-sm rounded-xl">
                {if error:
                    <div class="p-3 mb-4 text-sm text-red-700 rounded-lg bg-red-50">{error}</div>
                }
                <form onsubmit={handle_create} class="space-y-6">
                    <div class="grid gap-6 sm:grid-cols-2">
                        <div class="sm:col-span-2">
                            <label class="block mb-1 text-sm font-medium text-gray-700">Job Title *</label>
                            <input type="text" value={title} oninput={lambda e: setTitle(e.target.value)}
                                required placeholder="e.g. Senior React Developer"
                                class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
                        </div>
                        <div>
                            <label class="block mb-1 text-sm font-medium text-gray-700">Company *</label>
                            <input type="text" value={company} oninput={lambda e: setCompany(e.target.value)}
                                required placeholder="e.g. Acme Corp"
                                class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
                        </div>
                        <div>
                            <label class="block mb-1 text-sm font-medium text-gray-700">Location</label>
                            <input type="text" value={location} oninput={lambda e: setLocation(e.target.value)}
                                placeholder="e.g. New York, NY or Remote"
                                class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
                        </div>
                        <div>
                            <label class="block mb-1 text-sm font-medium text-gray-700">Job Type</label>
                            <select value={jobType} oninput={lambda e: setJobType(e.target.value)}
                                class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20">
                                <option value="full_time">Full-time</option>
                                <option value="part_time">Part-time</option>
                                <option value="contract">Contract</option>
                                <option value="internship">Internship</option>
                            </select>
                        </div>
                        <div>
                            <label class="block mb-1 text-sm font-medium text-gray-700">Experience Level</label>
                            <select value={experienceLevel} oninput={lambda e: setExperienceLevel(e.target.value)}
                                class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20">
                                <option value="entry">Entry Level</option>
                                <option value="mid">Mid Level</option>
                                <option value="senior">Senior Level</option>
                                <option value="lead">Lead / Principal</option>
                            </select>
                        </div>
                        <div>
                            <label class="block mb-1 text-sm font-medium text-gray-700">Min Salary ($)</label>
                            <input type="number" value={salaryMin} oninput={lambda e: setSalaryMin(e.target.value)}
                                min="0" placeholder="e.g. 50000"
                                class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
                        </div>
                        <div>
                            <label class="block mb-1 text-sm font-medium text-gray-700">Max Salary ($)</label>
                            <input type="number" value={salaryMax} oninput={lambda e: setSalaryMax(e.target.value)}
                                min="0" placeholder="e.g. 90000"
                                class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
                        </div>
                    </div>
                    <div>
                        <label class="block mb-1 text-sm font-medium text-gray-700">Job Description *</label>
                        <textarea rows="8" value={description} oninput={lambda e: setDescription(e.target.value)}
                            required placeholder="Describe the role, responsibilities, requirements, and benefits..."
                            class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20">
                        </textarea>
                    </div>
                    <div class="flex items-center gap-4">
                        <button type="submit"
                            class="px-6 py-3 font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50">
                            <p>Publish</p>
                        </button>
                        <a href="/jobs/dashboard" class="text-sm font-medium text-gray-600 hover:text-gray-800">Cancel</a>
                    </div>
                </form>
            </div>
        </div>
    )


default = CreateJobForm
