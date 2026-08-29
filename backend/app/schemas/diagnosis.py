"""
NetSage AI — Diagnosis Pydantic Schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DiagnoseRequest(BaseModel):
    """Optional runtime evidence override for diagnosis endpoint."""

    symptom: Optional[str] = None
    topology: Optional[str] = None
    show_outputs: Optional[Dict[str, str]] = None
    devices: Optional[List[Dict[str, Any]]] = None
    destination_network: Optional[str] = None
    expected_vlan: Optional[str] = None


class EvidenceItem(BaseModel):
    source: str
    observation: str


class DiagnosisResponse(BaseModel):
    """Full diagnosis response schema."""

    id: int
    case_id: str
    root_cause: str
    confidence: str
    confidence_score: float
    evidence: List[EvidenceItem]
    osi_layer: Optional[str]
    concept: Optional[str]
    next_command: Optional[str]
    fix_steps: List[str]
    limitations: List[str]
    ai_provider: str
    model_name: Optional[str]
    prompt_version: Optional[str]
    grounding_status: str
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, d) -> "DiagnosisResponse":
        return cls(
            id=d.id,
            case_id=d.case_id,
            root_cause=d.root_cause,
            confidence=d.confidence,
            confidence_score=d.confidence_score,
            evidence=[EvidenceItem(**e) for e in d.evidence_list],
            osi_layer=d.osi_layer,
            concept=d.concept,
            next_command=d.next_command,
            fix_steps=d.fix_steps_list,
            limitations=d.limitations_list,
            ai_provider=d.ai_provider,
            model_name=d.model_name,
            prompt_version=d.prompt_version,
            grounding_status=d.grounding_status,
            created_at=d.created_at,
        )


class ComparisonResult(BaseModel):
    """Result of comparing AI diagnosis with rule engine findings."""

    agreement: bool
    agreement_type: str  # STRONG | PARTIAL | CONFLICT | NO_RULE_EVIDENCE
    ai_root_cause: str
    rule_findings: List[str]
    conflicts: List[str]
    grounding_status: str
    requires_human_review: bool = True  # ALWAYS true


class DiagnoseResponse(BaseModel):
    """Full response from the diagnose endpoint."""

    case: Dict[str, Any]
    ai_diagnosis: DiagnosisResponse
    rule_findings: List[Dict[str, Any]]
    comparison: ComparisonResult
    workflow_state: str = "AWAITING_HUMAN_REVIEW"
    request_id: str
    timestamp: datetime
