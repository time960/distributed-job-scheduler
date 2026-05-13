import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime, timezone
from app.main import app

client = TestClient(app)

def test_metrics_prometheus():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "jobs_total" in response.text
    assert "workers_total" in response.text

def test_jobs_filtering():
    # Because we're using a MockJobService in test_jobs.py that overrides get_job_service,
    # making an actual DB call via TestClient will hit the mock unless we undo the override,
    # or test the repository directly.
    # To test the API endpoint properly, we just ensure it accepts the query params without 422 errors.
    
    response = client.get("/jobs?status=pending&priority=10&limit=5&skip=0")
    assert response.status_code == 200
    
    # Check that validation error occurs for bad limit
    response = client.get("/jobs?limit=10000")
    assert response.status_code == 422
