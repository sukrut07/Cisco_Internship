"""
NetSage AI — Review ORM Model.

Human review is MANDATORY. A diagnosis cannot become FINAL without one.
"""
from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Review(Base):
    """Stores human review decisions for AI diagnoses."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False, index=True
    )
    diagnosis_id: Mapped[int] = mapped_column(
        ForeignKey("diagnoses.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # ACCEPTED | EDITED | REJECTED
    decision: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # Snapshot of AI diagnosis at review time (JSON)
    original_ai_diagnosis: Mapped[str] = mapped_column(Text, nullable=True)

    # Human-edited diagnosis (JSON) — populated when decision == EDITED
    edited_diagnosis: Mapped[str] = mapped_column(Text, nullable=True)

    # The final diagnosis used — AI or human-edited (JSON)
    final_diagnosis: Mapped[str] = mapped_column(Text, nullable=True)

    reviewer: Mapped[str] = mapped_column(String(255), nullable=False, default="anonymous")
    review_reason: Mapped[str] = mapped_column(Text, nullable=True)
    review_notes: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_reviews_case_decision", "case_id", "decision"),
        Index("ix_reviews_created_at", "created_at"),
    )

    @property
    def original_ai_diagnosis_dict(self) -> dict:
        try:
            return json.loads(self.original_ai_diagnosis or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}

    @original_ai_diagnosis_dict.setter
    def original_ai_diagnosis_dict(self, value: dict) -> None:
        self.original_ai_diagnosis = json.dumps(value)

    @property
    def edited_diagnosis_dict(self) -> dict:
        try:
            return json.loads(self.edited_diagnosis or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}

    @edited_diagnosis_dict.setter
    def edited_diagnosis_dict(self, value: dict) -> None:
        self.edited_diagnosis = json.dumps(value)

    @property
    def final_diagnosis_dict(self) -> dict:
        try:
            return json.loads(self.final_diagnosis or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}

    @final_diagnosis_dict.setter
    def final_diagnosis_dict(self, value: dict) -> None:
        self.final_diagnosis = json.dumps(value)

    def __repr__(self) -> str:
        return f"<Review id={self.id} case={self.case_id} decision={self.decision}>"
