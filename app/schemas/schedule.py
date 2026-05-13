from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime

class ScheduleCreate(BaseModel):
    name: str
    cron_expression: str = Field(..., description="A standard cron expression")
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=0)
    max_attempts: int = Field(default=3)
    is_active: bool = Field(default=True)

class ScheduleResponse(BaseModel):
    id: UUID
    name: str
    cron_expression: str
    payload: Dict[str, Any]
    priority: int
    max_attempts: int
    is_active: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
