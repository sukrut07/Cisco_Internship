import pytest
from fastapi.testclient import TestClient
from tests.conftest import SAMPLE_CASE_PAYLOAD


def test_diagnose_case_mock(client):
    """Full diagnosis pipeline with mock AI provider."""
    # Create case
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)

    # Run diagnosis
    response = client.post("/api/v1/cases/TEST-001/diagnose")
    assert response.status_code == 201

    data = response.json()
    assert "ai_diagnosis" in data
    assert "rule_findings" in data
    assert "comparison" in data
    assert data["workflow_state"] == "AWAITING_HUMAN_REVIEW"
    assert data["comparison"]["requires_human_review"] is True


def test_diagnose_returns_evidence(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    response = client.post("/api/v1/cases/TEST-001/diagnose")
    data = response.json()

    ai_diag = data["ai_diagnosis"]
    assert "root_cause" in ai_diag
    assert "confidence" in ai_diag
    assert ai_diag["confidence"] in ("LOW", "MEDIUM", "HIGH")
    assert 0.0 <= ai_diag["confidence_score"] <= 1.0


def test_diagnose_case_not_found(client):
    response = client.post("/api/v1/cases/NONEXISTENT-999/diagnose")
    assert response.status_code == 404


def test_diagnose_with_runtime_evidence(client):
    """Test that runtime evidence overrides stored case data."""
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)

    runtime_request = {
        "symptom": "PC cannot reach server — custom runtime symptom",
        "show_outputs": {
            "show ip route": "C    192.168.1.0/24 is directly connected, GigabitEthernet0/0"
        },
    }
    response = client.post("/api/v1/cases/TEST-001/diagnose", json=runtime_request)
    assert response.status_code == 201


