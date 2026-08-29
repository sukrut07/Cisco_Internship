"""
NetSage AI — Review Pydantic Schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

VALID_DECISIONS = {"ACCEPTED", "EDITED", "REJECTED"}


class EditedDiagnosis(BaseModel):
    """Human-edited diagnosis data."""

    root_cause: str
    confidence: str
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    osi_layer: Optional[str] = None
    concept: Optional[str] = None
    next_command: Optional[str] = None
    fix_steps: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


class ReviewCreate(BaseModel):
    """Schema for submitting a human review."""

    diagnosis_id: int
    decision: str
    edited_diagnosis: Optional[EditedDiagnosis] = None
    reviewer: str = Field(default="anonymous", max_length=255)
    review_reason: Optional[str] = None
    review_notes: Optional[str] = None

    @field_validator("decision")
    @classmethod
    def validate_decision(cls, v: str) -> str:
        v = v.upper()
        if v not in VALID_DECISIONS:
            raise ValueError(f"decision must be one of {VALID_DECISIONS}")
        return v

    def model_post_init(self, __context: Any) -> None:
        # EDITED requires edited_diagnosis
        if self.decision == "EDITED" and not self.edited_diagnosis:
            raise ValueError("edited_diagnosis is required when decision is EDITED")


class FixRecordCreate(BaseModel):
    """Schema for recording a human-applied fix."""

    review_id: int
    commands: List[str] = Field(default_factory=list, description="Commands entered by human (not auto-executed)")
    description: str = Field(default="", description="Description of the fix performed")
    performed_by: str = Field(default="anonymous")


class ReviewResponse(BaseModel):
    """Review response schema."""

    id: int
    case_id: str
    diagnosis_id: int
    decision: str
    original_ai_diagnosis: Dict[str, Any]
    edited_diagnosis: Optional[Dict[str, Any]]
    final_diagnosis: Dict[str, Any]
    reviewer: str
    review_reason: Optional[str]
    review_notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, r) -> "ReviewResponse":
        return cls(
            id=r.id,
            case_id=r.case_id,
            diagnosis_id=r.diagnosis_id,
            decision=r.decision,
            original_ai_diagnosis=r.original_ai_diagnosis_dict,
            edited_diagnosis=r.edited_diagnosis_dict if r.edited_diagnosis else None,
            final_diagnosis=r.final_diagnosis_dict,
            reviewer=r.reviewer,
            review_reason=r.review_reason,
            review_notes=r.review_notes,
            created_at=r.created_at,
        )
