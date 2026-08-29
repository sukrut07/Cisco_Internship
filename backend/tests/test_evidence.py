"""
NetSage AI — Evidence Endpoint Tests.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.conftest import SAMPLE_CASE_PAYLOAD


def test_get_case_evidence_success(client: TestClient):
    # 1. Create a case
    create_resp = client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    assert create_resp.status_code == 201
    case_id = SAMPLE_CASE_PAYLOAD["case_id"]

    # 2. Query evidence
    resp = client.get(f"/api/v1/cases/{case_id}/evidence")
    assert resp.status_code == 200
    data = resp.json()

    assert data["case_id"] == case_id
    assert data["total_commands"] == 1
    assert len(data["evidence"]) == 1
    assert data["evidence"][0]["command"] == "show ip route"
    assert data["evidence"][0]["status"] == "ok"
    assert data["evidence"][0]["parsed"] is not None


def test_get_case_evidence_not_found(client: TestClient):
    resp = client.get("/api/v1/cases/NONEXISTENT-999/evidence")
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "CASE_NOT_FOUND"


def test_get_case_evidence_multiple_commands(client: TestClient):
    payload = {
        **SAMPLE_CASE_PAYLOAD,
        "case_id": "MULTI-CMD-001",
        "show_outputs": {
            "show ip route": "C 192.168.1.0/24 is directly connected, GigabitEthernet0/0",
            "show vlan brief": "1 default active Fa0/1\n10 SALES active Fa0/2",
            "show access-lists": "Standard IP access list 10\n 10 deny 192.168.1.5 (12 matches)",
        },
    }
    client.post("/api/v1/cases", json=payload)

    resp = client.get("/api/v1/cases/MULTI-CMD-001/evidence")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_commands"] == 3
    cmds = [item["command"] for item in data["evidence"]]
    assert "show ip route" in cmds
    assert "show vlan brief" in cmds
    assert "show access-lists" in cmds
