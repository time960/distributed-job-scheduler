from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional
from datetime import datetime
from uuid import UUID
from app.models.job import JobStatus

class JobCreate(BaseModel):
    name: str = Field(..., description="Name of the job")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Job payload")
    priority: int = Field(default=0, description="Job priority (higher is more important)")
    run_at: Optional[datetime] = Field(default=None, description="When to run the job")
    max_attempts: int = Field(default=3, description="Maximum number of retry attempts")

class JobResponse(BaseModel):
    id: UUID
    name: str
    payload: Dict[str, Any]
    status: JobStatus
    priority: int
    run_at: datetime
    attempts: int
    max_attempts: int
    locked_by: Optional[str]
    locked_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None
    next_retry_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    schedule_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
