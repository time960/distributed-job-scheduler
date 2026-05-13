import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime, timezone
from app.main import app
from app.schemas.worker import WorkerResponse
from app.models.worker import WorkerStatus

mock_worker_id = "worker-12345678"
base_mock_worker = {
    "id": str(uuid4()),
    "worker_id": mock_worker_id,
    "hostname": "localhost",
    "status": WorkerStatus.ACTIVE,
    "last_heartbeat_at": datetime.now(timezone.utc).isoformat(),
    "started_at": datetime.now(timezone.utc).isoformat(),
    "stopped_at": None,
    "jobs_processed": 0,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat()
}

class MockWorkerService:
    def list_workers(self, skip=0, limit=100):
        return [WorkerResponse(**base_mock_worker)]

    def list_active_workers(self, skip=0, limit=100):
        return [WorkerResponse(**base_mock_worker)]

    def list_dead_workers(self, skip=0, limit=100):
        dead_worker = base_mock_worker.copy()
        dead_worker["status"] = WorkerStatus.DEAD
        return [WorkerResponse(**dead_worker)]

    def get_worker(self, worker_id):
        worker = base_mock_worker.copy()
        worker["worker_id"] = worker_id
        return WorkerResponse(**worker)

from app.api.workers import get_worker_service

def override_get_worker_service():
    return MockWorkerService()

app.dependency_overrides[get_worker_service] = override_get_worker_service

client = TestClient(app)

def test_list_workers():
    response = client.get("/workers")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["worker_id"] == mock_worker_id

def test_list_active_workers():
    response = client.get("/workers/active")
    assert response.status_code == 200
    assert response.json()[0]["status"].upper() == WorkerStatus.ACTIVE.name

def test_list_dead_workers():
    response = client.get("/workers/dead")
    assert response.status_code == 200
    assert response.json()[0]["status"].upper() == WorkerStatus.DEAD.name

def test_get_worker():
    response = client.get(f"/workers/{mock_worker_id}")
    assert response.status_code == 200
    assert response.json()["worker_id"] == mock_worker_id
