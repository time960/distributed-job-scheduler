from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.worker import WorkerStatus

class WorkerResponse(BaseModel):
    id: UUID
    worker_id: str
    hostname: str
    status: WorkerStatus
    last_heartbeat_at: datetime
    started_at: datetime
    stopped_at: Optional[datetime]
    jobs_processed: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
