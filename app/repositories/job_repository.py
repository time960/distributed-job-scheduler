from typing import List, Optional, Sequence
from uuid import UUID
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from app.models.job import Job, JobStatus
from datetime import datetime, timezone

class JobRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, job: Job) -> Job:
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job

    def get_by_id(self, job_id: UUID) -> Optional[Job]:
        return self.session.query(Job).filter(Job.id == job_id).first()

    def list_jobs(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        schedule_id: Optional[UUID] = None
    ) -> Sequence[Job]:
        query = self.session.query(Job)
        if status:
            query = query.filter(Job.status == status)
        if priority is not None:
            query = query.filter(Job.priority == priority)
        if schedule_id:
            query = query.filter(Job.schedule_id == schedule_id)
        return query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, job: Job) -> Job:
        self.session.commit()
        self.session.refresh(job)
        return job

    def cancel(self, job_id: UUID) -> Optional[Job]:
        job = self.get_by_id(job_id)
        if job and job.status in [JobStatus.PENDING, JobStatus.FAILED]:
            job.status = JobStatus.CANCELED
            job.updated_at = datetime.now(timezone.utc)
            self.session.commit()
            self.session.refresh(job)
            return job
        return None

    def manual_retry(self, job_id: UUID) -> Optional[Job]:
        job = self.get_by_id(job_id)
        if job and job.status in [JobStatus.FAILED, JobStatus.DEAD_LETTER]:
            job.status = JobStatus.PENDING
            job.error_message = None
            job.locked_by = None
            job.locked_at = None
            job.next_retry_at = datetime.now(timezone.utc)
            job.updated_at = datetime.now(timezone.utc)
            self.session.commit()
            self.session.refresh(job)
            return job
        return None

