"""
NetSage AI — Audit Trail Endpoint Tests.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.conftest import SAMPLE_CASE_PAYLOAD


def test_get_case_audit_trail_created_event(client: TestClient):
    # 1. Create a case
    create_resp = client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    assert create_resp.status_code == 201
    case_id = SAMPLE_CASE_PAYLOAD["case_id"]

    # 2. Get audit trail
    resp = client.get(f"/api/v1/cases/{case_id}/audit-trail")
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) >= 1
    assert events[0]["event_type"] == "CASE_CREATED"
    assert events[0]["case_id"] == case_id
    assert "metadata" in events[0]


def test_get_case_audit_trail_not_found(client: TestClient):
    resp = client.get("/api/v1/cases/NONEXISTENT-999/audit-trail")
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "CASE_NOT_FOUND"


def test_audit_trail_chronological_progression(client: TestClient):
    case_id = "AUDIT-FLOW-001"
    payload = {**SAMPLE_CASE_PAYLOAD, "case_id": case_id}
    client.post("/api/v1/cases", json=payload)

    # Diagnose
    client.post(f"/api/v1/cases/{case_id}/diagnose")

    # Review
    diag_resp = client.get(f"/api/v1/cases/{case_id}/diagnoses")
    diag_id = diag_resp.json()[0]["id"]
    client.post(
        f"/api/v1/cases/{case_id}/review",
        json={"diagnosis_id": diag_id, "decision": "ACCEPTED", "reviewer": "eng1"},
    )

    # Check audit trail
    resp = client.get(f"/api/v1/cases/{case_id}/audit-trail")
    assert resp.status_code == 200
    events = resp.json()
    event_types = [e["event_type"] for e in events]

    assert "CASE_CREATED" in event_types
    assert "DIAGNOSIS_REQUESTED" in event_types
    assert "AI_DIAGNOSIS_COMPLETED" in event_types
    assert "REVIEW_ACCEPTED" in event_types
