from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.worker import WorkerNode, WorkerStatus

class WorkerRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self, skip: int = 0, limit: int = 100) -> List[WorkerNode]:
        return self.session.query(WorkerNode).order_by(WorkerNode.created_at.desc()).offset(skip).limit(limit).all()

    def list_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[WorkerNode]:
        return self.session.query(WorkerNode).filter(WorkerNode.status == status).order_by(WorkerNode.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_worker_id(self, worker_id: str) -> Optional[WorkerNode]:
        return self.session.query(WorkerNode).filter(WorkerNode.worker_id == worker_id).first()
