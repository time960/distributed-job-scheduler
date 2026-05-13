from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate

class ScheduleRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, schedule_in: ScheduleCreate, next_run_at) -> Schedule:
        db_schedule = Schedule(
            name=schedule_in.name,
            cron_expression=schedule_in.cron_expression,
            payload=schedule_in.payload,
            priority=schedule_in.priority,
            max_attempts=schedule_in.max_attempts,
            is_active=schedule_in.is_active,
            next_run_at=next_run_at
        )
        self.session.add(db_schedule)
        self.session.commit()
        self.session.refresh(db_schedule)
        return db_schedule

    def get_by_id(self, schedule_id: UUID) -> Optional[Schedule]:
        return self.session.query(Schedule).filter(Schedule.id == schedule_id).first()

    def list(self, skip: int = 0, limit: int = 100) -> List[Schedule]:
        return self.session.query(Schedule).order_by(Schedule.created_at.desc()).offset(skip).limit(limit).all()

    def set_active(self, schedule_id: UUID, is_active: bool) -> Optional[Schedule]:
        schedule = self.get_by_id(schedule_id)
        if schedule:
            schedule.is_active = is_active
            self.session.commit()
            self.session.refresh(schedule)
            return schedule
        return None

    def delete(self, schedule_id: UUID) -> bool:
        schedule = self.get_by_id(schedule_id)
        if schedule:
            self.session.delete(schedule)
            self.session.commit()
            return True
        return False
