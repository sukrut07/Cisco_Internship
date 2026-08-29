"""
NetSage AI — Rules Pydantic Schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class RuleResultResponse(BaseModel):
    """Schema for a single rule check result."""

    id: int
    case_id: str
    diagnosis_id: Optional[int]
    rule_name: str
    status: str  # PASS | FAIL | WARNING | NOT_CHECKED
    severity: str
    message: str
    evidence: List[str]
    details: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, r) -> "RuleResultResponse":
        return cls(
            id=r.id,
            case_id=r.case_id,
            diagnosis_id=r.diagnosis_id,
            rule_name=r.rule_name,
            status=r.status,
            severity=r.severity,
            message=r.message,
            evidence=r.evidence_list,
            details=r.details_dict,
            created_at=r.created_at,
        )


class RuleSummary(BaseModel):
    """Lightweight rule result for diagnosis response."""

    rule_name: str
    status: str
    severity: str
    message: str
