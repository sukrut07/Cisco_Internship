"""
NetSage AI — Rule Result ORM Model.
"""
from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RuleResult(Base):
    """Stores the output of each deterministic rule check."""

    __tablename__ = "rule_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False, index=True
    )
    diagnosis_id: Mapped[int] = mapped_column(
        ForeignKey("diagnoses.id", ondelete="CASCADE"), nullable=True, index=True
    )
    rule_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # PASS | FAIL | WARNING | NOT_CHECKED
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, default="LOW"
    )  # LOW | MEDIUM | HIGH | CRITICAL
    message: Mapped[str] = mapped_column(Text, nullable=False)
    # JSON-encoded list of evidence strings
    evidence: Mapped[str] = mapped_column(Text, nullable=True, default="[]")
    # JSON-encoded dict of rule-specific details
    details: Mapped[str] = mapped_column(Text, nullable=True, default="{}")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_rule_results_case_diagnosis", "case_id", "diagnosis_id"),
    )

    @property
    def evidence_list(self) -> list:
        try:
            return json.loads(self.evidence or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    @evidence_list.setter
    def evidence_list(self, value: list) -> None:
        self.evidence = json.dumps(value)

    @property
    def details_dict(self) -> dict:
        try:
            return json.loads(self.details or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}

    @details_dict.setter
    def details_dict(self, value: dict) -> None:
        self.details = json.dumps(value)

    def __repr__(self) -> str:
        return f"<RuleResult rule={self.rule_name} status={self.status}>"
