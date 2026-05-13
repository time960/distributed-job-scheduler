import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from app.main import app
from app.models.job import JobStatus
from app.schemas.job import JobResponse

# Mock data
mock_job_id = uuid4()
base_mock_job = {
    "id": str(mock_job_id),
    "name": "test_job",
    "payload": {"key": "value"},
    "status": JobStatus.PENDING,
    "priority": 0,
    "run_at": datetime.now(timezone.utc).isoformat(),
    "attempts": 0,
    "max_attempts": 3,
    "locked_by": None,
    "locked_at": None,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "error_message": None,
    "next_retry_at": None,
    "completed_at": None
}

class MockJobService:
    def create_job(self, job_in):
        job = base_mock_job.copy()
        job["name"] = job_in.name
        job["payload"] = job_in.payload
        return JobResponse(**job)

    def get_job(self, job_id):
        job = base_mock_job.copy()
        job["id"] = job_id
        return JobResponse(**job)

    def list_jobs(self, skip=0, limit=100, status=None, priority=None, schedule_id=None):
        return [JobResponse(**base_mock_job)]

    def cancel_job(self, job_id):
        canceled = base_mock_job.copy()
        canceled["status"] = JobStatus.CANCELED
        return JobResponse(**canceled)

    def retry_job(self, job_id):
        retried = base_mock_job.copy()
        retried["status"] = JobStatus.PENDING
        retried["error_message"] = None
        retried["next_retry_at"] = datetime.now(timezone.utc).isoformat()
        return JobResponse(**retried)

from app.api.jobs import get_job_service

def override_get_job_service():
    return MockJobService()

app.dependency_overrides[get_job_service] = override_get_job_service

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_successful_job():
    response = client.post("/jobs", json={"name": "test_job", "payload": {}})
    assert response.status_code == 201
    assert response.json()["name"] == "test_job"

def test_list_jobs():
    response = client.get("/jobs")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_manual_retry_endpoint():
    response = client.post(f"/jobs/{mock_job_id}/retry")
    assert response.status_code == 200
    assert response.json()["status"] == "pending"
