from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Sequence
from uuid import UUID

from app.database import get_db
from app.schemas.job import JobCreate, JobResponse
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])

def get_job_service(session: Session = Depends(get_db)) -> JobService:
    repository = JobRepository(session)
    return JobService(repository)

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_in: JobCreate, service: JobService = Depends(get_job_service)):
    return service.create_job(job_in)

@router.get("", response_model=List[JobResponse])
def list_jobs(
    status: Optional[str] = None,
    priority: Optional[int] = None,
    schedule_id: Optional[UUID] = None,
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    service: JobService = Depends(get_job_service)
):
    return service.list_jobs(status=status, priority=priority, schedule_id=schedule_id, skip=skip, limit=limit)

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: UUID, service: JobService = Depends(get_job_service)):
    return service.get_job(job_id)

@router.post("/{job_id}/cancel", response_model=JobResponse)
def cancel_job(job_id: UUID, service: JobService = Depends(get_job_service)):
    return service.cancel_job(job_id)

@router.post("/{job_id}/retry", response_model=JobResponse)
def retry_job(job_id: UUID, service: JobService = Depends(get_job_service)):
    return service.retry_job(job_id)

