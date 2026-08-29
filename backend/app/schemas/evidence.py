"""
NetSage AI — Evidence Pydantic Schemas.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CaseEvidenceItem(BaseModel):
    """Structured evidence item for a single show command."""

    command: str = Field(..., description="Cisco command name (e.g. show ip route)")
    output: str = Field(..., description="Raw command output text")
    status: str = Field(default="ok", description="Parser status: ok | empty | unknown_format | error")
    parsed: Optional[Any] = Field(default=None, description="Structured parsed representation if supported")


class CaseEvidenceResponse(BaseModel):
    """Response schema for GET /cases/{case_id}/evidence."""

    case_id: str
    total_commands: int
    evidence: List[CaseEvidenceItem]
