"""Tests for Case API endpoints."""
import pytest
from tests.conftest import SAMPLE_CASE_PAYLOAD


def test_create_case(client):
    response = client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["case_id"] == "TEST-001"
    assert data["category"] == "STATIC_ROUTING"
    assert data["severity"] == "HIGH"
    assert data["workflow_state"] == "CREATED"


def test_create_duplicate_case(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    response = client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    assert response.status_code == 409


def test_get_case(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    response = client.get("/api/v1/cases/TEST-001")
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "TEST-001"


def test_get_case_not_found(client):
    response = client.get("/api/v1/cases/NONEXISTENT-999")
    assert response.status_code == 404
    data = response.json()
    # NetSageException wraps in "error" key; FastAPI HTTPException uses "detail"
    assert "error" in data or "detail" in data
    # The error code should be CASE_NOT_FOUND regardless of wrapper
    raw = data.get("error", data.get("detail", {}))
    assert raw.get("code") == "CASE_NOT_FOUND"


def test_list_cases_empty(client):
    response = client.get("/api/v1/cases")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_cases_pagination(client):
    # Create 3 cases
    for i in range(1, 4):
        payload = SAMPLE_CASE_PAYLOAD.copy()
        payload["case_id"] = f"TEST-{i:03d}"
        client.post("/api/v1/cases", json=payload)

    response = client.get("/api/v1/cases?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["pages"] == 2


def test_list_cases_filter_category(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    response = client.get("/api/v1/cases?category=STATIC_ROUTING")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["category"] == "STATIC_ROUTING"


def test_list_cases_filter_severity(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    response = client.get("/api/v1/cases?severity=HIGH")
    assert response.status_code == 200
    data = response.json()
    assert all(i["severity"] == "HIGH" for i in data["items"])


def test_update_case(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    response = client.put(
        "/api/v1/cases/TEST-001",
        json={"title": "Updated Title", "severity": "CRITICAL"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["severity"] == "CRITICAL"


def test_delete_case(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    response = client.delete("/api/v1/cases/TEST-001")
    assert response.status_code == 204

    get_response = client.get("/api/v1/cases/TEST-001")
    assert get_response.status_code == 404


def test_search_cases(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    response = client.get("/api/v1/cases?search=Missing Route")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_case_id_normalized_to_uppercase(client):
    payload = SAMPLE_CASE_PAYLOAD.copy()
    payload["case_id"] = "test-001"
    response = client.post("/api/v1/cases", json=payload)
    assert response.status_code == 201
    assert response.json()["case_id"] == "TEST-001"


def test_oversized_request_rejection(client):
    """Requests exceeding MAX_REQUEST_BODY_MB must receive HTTP 413."""
    huge_headers = {"Content-Length": str(10 * 1024 * 1024)}  # 10 MB declared
    response = client.post("/api/v1/cases", headers=huge_headers, json=SAMPLE_CASE_PAYLOAD)
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "REQUEST_ENTITY_TOO_LARGE"


def test_secret_redaction_security():
    from app.core.security import redact_secrets

    sensitive_dict = {
        "api_key": "sk-proj-secret-12345",
        "nested": {
            "password": "super-secret-db-pass",
            "auth_token": "bearer eyJ...",
            "normal_field": "public_data",
        },
        "list_data": [{"bearer": "token123"}, "clean_string"],
    }
    redacted = redact_secrets(sensitive_dict)
    assert redacted["api_key"] == "***REDACTED***"
    assert redacted["nested"]["password"] == "***REDACTED***"
    assert redacted["nested"]["auth_token"] == "***REDACTED***"
    assert redacted["nested"]["normal_field"] == "public_data"
    assert redacted["list_data"][0]["bearer"] == "***REDACTED***"
    assert redacted["list_data"][1] == "clean_string"
