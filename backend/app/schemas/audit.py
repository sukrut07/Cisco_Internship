"""
NetSage AI — Audit Trail Pydantic Schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """Schema for returning an immutable audit log entry."""

    id: int
    case_id: Optional[str] = None
    event_type: str
    actor: str
    description: str
    metadata: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, log) -> "AuditLogResponse":
        return cls(
            id=log.id,
            case_id=log.case_id,
            event_type=log.event_type,
            actor=log.actor,
            description=log.description,
            metadata=log.metadata_dict,
            created_at=log.created_at,
        )
