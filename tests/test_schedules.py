import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime, timezone
from app.main import app
from app.schemas.schedule import ScheduleResponse
from app.scheduler.scheduler import calculate_next_run

# Mock data
mock_schedule_id = uuid4()
base_mock_schedule = {
    "id": str(mock_schedule_id),
    "name": "test_cron",
    "cron_expression": "* * * * *",
    "payload": {"key": "value"},
    "priority": 0,
    "max_attempts": 3,
    "is_active": True,
    "last_run_at": None,
    "next_run_at": datetime.now(timezone.utc).isoformat(),
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat()
}

class MockScheduleService:
    def create_schedule(self, schedule_in):
        sched = base_mock_schedule.copy()
        sched["name"] = schedule_in.name
        sched["cron_expression"] = schedule_in.cron_expression
        return ScheduleResponse(**sched)

    def get_schedule(self, schedule_id):
        sched = base_mock_schedule.copy()
        sched["id"] = schedule_id
        return ScheduleResponse(**sched)

    def list_schedules(self, skip=0, limit=100):
        return [ScheduleResponse(**base_mock_schedule)]

    def pause_schedule(self, schedule_id):
        paused = base_mock_schedule.copy()
        paused["is_active"] = False
        return ScheduleResponse(**paused)

    def resume_schedule(self, schedule_id):
        resumed = base_mock_schedule.copy()
        resumed["is_active"] = True
        return ScheduleResponse(**resumed)

from app.api.schedules import get_schedule_service

def override_get_schedule_service():
    return MockScheduleService()

app.dependency_overrides[get_schedule_service] = override_get_schedule_service

client = TestClient(app)

def test_create_schedule():
    response = client.post("/schedules", json={"name": "test_cron", "cron_expression": "* * * * *", "payload": {}})
    assert response.status_code == 201
    assert response.json()["name"] == "test_cron"
    assert response.json()["is_active"] == True

def test_pause_schedule():
    response = client.post(f"/schedules/{mock_schedule_id}/pause")
    assert response.status_code == 200
    assert response.json()["is_active"] == False

def test_resume_schedule():
    response = client.post(f"/schedules/{mock_schedule_id}/resume")
    assert response.status_code == 200
    assert response.json()["is_active"] == True

def test_calculate_next_run():
    dt = datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)
    next_run = calculate_next_run("* * * * *", dt)
    assert next_run == datetime(2026, 5, 11, 12, 1, tzinfo=timezone.utc)
