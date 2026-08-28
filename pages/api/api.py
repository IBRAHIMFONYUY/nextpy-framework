import nextpy as nx
from fastapi import HTTPException
from nextpy.db import Job


@nx.api.get("/jobs")
async def list_jobs():
    with nx.session() as db:
        jobs = db.query(Job).filter(Job.is_active == True).all()

        return [
            {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "description": job.description,
                "salary": job.salary,
            }
            for job in jobs
        ]


@nx.api.get("/jobs/{job_id}")
async def get_job(job_id: int):
    with nx.session() as db:
        job = db.get(Job, job_id)

        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")

        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "salary": job.salary,
        }


@nx.api.post("/jobs")
async def create_job(data: dict):
    with nx.session() as db:
        job = Job(
            title=data["title"],
            company=data["company"],
            location=data.get("location"),
            description=data["description"],
            salary=data.get("salary"),
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        return {"id": job.id, "message": "Job created"}


@nx.api.put("/jobs/{job_id}")
async def update_job(job_id: int, data: dict):
    with nx.session() as db:
        job = db.get(Job, job_id)

        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")

        for field in ["title", "company", "location", "description", "salary"]:
            if field in data:
                setattr(job, field, data[field])

        db.commit()

        return {"message": "Job updated"}


@nx.api.delete("/jobs/{job_id}")
async def delete_job(job_id: int):
    with nx.session() as db:
        job = db.get(Job, job_id)

        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")

        db.delete(job)
        db.commit()

        return {"message": "Job deleted"}