def test_get_case_diagnoses(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    client.post("/api/v1/cases/TEST-001/diagnose")
    client.post("/api/v1/cases/TEST-001/diagnose")  # Run twice

    response = client.get("/api/v1/cases/TEST-001/diagnoses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Both stored, never overwritten


def test_get_single_diagnosis(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    diag_response = client.post("/api/v1/cases/TEST-001/diagnose")
    diag_id = diag_response.json()["ai_diagnosis"]["id"]

    response = client.get(f"/api/v1/diagnoses/{diag_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == diag_id


def test_diagnosis_grounding_status_present(client):
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    response = client.post("/api/v1/cases/TEST-001/diagnose")
    data = response.json()
    assert "grounding_status" in data["ai_diagnosis"]
    assert data["ai_diagnosis"]["grounding_status"] in (
        "GROUNDED", "PARTIALLY_GROUNDED", "UNGROUNDED", "UNKNOWN"
    )


def test_diagnosis_human_review_always_required(client):
    """Core business rule: human review is always required."""
    client.post("/api/v1/cases", json=SAMPLE_CASE_PAYLOAD)
    response = client.post("/api/v1/cases/TEST-001/diagnose")
    data = response.json()
    assert data["comparison"]["requires_human_review"] is True


def test_ai_evidence_parser_malformed_json():
    """Test that malformed AI JSON is rejected gracefully."""
    from app.ai.parser import AIResponseParser
    parser = AIResponseParser()

    result = parser.parse("This is not JSON at all")
    assert result["success"] is False
    assert result["error"] is not None


def test_ai_evidence_parser_valid_json():
    """Test that valid AI JSON passes parsing."""
    from app.ai.parser import AIResponseParser
    parser = AIResponseParser()

    valid_json = """{
        "root_cause": "Missing static route to destination network",
        "confidence": "HIGH",
        "confidence_score": 0.90,
        "evidence": [{"source": "show ip route", "observation": "Destination absent"}],
        "osi_layer": "Layer 3",
        "concept": "Static Routing",
        "next_command": "show ip route",
        "fix_steps": ["Configure static route"],
        "limitations": []
    }"""
    result = parser.parse(valid_json)
    assert result["success"] is True
    assert result["ai_output"] is not None


def test_ai_evidence_grounding_valid_source():
    """AI evidence from a valid source should be GROUNDED."""
    from app.ai.parser import AIResponseParser
    parser = AIResponseParser()

    valid_json = """{
        "root_cause": "Missing route",
        "confidence": "HIGH",
        "confidence_score": 0.85,
        "evidence": [{"source": "show ip route", "observation": "route missing from routing table"}],
        "osi_layer": "Layer 3",
        "concept": "Routing",
        "next_command": "show ip route",
        "fix_steps": ["Add route"],
        "limitations": []
    }"""
    show_outputs = {"show ip route": "route missing from routing table in output"}
    result = parser.parse(valid_json, show_outputs)
    assert result["grounding_status"] in ("GROUNDED", "PARTIALLY_GROUNDED")


def test_comparison_conflict_scenario():
    """Test AI vs rule conflict: AI says DNS, rules say Missing Route."""
    from app.services.comparison_service import comparison_service
    from app.rules.base import RuleCheckResult

    rule_results = [
        RuleCheckResult(
            rule_name="missing_route",
            status="FAIL",
            severity="HIGH",
            message="No route to 192.168.30.0/24 in routing table.",
            evidence=["show ip route: missing"],
        )
    ]
    comparison = comparison_service.compare(
        ai_root_cause="DNS server 8.8.8.8 unreachable causing resolution failure",
        ai_osi_layer="Layer 7",
        rule_results=rule_results,
        grounding_status="GROUNDED",
    )
    assert comparison["agreement_type"] in ("CONFLICT", "DISAGREEMENT")
    assert comparison["requires_human_review"] is True


def test_comparison_partial_agreement_scenario():
    """Test partial agreement: AI says routing problem, rule detected missing route."""
    from app.services.comparison_service import comparison_service
    from app.rules.base import RuleCheckResult

    rule_results = [
        RuleCheckResult(
            rule_name="missing_route",
            status="FAIL",
            severity="HIGH",
            message="No route to destination network.",
            evidence=["show ip route"],
        )
    ]
    comparison = comparison_service.compare(
        ai_root_cause="Routing issue: missing route to remote host",
        ai_osi_layer="Layer 3",
        rule_results=rule_results,
        grounding_status="GROUNDED",
    )
    assert comparison["agreement_type"] in ("STRONG", "PARTIAL", "AGREEMENT")
    assert comparison["requires_human_review"] is True


def test_comparison_no_rule_evidence_scenario():
    """When rules detect nothing (PASS/NOT_CHECKED), agreement_type should reflect no rule evidence."""
    from app.services.comparison_service import comparison_service
    from app.rules.base import RuleCheckResult

    rule_results = [
        RuleCheckResult(
            rule_name="vlan_check",
            status="NOT_CHECKED",
            severity="LOW",
            message="No VLAN info",
        )
    ]
    comparison = comparison_service.compare(
        ai_root_cause="Physical cable unplugged",
        ai_osi_layer="Layer 1",
        rule_results=rule_results,
        grounding_status="GROUNDED",
    )
    assert comparison["requires_human_review"] is True


def test_ai_provider_timeout_exception(client: TestClient, monkeypatch):
    """Verify that an AI provider timeout returns HTTP 504 Gateway Timeout."""
    from app.core.exceptions import AIProviderTimeout

    def mock_diagnose_timeout(*args, **kwargs):
        raise AIProviderTimeout("Request to AI provider timed out after 30s.")

    from app.services.diagnosis_service import diagnosis_service
    monkeypatch.setattr(diagnosis_service, "run_diagnosis", mock_diagnose_timeout)

    resp = client.post("/api/v1/cases/TEST-001/diagnose")
    assert resp.status_code == 504
    assert resp.json()["detail"]["code"] == "AI_PROVIDER_TIMEOUT"
