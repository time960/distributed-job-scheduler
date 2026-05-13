from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.worker import WorkerResponse
from app.services.worker_service import WorkerService

router = APIRouter()

def get_worker_service(db: Session = Depends(get_db)) -> WorkerService:
    from app.services.worker_service import get_worker_service as get_service
    return get_service(db)

@router.get("", response_model=List[WorkerResponse])
def list_workers(skip: int = 0, limit: int = 100, service: WorkerService = Depends(get_worker_service)):
    return service.list_workers(skip, limit)

@router.get("/active", response_model=List[WorkerResponse])
def list_active_workers(skip: int = 0, limit: int = 100, service: WorkerService = Depends(get_worker_service)):
    return service.list_active_workers(skip, limit)

@router.get("/dead", response_model=List[WorkerResponse])
def list_dead_workers(skip: int = 0, limit: int = 100, service: WorkerService = Depends(get_worker_service)):
    return service.list_dead_workers(skip, limit)

@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker(worker_id: str, service: WorkerService = Depends(get_worker_service)):
    return service.get_worker(worker_id)
