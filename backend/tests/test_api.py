import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert "python" in data["languages_supported"]


def test_api_run_python():
    payload = {
        "language": "python",
        "code": "total = sum([1, 2, 3, 4])\nprint(f'Total: {total}')",
    }
    response = client.post("/runs", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["exit_code"] == 0
    assert "Total: 10" in data["stdout"]
    assert data["timed_out"] is False


def test_api_run_unsupported_language():
    payload = {
        "language": "rust",
        "code": "fn main() { println!(\"Hi\"); }",
    }
    response = client.post("/runs", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "not yet supported" in data["detail"].lower()
