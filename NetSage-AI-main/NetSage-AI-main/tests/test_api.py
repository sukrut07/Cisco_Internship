import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "NetSage AI"


def test_get_cases():
    response = client.get("/api/cases")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_diagnose_case():
    cases_resp = client.get("/api/cases")
    case_id = cases_resp.json()[0]["id"]

    response = client.post(f"/api/cases/{case_id}/diagnose")
    assert response.status_code == 200
    data = response.json()
    assert "root_cause" in data
    assert "confidence" in data
    assert "osi_layer" in data
    assert isinstance(data["evidence"], list)


def test_human_review_workflow():
    cases_resp = client.get("/api/cases")
    case_id = cases_resp.json()[0]["id"]

    # Test ACCEPT review
    review_data = {
        "decision": "ACCEPT",
        "reviewer_comments": "Accepted via test suite",
        "reviewer_name": "Test Suite"
    }
    response = client.post(f"/api/cases/{case_id}/review", json=review_data)
    assert response.status_code == 200
    assert response.json()["decision"] == "ACCEPT"


def test_verification_endpoint():
    cases_resp = client.get("/api/cases")
    case_id = cases_resp.json()[0]["id"]

    verif_data = {
        "verification_output": "show ip interface brief\nGigabitEthernet0/0 up up\nSuccess rate is 100 percent (5/5)"
    }
    response = client.post(f"/api/cases/{case_id}/verify", json=verif_data)
    assert response.status_code == 200, response.text
    res_json = response.json()
    assert res_json["status"] == "Passed", f"Got status={res_json['status']}, explanation={res_json['explanation']}"


def test_dashboard_stats():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_cases" in data
    assert "accepted_diagnoses" in data
    assert "agreement_rate" in data


def test_responsible_ai_endpoint():
    response = client.get("/api/responsible-ai")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "corrections_log" in data
