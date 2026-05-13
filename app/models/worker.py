import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class WorkerStatus(str, enum.Enum):
    ACTIVE = "active"
    DEAD = "dead"
    STOPPED = "stopped"

class WorkerNode(Base):
    __tablename__ = "workers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id = Column(String, unique=True, index=True, nullable=False)
    hostname = Column(String, nullable=False)
    status = Column(Enum(WorkerStatus), default=WorkerStatus.ACTIVE, nullable=False)
    last_heartbeat_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    stopped_at = Column(DateTime(timezone=True), nullable=True)
    jobs_processed = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
