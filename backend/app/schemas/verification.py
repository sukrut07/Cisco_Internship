"""
NetSage AI — Verification Pydantic Schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, field_validator

VALID_STATUSES = {"SUCCESS", "FAILED", "PARTIAL", "NOT_VERIFIED"}
VALID_METHODS = {"PING", "TRACEROUTE", "SHOW_COMMAND", "MANUAL", "PACKET_TRACER", "OTHER"}


class VerificationCreate(BaseModel):
    """Schema for submitting a verification result."""

    review_id: int
    verification_status: str
    verification_method: str = "MANUAL"
    verification_evidence: Optional[str] = None
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    verified_by: str = "anonymous"

    @field_validator("verification_status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        v = v.upper()
        if v not in VALID_STATUSES:
            raise ValueError(f"verification_status must be one of {VALID_STATUSES}")
        return v

    @field_validator("verification_method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        v = v.upper()
        if v not in VALID_METHODS:
            raise ValueError(f"verification_method must be one of {VALID_METHODS}")
        return v


class VerificationResponse(BaseModel):
    """Verification response schema."""

    id: int
    case_id: str
    review_id: int
    verification_status: str
    verification_method: str
    verification_evidence: Optional[str]
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    verified_by: str
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, v) -> "VerificationResponse":
        return cls(
            id=v.id,
            case_id=v.case_id,
            review_id=v.review_id,
            verification_status=v.verification_status,
            verification_method=v.verification_method,
            verification_evidence=v.verification_evidence,
            before_state=v.before_state_dict,
            after_state=v.after_state_dict,
            verified_by=v.verified_by,
            created_at=v.created_at,
        )
