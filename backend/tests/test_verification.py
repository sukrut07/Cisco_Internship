"""Tests for Verification API."""
import pytest
from tests.conftest import SAMPLE_CASE_PAYLOAD


def _setup_to_review_stage(client):
    """Create case, diagnose, and accept review. Return review_id."""
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    diag_resp = client.post("/api/v1/cases/TEST-001/diagnose")
    diag_id = diag_resp.json()["ai_diagnosis"]["id"]
    review_resp = client.post(
        "/api/v1/cases/TEST-001/review",
        json={"diagnosis_id": diag_id, "decision": "ACCEPTED", "reviewer": "S1"},
    )
    return review_resp.json()["id"]


def test_create_verification_success(client):
    review_id = _setup_to_review_stage(client)
    response = client.post(
        "/api/v1/cases/TEST-001/verify",
        json={
            "review_id": review_id,
            "verification_status": "SUCCESS",
            "verification_method": "PING",
            "verification_evidence": "Reply from 192.168.30.10: bytes=32 time=1ms",
            "verified_by": "Student-1",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["verification_status"] == "SUCCESS"
    assert data["verification_method"] == "PING"
    assert data["verified_by"] == "Student-1"


def test_create_verification_failed(client):
    review_id = _setup_to_review_stage(client)
    response = client.post(
        "/api/v1/cases/TEST-001/verify",
        json={
            "review_id": review_id,
            "verification_status": "FAILED",
            "verification_method": "MANUAL",
            "verification_evidence": "Still cannot reach destination.",
            "verified_by": "Student-1",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["verification_status"] == "FAILED"


def test_invalid_verification_status(client):
    review_id = _setup_to_review_stage(client)
    response = client.post(
        "/api/v1/cases/TEST-001/verify",
        json={
            "review_id": review_id,
            "verification_status": "INVALID_STATUS",
            "verification_method": "PING",
            "verified_by": "Student-1",
        },
    )
    assert response.status_code == 422


def test_get_case_verifications(client):
    review_id = _setup_to_review_stage(client)
    client.post(
        "/api/v1/cases/TEST-001/verify",
        json={
            "review_id": review_id,
            "verification_status": "SUCCESS",
            "verification_method": "PING",
            "verified_by": "S1",
        },
    )
    response = client.get("/api/v1/cases/TEST-001/verifications")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
