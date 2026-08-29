"""Tests for Review API endpoints."""
import pytest
from tests.conftest import SAMPLE_CASE_PAYLOAD


def _create_case_and_diagnose(client):
    """Helper: create a case and run diagnosis, return diagnosis_id."""
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    resp = client.post("/api/v1/cases/TEST-001/diagnose")
    return resp.json()["ai_diagnosis"]["id"]


def test_accept_review(client):
    diag_id = _create_case_and_diagnose(client)
    response = client.post(
        "/api/v1/cases/TEST-001/review",
        json={
            "diagnosis_id": diag_id,
            "decision": "ACCEPTED",
            "reviewer": "Student-1",
            "review_reason": "AI diagnosis is correct.",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["decision"] == "ACCEPTED"
    assert data["reviewer"] == "Student-1"
    assert data["final_diagnosis"]["root_cause"] != ""


def test_edit_review(client):
    diag_id = _create_case_and_diagnose(client)
    response = client.post(
        "/api/v1/cases/TEST-001/review",
        json={
            "diagnosis_id": diag_id,
            "decision": "EDITED",
            "edited_diagnosis": {
                "root_cause": "Gateway mismatch — human corrected",
                "confidence": "HIGH",
                "osi_layer": "Layer 3",
                "next_command": "show ip interface brief",
                "fix_steps": ["Correct the gateway"],
            },
            "reviewer": "Student-2",
            "review_reason": "AI missed the gateway mismatch.",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["decision"] == "EDITED"
    assert data["final_diagnosis"]["root_cause"] == "Gateway mismatch — human corrected"


def test_reject_review(client):
    diag_id = _create_case_and_diagnose(client)
    response = client.post(
        "/api/v1/cases/TEST-001/review",
        json={
            "diagnosis_id": diag_id,
            "decision": "REJECTED",
            "reviewer": "Student-3",
            "review_reason": "Completely wrong diagnosis.",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["decision"] == "REJECTED"
    assert data["final_diagnosis"] == {}  # REJECTED has no final AI diagnosis


def test_edit_requires_edited_diagnosis(client):
    """EDITED decision must include edited_diagnosis."""
    diag_id = _create_case_and_diagnose(client)
    response = client.post(
        "/api/v1/cases/TEST-001/review",
        json={
            "diagnosis_id": diag_id,
            "decision": "EDITED",
            "reviewer": "Student-1",
            # Missing edited_diagnosis
        },
    )
    assert response.status_code in (400, 422)


def test_invalid_decision(client):
    diag_id = _create_case_and_diagnose(client)
    response = client.post(
        "/api/v1/cases/TEST-001/review",
        json={
            "diagnosis_id": diag_id,
            "decision": "MAYBE",  # Invalid
            "reviewer": "Student-1",
        },
    )
    assert response.status_code == 422


def test_get_case_reviews(client):
    diag_id = _create_case_and_diagnose(client)
    client.post(
        "/api/v1/cases/TEST-001/review",
        json={"diagnosis_id": diag_id, "decision": "ACCEPTED", "reviewer": "S1"},
    )

    response = client.get("/api/v1/cases/TEST-001/reviews")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_get_single_review(client):
    diag_id = _create_case_and_diagnose(client)
    create_resp = client.post(
        "/api/v1/cases/TEST-001/review",
        json={"diagnosis_id": diag_id, "decision": "ACCEPTED", "reviewer": "S1"},
    )
    review_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/reviews/{review_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == review_id


def test_record_fix(client):
    diag_id = _create_case_and_diagnose(client)
    review_resp = client.post(
        "/api/v1/cases/TEST-001/review",
        json={"diagnosis_id": diag_id, "decision": "ACCEPTED", "reviewer": "S1"},
    )
    review_id = review_resp.json()["id"]

    fix_response = client.post(
        "/api/v1/cases/TEST-001/fix",
        json={
            "review_id": review_id,
            "commands": ["ip route 192.168.30.0 255.255.255.0 10.0.0.2"],
            "description": "Added missing static route.",
            "performed_by": "Student-1",
        },
    )
    assert fix_response.status_code == 201
    data = fix_response.json()
    assert data["applied_by"] == "HUMAN_APPLIED"
    assert "NOT automatically executed" in data["note"] or "not" in data["note"].lower()


def test_workflow_original_ai_diagnosis_saved(client):
    """Verify that original AI diagnosis is saved in the review."""
    diag_id = _create_case_and_diagnose(client)
    resp = client.post(
        "/api/v1/cases/TEST-001/review",
        json={"diagnosis_id": diag_id, "decision": "ACCEPTED", "reviewer": "S1"},
    )
    data = resp.json()
    assert data["original_ai_diagnosis"] is not None
    assert "root_cause" in data["original_ai_diagnosis"]


def test_review_edit_without_body_fails(client):
    """EDIT review without edited_diagnosis must fail validation."""
    diag_id = _create_case_and_diagnose(client)
    resp = client.post(
        "/api/v1/cases/TEST-001/review",
        json={"diagnosis_id": diag_id, "decision": "EDITED", "reviewer": "S1"},
    )
    assert resp.status_code == 422


def test_review_invalid_decision_fails(client):
    """Invalid decision string must fail validation."""
    diag_id = _create_case_and_diagnose(client)
    resp = client.post(
        "/api/v1/cases/TEST-001/review",
        json={"diagnosis_id": diag_id, "decision": "APPROVED", "reviewer": "S1"},
    )
    assert resp.status_code == 422


def test_review_nonexistent_diagnosis_fails(client):
    """Reviewing a non-existent diagnosis ID must return 404."""
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    resp = client.post(
        "/api/v1/cases/TEST-001/review",
        json={"diagnosis_id": 99999, "decision": "ACCEPTED", "reviewer": "S1"},
    )
    assert resp.status_code == 404
