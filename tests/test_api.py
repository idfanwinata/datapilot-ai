
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "OpsPilot AI" in response.text


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_connection_error():
    response = client.post(
        "/diagnostics/analyze",
        json={
            "application": "PaymentService",
            "error_log": "Database connection refused",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "PaymentService"
    assert "service" in data["possible_cause"].lower()
    assert len(data["recommended_steps"]) > 0
    assert data["analysis_type"] == "mock"


def test_analyze_rejects_empty_application():
    response = client.post(
        "/diagnostics/analyze",
        json={
            "application": "",
            "error_log": "Connection refused",
        },
    )

    assert response.status_code == 422
