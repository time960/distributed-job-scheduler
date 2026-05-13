import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_leader():
    response = client.get("/leader")
    assert response.status_code == 200
    data = response.json()
    assert "leader_id" in data
    assert "ttl" in data
    assert "status" in data
