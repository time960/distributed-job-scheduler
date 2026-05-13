from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.database import get_db
from app.schemas.schedule import ScheduleCreate, ScheduleResponse
from app.services.schedule_service import ScheduleService

router = APIRouter()

def get_schedule_service(db: Session = Depends(get_db)) -> ScheduleService:
    from app.services.schedule_service import get_schedule_service as get_service
    return get_service(db)

@router.post("", response_model=ScheduleResponse, status_code=201)
def create_schedule(schedule_in: ScheduleCreate, service: ScheduleService = Depends(get_schedule_service)):
    return service.create_schedule(schedule_in)

@router.get("", response_model=List[ScheduleResponse])
def list_schedules(skip: int = 0, limit: int = 100, service: ScheduleService = Depends(get_schedule_service)):
    return service.list_schedules(skip, limit)

@router.get("/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(schedule_id: UUID, service: ScheduleService = Depends(get_schedule_service)):
    return service.get_schedule(schedule_id)

@router.post("/{schedule_id}/pause", response_model=ScheduleResponse)
def pause_schedule(schedule_id: UUID, service: ScheduleService = Depends(get_schedule_service)):
    return service.pause_schedule(schedule_id)

@router.post("/{schedule_id}/resume", response_model=ScheduleResponse)
def resume_schedule(schedule_id: UUID, service: ScheduleService = Depends(get_schedule_service)):
    return service.resume_schedule(schedule_id)

@router.delete("/{schedule_id}", status_code=204)
def delete_schedule(schedule_id: UUID, service: ScheduleService = Depends(get_schedule_service)):
    service.delete_schedule(schedule_id)
