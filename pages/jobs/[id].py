from nextpy.psx import component, Link
from nextpy.db import get_session, Job


@component
def JobDetailsPage(props=None):
    job = (props or {}).get("job")
    
    

    

    return (
        <main class="max-w-3xl px-6 py-12 mx-auto">
            <h1 class="text-4xl font-bold">{job["title"]}</h1>
            <p class="text-xl">{job["company"]}</p>
            <p>{job["location"]}</p>
            <p class="mt-6">{job["description"]}</p>
            <p class="mt-4 font-semibold">{job["salary"]}</p>

            <Link href="/jobs/{job["id"]}/apply">
                Apply now
            </Link>
        </main>
    )


def getServerSideProps(context):
    job_id = int(context["params"]["id"])

    with get_session() as session:
        

        job = session.get(Job, job_id)

        if not job:
            return {"not_found": True}

        data = {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "salary": job.salary,
        }

    return {"props": {"job": data}}


default = JobDetailsPage