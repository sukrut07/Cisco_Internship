"""
NetSage AI — Diagnosis ORM Model.
"""
from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Diagnosis(Base):
    """Stores every AI-generated diagnosis — never overwritten, always traceable."""

    __tablename__ = "diagnoses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False, index=True
    )
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[str] = mapped_column(String(10), nullable=False)  # LOW|MEDIUM|HIGH
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # JSON-encoded list of evidence dicts
    evidence: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    osi_layer: Mapped[str] = mapped_column(String(50), nullable=True)
    concept: Mapped[str] = mapped_column(String(100), nullable=True)
    next_command: Mapped[str] = mapped_column(String(255), nullable=True)
    # JSON-encoded list of fix steps
    fix_steps: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    # JSON-encoded list of limitation strings
    limitations: Mapped[str] = mapped_column(Text, nullable=True, default="[]")

    # AI metadata
    ai_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=True)
    raw_response: Mapped[str] = mapped_column(Text, nullable=True)

    # Grounding metadata
    grounding_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="UNKNOWN"
    )  # GROUNDED|PARTIALLY_GROUNDED|UNGROUNDED|UNKNOWN

    # Computed confidence signals (JSON)
    confidence_signals: Mapped[str] = mapped_column(Text, nullable=True, default="{}")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_diagnoses_case_id_created", "case_id", "created_at"),
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
    def fix_steps_list(self) -> list:
        try:
            return json.loads(self.fix_steps or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    @fix_steps_list.setter
    def fix_steps_list(self, value: list) -> None:
        self.fix_steps = json.dumps(value)

    @property
    def limitations_list(self) -> list:
        try:
            return json.loads(self.limitations or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    @limitations_list.setter
    def limitations_list(self, value: list) -> None:
        self.limitations = json.dumps(value)

    @property
    def confidence_signals_dict(self) -> dict:
        try:
            return json.loads(self.confidence_signals or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}

    @confidence_signals_dict.setter
    def confidence_signals_dict(self, value: dict) -> None:
        self.confidence_signals = json.dumps(value)

    def __repr__(self) -> str:
        return f"<Diagnosis id={self.id} case={self.case_id} confidence={self.confidence}>"
