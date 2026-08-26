from nextpy import component, Link, get_session, useFetch, fetch_api
from nextpy.db import Job, User



@component
def JobsPage(props=None):
    props = props or {}
    jobs = props.get("jobs", [])
    users = props.get('users', [])

    return (
        <main class="max-w-5xl px-6 py-12 mx-auto">
            <h1 class="mb-8 text-4xl font-bold">Available Jobs</h1>

            <div class="grid gap-6">
                {for job in jobs:
                    <article class="p-6 border shadow-sm rounded-xl">
                        <h2 class="text-2xl font-semibold">{job["title"]}</h2>
                        <p class="text-gray-600">{job["company"]}</p>
                        <p class="text-gray-500">{job["location"]}</p>
                        <p class="mt-4">{job["description"]}</p>

                        <Link href="/jobs/{job["id"]}"
                            className="inline-block mt-4 text-blue-600"
                        >
                            View job</Link>
                    </article>
    
                }
                {if users:
                    {for user in users:
                        <article class="p-6 border shadow-sm rounded-xl">
                                                <h2 class="text-2xl font-semibold">{user["username"]}</h2>
                                                    <p class="text-gray-600">{user["email"]}</p>
                                                <Link href="/users/{user["id"]}"
                                                    className="inline-block mt-4 text-blue-600"
                                                >
                                                    View job</Link>
                                            </article>   
                    }
                {else:
                    <p>no usera..</p>    
                }
            </div>
        </main>
    )


def getServerSideProps(context):
    
        session=get_session()
        users= [
             {
                 "id":user.id,
                 "email":user.email,
                 "username":user.username
             }
             for user in session.query(User)
         ]
        

        jobs = [
            {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "description": job.description,
            }
            for job in session.query(Job).order_by(Job.created_at.desc()).all()
                
        ]

        return {"props": {"jobs": jobs, "users":users}}


default = JobsPage