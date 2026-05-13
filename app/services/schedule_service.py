from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from croniter import croniter
from datetime import datetime, timezone
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.schedule import ScheduleCreate
from app.models.schedule import Schedule

class ScheduleService:
    def __init__(self, session: Session):
        self.repository = ScheduleRepository(session)

    def _calculate_next_run(self, cron_expression: str) -> datetime:
        try:
            now = datetime.now(timezone.utc)
            cron = croniter(cron_expression, now)
            return cron.get_next(datetime)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid cron expression: {e}")

    def create_schedule(self, schedule_in: ScheduleCreate) -> Schedule:
        next_run = self._calculate_next_run(schedule_in.cron_expression)
        return self.repository.create(schedule_in, next_run)

    def get_schedule(self, schedule_id: UUID) -> Schedule:
        schedule = self.repository.get_by_id(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return schedule

    def list_schedules(self, skip: int = 0, limit: int = 100) -> List[Schedule]:
        return self.repository.list(skip, limit)

    def pause_schedule(self, schedule_id: UUID) -> Schedule:
        schedule = self.repository.set_active(schedule_id, False)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return schedule

    def resume_schedule(self, schedule_id: UUID) -> Schedule:
        schedule = self.repository.set_active(schedule_id, True)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return schedule

    def delete_schedule(self, schedule_id: UUID) -> None:
        if not self.repository.delete(schedule_id):
            raise HTTPException(status_code=404, detail="Schedule not found")

def get_schedule_service(session: Session) -> ScheduleService:
    return ScheduleService(session)
