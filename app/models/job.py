import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Enum, JSON, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"
    DEAD_LETTER = "dead_letter"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    payload = Column(JSON, nullable=False, default=dict)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, index=True, nullable=False)
    priority = Column(Integer, default=0, index=True, nullable=False)
    run_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)
    locked_by = Column(String, nullable=True)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    error_message = Column(String, nullable=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("schedules.id"), nullable=True, index=True)
    scheduled_for = Column(DateTime(timezone=True), nullable=True, index=True)

    __table_args__ = (
        UniqueConstraint('schedule_id', 'scheduled_for', name='uq_job_schedule_time'),
        Index('idx_jobs_polling', 'status', 'run_at', 'next_retry_at', 'priority'),
    )
