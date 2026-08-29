"""
NetSage AI — Case Pydantic Schemas.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_CATEGORIES = {
    "VLAN", "TRUNKING", "INTER_VLAN_ROUTING", "IP_ADDRESSING", "GATEWAY",
    "DHCP", "DNS", "STATIC_ROUTING", "DYNAMIC_ROUTING", "ACL", "NAT", "WIRELESS",
    "ROUTING", "GENERAL",
}
VALID_WORKFLOW_STATES = {
    "CREATED", "READY_FOR_DIAGNOSIS", "DIAGNOSING", "AWAITING_HUMAN_REVIEW",
    "ACCEPTED", "EDITED", "REJECTED", "FIX_RECORDED", "VERIFICATION_PENDING",
    "VERIFIED", "VERIFICATION_FAILED",
}


class CaseCreate(BaseModel):
    """Schema for creating a new case."""

    case_id: str = Field(..., min_length=1, max_length=50, description="Unique case identifier")
    category: str = Field(..., description="Network problem category")
    title: str = Field(..., min_length=3, max_length=255)
    symptom: str = Field(..., min_length=10)
    topology: str = Field(..., min_length=5)
    show_outputs: Dict[str, str] = Field(default_factory=dict)
    expected_fault: Optional[str] = None
    expected_osi_layer: Optional[str] = None
    concept: Optional[str] = None
    severity: str = Field(default="MEDIUM")
    expected_fix: List[str] = Field(default_factory=list)
    next_command: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    @field_validator("case_id")
    @classmethod
    def validate_case_id(cls, v: str) -> str:
        if not re.match(r"^[A-Z0-9\-_]{1,50}$", v.upper()):
            raise ValueError("case_id must contain only uppercase letters, digits, hyphens, underscores")
        return v.upper()

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        v = v.upper()
        if v not in VALID_SEVERITIES:
            raise ValueError(f"severity must be one of {VALID_SEVERITIES}")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        return v.upper().replace(" ", "_").replace("-", "_")


class CaseUpdate(BaseModel):
    """Schema for updating an existing case (partial update)."""

    title: Optional[str] = None
    symptom: Optional[str] = None
    topology: Optional[str] = None
    show_outputs: Optional[Dict[str, str]] = None
    expected_fault: Optional[str] = None
    expected_osi_layer: Optional[str] = None
    concept: Optional[str] = None
    severity: Optional[str] = None
    expected_fix: Optional[List[str]] = None
    next_command: Optional[str] = None
    tags: Optional[List[str]] = None

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.upper()
            if v not in VALID_SEVERITIES:
                raise ValueError(f"severity must be one of {VALID_SEVERITIES}")
        return v


class CaseResponse(BaseModel):
    """Case response schema."""

    id: int
    case_id: str
    category: str
    title: str
    symptom: str
    topology: str
    show_outputs: Dict[str, str]
    expected_fault: Optional[str]
    expected_osi_layer: Optional[str]
    concept: Optional[str]
    severity: str
    expected_fix: List[str]
    next_command: Optional[str]
    tags: List[str]
    workflow_state: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, case) -> "CaseResponse":
        return cls(
            id=case.id,
            case_id=case.case_id,
            category=case.category,
            title=case.title,
            symptom=case.symptom,
            topology=case.topology,
            show_outputs=case.show_outputs_dict,
            expected_fault=case.expected_fault,
            expected_osi_layer=case.expected_osi_layer,
            concept=case.concept,
            severity=case.severity,
            expected_fix=case.expected_fix_list,
            next_command=case.next_command,
            tags=case.tags_list,
            workflow_state=case.workflow_state,
            created_at=case.created_at,
            updated_at=case.updated_at,
        )


class CaseSummary(BaseModel):
    """Lightweight case summary for list views."""

    case_id: str
    category: str
    title: str
    severity: str
    concept: Optional[str]
    workflow_state: str
    created_at: datetime

    model_config = {"from_attributes": True}
