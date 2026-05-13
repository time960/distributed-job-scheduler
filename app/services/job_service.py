from typing import List, Optional, Sequence
from uuid import UUID
from fastapi import HTTPException
from app.models.job import Job, JobStatus
from app.schemas.job import JobCreate
from app.repositories.job_repository import JobRepository
from datetime import datetime, timezone

class JobService:
    def __init__(self, repository: JobRepository):
        self.repository = repository

    def create_job(self, job_in: JobCreate) -> Job:
        job = Job(
            name=job_in.name,
            payload=job_in.payload,
            priority=job_in.priority,
            run_at=job_in.run_at or datetime.now(timezone.utc),
            max_attempts=job_in.max_attempts
        )
        return self.repository.create(job)

    def get_job(self, job_id: UUID) -> Job:
        job = self.repository.get_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job

    def list_jobs(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        schedule_id: Optional[UUID] = None
    ) -> Sequence[Job]:
        return self.repository.list_jobs(
            skip=skip,
            limit=limit,
            status=status,
            priority=priority,
            schedule_id=schedule_id
        )

    def cancel_job(self, job_id: UUID) -> Job:
        job = self.repository.cancel(job_id)
        if not job:
            raise HTTPException(status_code=400, detail="Job cannot be canceled or not found")
        return job

    def retry_job(self, job_id: UUID) -> Job:
        job = self.repository.manual_retry(job_id)
        if not job:
            raise HTTPException(status_code=400, detail="Job cannot be retried or not found")
        return job

