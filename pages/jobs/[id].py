"""
JobHub - Job detail page (/jobs/[id]). Uses interactive_component + callServerAction.
"""

from nextpy.psx import interactive_component, useState, callServerAction


@interactive_component
def JobDetailPage(props=None):
    props = props or {}
    job = props.get("job")
    employer = props.get("employer")
    is_owner = props.get("is_owner", False)
    already_applied = props.get("already_applied", False)
    is_authenticated = props.get("is_authenticated", False)
    application_count = props.get("application_count", 0)

    [showModal, setShowModal] = useState(False)
    [coverLetter, setCoverLetter] = useState("")
    [applying, setApplying] = useState(False)
    [done, setDone] = useState(False)
    [error, setError] = useState("")
    [_server_result, _setServerResult] = useState(None)

    def handle_apply(e):
        setApplying(True)
        setError("")
        callServerAction("apply_to_job", {"job_id": job["id"] if job else 0, "cover_letter": coverLetter})
        if _server_result and _server_result.get("success"):
            setDone(True)
            setShowModal(False)
        else:
            setError(_server_result.get("error", "Failed to apply.") if _server_result else "Failed to apply.")
            setApplying(False)

    if job is None:
        return (
            <div class="py-16 text-center">
                <h1 class="text-2xl font-bold text-gray-900">Job not found</h1>
                <a href="/jobs/browse" class="mt-4 inline-block text-indigo-600 hover:text-indigo-500">Browse all jobs</a>
            </div>
        )

    JOB_TYPES = {"full_time": "Full-time", "part_time": "Part-time", "contract": "Contract", "internship": "Internship"}

    return (
        <div class="mx-auto max-w-4xl">
            <a href="/jobs/browse" class="mb-6 inline-flex items-center gap-1 text-sm font-medium text-gray-500 hover:text-indigo-600">Back to jobs</a>

            <div class="rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
                <div class="mb-4 flex flex-wrap items-center gap-2">
                    <span class="rounded-full bg-indigo-100 px-3 py-1 text-xs font-medium text-indigo-700">
                        {JOB_TYPES.get(job["job_type"], job["job_type"])}
                    </span>
                    <span class="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
                        {job.get("experience_level", "mid").title()}
                    </span>
                </div>

                <h1 class="text-3xl font-bold text-gray-900">{job["title"]}</h1>
                <p class="mt-2 text-lg text-gray-600">{job["company"]}</p>

                <div class="mt-4 flex flex-wrap items-center gap-6 text-sm text-gray-500">
                    <span>{job.get("location") or "Remote"}</span>
                    <span>Posted {job.get("created_at", "")[:10]}</span>
                </div>

                <hr class="my-6" />

                <div class="prose max-w-none text-gray-700">
                    <h3 class="text-lg font-semibold text-gray-900">Job Description</h3>
                    <div class="mt-3 whitespace-pre-line leading-relaxed">{job["description"]}</div>
                </div>

                {if employer:
                    <div class="mt-8 rounded-lg bg-gray-50 p-6">
                        <h3 class="mb-2 text-sm font-semibold text-gray-900">About the Employer</h3>
                        <p class="text-sm text-gray-600">{employer["full_name"]}</p>
                        {if employer.get("company_name"):
                            <p class="text-sm text-gray-500">{employer["company_name"]}</p>
                        }
                        {if employer.get("bio"):
                            <p class="mt-2 text-sm text-gray-600">{employer["bio"]}</p>
                        }
                    </div>
                }

                <div class="mt-8">
                    {if is_owner:
                        <div class="rounded-lg bg-blue-50 p-4">
                            <p class="mb-2 text-sm font-medium text-blue-700">
                                This is your job listing ({application_count} application{"s" if application_count != 1 else ""}).
                            </p>
                            <a href="/jobs/dashboard" class="text-sm font-medium text-blue-600 hover:text-blue-500">Manage in Dashboard</a>
                        </div>
                    }

                    {if (not is_owner) and is_authenticated:
                        {if not showModal and (not done) and (not already_applied):
                            <button onclick={lambda e: setShowModal(True)}
                                class="w-full rounded-lg bg-indigo-600 px-6 py-3 font-semibold text-white hover:bg-indigo-700">
                                Apply Now
                            </button>
                        }

                        {if already_applied and (not done):
                            <div class="rounded-lg bg-green-50 p-4 text-center text-sm font-medium text-green-700">
                                You already applied to this job.
                            </div>
                        }

                        {if done:
                            <div class="rounded-lg bg-green-50 p-4 text-center text-sm font-medium text-green-700">
                                Application submitted!
                            </div>
                        }

                        {if showModal:
                            <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
                                <div class="w-full max-w-lg rounded-xl bg-white p-6 shadow-2xl">
                                    <h3 class="mb-4 text-lg font-semibold text-gray-900">Apply to this job</h3>
                                    {if error:
                                        <div class="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
                                    }
                                    <div class="mb-4">
                                        <label class="mb-1 block text-sm font-medium text-gray-700">Cover letter (optional)</label>
                                        <textarea rows="5" value={coverLetter} oninput={lambda e: setCoverLetter(e.target.value)}
                                            placeholder="Tell the employer why you're a great fit..."
                                            class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-gray-900 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20">
                                        </textarea>
                                    </div>
                                    <div class="flex justify-end gap-3">
                                        <button onclick={lambda e: setShowModal(False)}
                                            class="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100">Cancel</button>
                                        <button onclick={handle_apply} disabled={applying}
                                            class="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50">
                                            {if applying: "Submitting..."}
                                            {if not applying: "Submit Application"}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        }
                    }

                    {if not is_authenticated:
                        <div class="rounded-lg bg-gray-50 p-4 text-center text-sm text-gray-600">
                            <a href="/jobs/login" class="font-medium text-indigo-600 hover:text-indigo-500">Log in</a>
                            {" "}to apply to this job.
                        </div>
                    }
                </div>
            </div>
        </div>
    )


def getServerSideProps(context):
    from nextpy.db import get_session, Job, User, Application
    from nextpy.auth import get_user_id_from_request

    params = context.get("params", {})
    job_id = params.get("id")
    if not job_id:
        return {"props": {"job": None}}

    db = get_session()
    try:
        job = db.query(Job).filter(Job.id == int(job_id), Job.is_active == True).first()
        if job is None:
            return {"props": {"job": None}}

        employer = db.query(User).filter(User.id == job.employer_id).first() if job.employer_id else None

        request = context.get("request")
        user_id = get_user_id_from_request(request) if request else None
        is_owner = user_id is not None and job.employer_id == user_id

        already_applied = False
        if user_id and not is_owner:
            already_applied = (
                db.query(Application)
                .filter(Application.job_id == job.id, Application.applicant_id == user_id)
                .first()
            ) is not None

        application_count = db.query(Application).filter(Application.job_id == job.id).count() if is_owner else 0

        return {
            "props": {
                "job": {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "location": job.location or "",
                    "description": job.description or "",
                    "job_type": job.job_type or "full_time",
                    "experience_level": job.experience_level or "mid",
                    "employer_id": job.employer_id,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                },
                "employer": {
                    "full_name": employer.full_name,
                    "company_name": employer.company_name or "",
                    "bio": employer.bio or "",
                } if employer else None,
                "is_owner": is_owner,
                "is_authenticated": user_id is not None,
                "already_applied": already_applied,
                "application_count": application_count,
            }
        }
    finally:
        db.close()


default = JobDetailPage
