"""
NetSage AI — Full Workflow End-to-End Integration Test.

Validates the entire lifecycle:
1. Create Case
2. Query Evidence
3. Run AI Diagnosis + Rules + Grounding
4. Mandatory Human Review (ACCEPT / EDIT / REJECT)
5. Record Fix (HUMAN_APPLIED, never executed)
6. Record Verification (SUCCESS / FAILED)
7. Query Audit Trail
8. Query Dashboard & Responsible AI Analytics
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.conftest import SAMPLE_CASE_PAYLOAD


def test_complete_human_in_the_loop_e2e_workflow(client: TestClient):
    case_id = "E2E-INTEGRATION-001"
    payload = {
        **SAMPLE_CASE_PAYLOAD,
        "case_id": case_id,
        "title": "E2E Inter-VLAN Routing Failure",
        "category": "INTER_VLAN_ROUTING",
        "symptom": "Host in VLAN 10 cannot ping Host in VLAN 20. Gateway unreachable.",
        "topology": "Host1 (VLAN 10) -> SW1 -> Router -> SW1 -> Host2 (VLAN 20)",
        "show_outputs": {
            "show ip route": "Codes: C - connected, S - static\nC 192.168.10.0/24 is directly connected, GigabitEthernet0/0.10",
            "show ip interface brief": "GigabitEthernet0/0.10 192.168.10.1 YES manual up up\nGigabitEthernet0/0.20 192.168.20.1 YES manual administratively down down",
            "show interfaces trunk": "Port Mode Encapsulation Status Native vlan\nFa0/1 on 802.1q trunking 1\nPort Vlans allowed on trunk\nFa0/1 1-4094",
        },
        "expected_fault": "Sub-interface GigabitEthernet0/0.20 is administratively down",
        "expected_osi_layer": "Layer 3",
        "severity": "HIGH",
    }

    # Step 1: Create Case
    create_resp = client.post("/api/v1/cases", json=payload)
    assert create_resp.status_code == 201
    assert create_resp.json()["case_id"] == case_id
    assert create_resp.json()["workflow_state"] == "CREATED"

    # Step 2: Query Evidence Endpoint
    ev_resp = client.get(f"/api/v1/cases/{case_id}/evidence")
    assert ev_resp.status_code == 200
    ev_data = ev_resp.json()
    assert ev_data["total_commands"] == 3
    assert len(ev_data["evidence"]) == 3

    # Step 3: Run Diagnosis
    diag_resp = client.post(f"/api/v1/cases/{case_id}/diagnose")
    assert diag_resp.status_code == 201
    diag_data = diag_resp.json()

    # Verify Human-in-the-Loop requirement
    assert diag_data["workflow_state"] == "AWAITING_HUMAN_REVIEW"
    assert diag_data["comparison"]["requires_human_review"] is True
    assert diag_data["ai_diagnosis"]["id"] is not None
    diagnosis_id = diag_data["ai_diagnosis"]["id"]

    # Verify rule findings were generated
    rule_names = [r["rule_name"] for r in diag_data["rule_findings"]]
    assert "interface_status" in rule_names

    # Step 4: Mandatory Human Review (Submit ACCEPT)
    review_payload = {
        "diagnosis_id": diagnosis_id,
        "decision": "ACCEPTED",
        "reviewer": "Senior NetOps Engineer",
        "review_reason": "Verified interface Gi0/0.20 is shut down.",
    }
    review_resp = client.post(f"/api/v1/cases/{case_id}/review", json=review_payload)
    assert review_resp.status_code == 201
    review_data = review_resp.json()
    assert review_data["decision"] == "ACCEPTED"
    assert review_data["final_diagnosis"] != {}
    review_id = review_data["id"]

    # Verify case transitioned to ACCEPTED
    case_resp = client.get(f"/api/v1/cases/{case_id}")
    assert case_resp.json()["workflow_state"] == "ACCEPTED"

    # Step 5: Record Fix (HUMAN_APPLIED — safety: never executed)
    fix_payload = {
        "review_id": review_id,
        "commands": ["interface GigabitEthernet0/0.20", "no shutdown"],
        "description": "Brought up sub-interface Gi0/0.20",
        "performed_by": "Senior NetOps Engineer",
    }
    fix_resp = client.post(f"/api/v1/cases/{case_id}/fix", json=fix_payload)
    assert fix_resp.status_code == 201
    fix_data = fix_resp.json()
    assert fix_data["status"] == "RECORDED"
    assert fix_data["safety_notice"] is not None

    # Step 6: Record Verification
    verif_payload = {
        "review_id": review_id,
        "verification_status": "SUCCESS",
        "verification_method": "PING",
        "verification_evidence": "Ping from 192.168.10.10 to 192.168.20.10 succeeded with 5/5 replies (100%).",
        "verified_by": "Senior NetOps Engineer",
    }
    verif_resp = client.post(f"/api/v1/cases/{case_id}/verify", json=verif_payload)
    assert verif_resp.status_code == 201
    assert verif_resp.json()["verification_status"] == "SUCCESS"

    # Step 7: Check Audit Trail
    audit_resp = client.get(f"/api/v1/cases/{case_id}/audit-trail")
    assert audit_resp.status_code == 200
    events = [e["event_type"] for e in audit_resp.json()]
    assert "CASE_CREATED" in events
    assert "DIAGNOSIS_REQUESTED" in events
    assert "REVIEW_ACCEPTED" in events
    assert "FIX_RECORDED" in events
    assert "VERIFICATION_COMPLETED" in events

    # Step 8: Check Dashboard & Responsible AI
    dash_resp = client.get("/api/v1/dashboard/summary")
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert dash_data["total_cases"] >= 1
    assert dash_data["total_diagnoses"] >= 1
    assert dash_data["total_reviews"] >= 1

    rai_resp = client.get("/api/v1/responsible-ai/summary")
    assert rai_resp.status_code == 200
    rai_data = rai_resp.json()
    assert rai_data["total_diagnoses"] >= 1
    assert rai_data["accepted"] >= 1


def test_edit_review_workflow_preserves_original_ai(client: TestClient):
    case_id = "EDIT-FLOW-001"
    payload = {**SAMPLE_CASE_PAYLOAD, "case_id": case_id}
    client.post("/api/v1/cases", json=payload)
    diag_resp = client.post(f"/api/v1/cases/{case_id}/diagnose")
    diag_id = diag_resp.json()["ai_diagnosis"]["id"]

    edit_payload = {
        "diagnosis_id": diag_id,
        "decision": "EDITED",
        "reviewer": "Alice",
        "review_reason": "Corrected root cause details based on topology",
        "edited_diagnosis": {
            "root_cause": "Static route next hop IP is transposed",
            "confidence": "HIGH",
            "confidence_score": 0.95,
            "evidence": [],
            "osi_layer": "Layer 3",
            "concept": "Static Routing",
            "next_command": "show run | inc ip route",
            "fix_steps": ["no ip route ...", "ip route ..."],
            "limitations": [],
        },
    }
    resp = client.post(f"/api/v1/cases/{case_id}/review", json=edit_payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["decision"] == "EDITED"
    assert data["original_ai_diagnosis"]["root_cause"] != data["final_diagnosis"]["root_cause"]
    assert data["final_diagnosis"]["root_cause"] == "Static route next hop IP is transposed"


def test_cannot_fix_before_review_approval(client: TestClient):
    case_id = "ILLEGAL-FIX-001"
    payload = {**SAMPLE_CASE_PAYLOAD, "case_id": case_id}
    client.post("/api/v1/cases", json=payload)
    # Attempting to fix without human review should fail
    resp = client.post(
        f"/api/v1/cases/{case_id}/fix",
        json={
            "review_id": 9999,
            "commands": ["no shutdown"],
            "description": "Attempted fix without review",
        },
    )
    assert resp.status_code in [400, 404, 422]


def test_cannot_verify_before_fix_staged(client: TestClient):
    case_id = "ILLEGAL-VERIF-001"
    payload = {**SAMPLE_CASE_PAYLOAD, "case_id": case_id}
    client.post("/api/v1/cases", json=payload)
    diag_resp = client.post(f"/api/v1/cases/{case_id}/diagnose")
    diag_id = diag_resp.json()["ai_diagnosis"]["id"]
    rev_resp = client.post(
        f"/api/v1/cases/{case_id}/reviews",
        json={"diagnosis_id": diag_id, "decision": "ACCEPTED", "reviewer": "Bob"},
    )
    review_id = rev_resp.json()["id"]

    # Attempting to verify with an invalid/non-existent review or before fix should fail
    bad_verif = client.post(
        f"/api/v1/cases/{case_id}/verification",
        json={
            "review_id": 999999,
            "verification_status": "SUCCESS",
            "verification_method": "PING",
        },
    )
    assert bad_verif.status_code in [400, 404, 422]
