"""Tests for Dashboard and Responsible AI APIs."""
import pytest
from tests.conftest import SAMPLE_CASE_PAYLOAD


def test_dashboard_summary_empty(client):
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_cases"] == 0
    assert data["total_diagnoses"] == 0
    assert data["agreement_rate"] is None  # No reviews yet


def test_dashboard_summary_with_data(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    diag_resp = client.post("/api/v1/cases/TEST-001/diagnose")
    diag_id = diag_resp.json()["ai_diagnosis"]["id"]
    client.post(
        "/api/v1/cases/TEST-001/review",
        json={"diagnosis_id": diag_id, "decision": "ACCEPTED", "reviewer": "S1"},
    )

    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_cases"] == 1
    assert data["total_diagnoses"] == 1
    assert data["total_reviews"] == 1
    assert data["accepted"] == 1
    assert data["agreement_rate"] == 1.0
    assert data["human_correction_rate"] == 0.0


def test_dashboard_categories(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    response = client.get("/api/v1/dashboard/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["category"] == "STATIC_ROUTING"


def test_dashboard_severity(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    response = client.get("/api/v1/dashboard/severity")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_dashboard_agreement(client):
    response = client.get("/api/v1/dashboard/agreement")
    assert response.status_code == 200
    data = response.json()
    assert "total_reviewed" in data
    assert "agreement_rate" in data


def test_dashboard_rules(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    client.post("/api/v1/cases/TEST-001/diagnose")
    response = client.get("/api/v1/dashboard/rules")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_dashboard_timeline(client):
    response = client.get("/api/v1/dashboard/timeline?days=7")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_responsible_ai_summary_empty(client):
    response = client.get("/api/v1/responsible-ai/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_diagnoses"] == 0
    assert data["ai_human_agreement_rate"] is None


def test_responsible_ai_summary_with_edit(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    diag_resp = client.post("/api/v1/cases/TEST-001/diagnose")
    diag_id = diag_resp.json()["ai_diagnosis"]["id"]
    client.post(
        "/api/v1/cases/TEST-001/review",
        json={
            "diagnosis_id": diag_id,
            "decision": "EDITED",
            "edited_diagnosis": {
                "root_cause": "Human correction",
                "confidence": "HIGH",
                "next_command": "show ip route",
                "fix_steps": ["Fix it"],
            },
            "reviewer": "S1",
            "review_reason": "Wrong diagnosis",
        },
    )

    response = client.get("/api/v1/responsible-ai/summary")
    data = response.json()
    assert data["edited"] == 1
    assert data["human_correction_rate"] == 1.0
    assert "evaluation_note" in data


def test_responsible_ai_corrections(client):
    response = client.get("/api/v1/responsible-ai/corrections")
    assert response.status_code == 200
    data = response.json()
    assert "corrections" in data
    assert "total_corrections" in data


def test_evaluation_run(client):
    response = client.post("/api/v1/evaluation/run")
    assert response.status_code == 200
    data = response.json()
    assert "cases_evaluated" in data
    assert "evaluation_note" in data
