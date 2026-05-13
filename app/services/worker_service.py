from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.repositories.worker_repository import WorkerRepository
from app.models.worker import WorkerNode, WorkerStatus

class WorkerService:
    def __init__(self, session: Session):
        self.repository = WorkerRepository(session)

    def list_workers(self, skip: int = 0, limit: int = 100) -> List[WorkerNode]:
        return self.repository.list(skip, limit)

    def list_active_workers(self, skip: int = 0, limit: int = 100) -> List[WorkerNode]:
        return self.repository.list_by_status(WorkerStatus.ACTIVE.name, skip, limit)

    def list_dead_workers(self, skip: int = 0, limit: int = 100) -> List[WorkerNode]:
        return self.repository.list_by_status(WorkerStatus.DEAD.name, skip, limit)

    def get_worker(self, worker_id: str) -> WorkerNode:
        worker = self.repository.get_by_worker_id(worker_id)
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        return worker

def get_worker_service(session: Session) -> WorkerService:
    return WorkerService(session)
