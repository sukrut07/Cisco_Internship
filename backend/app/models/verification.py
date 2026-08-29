"""
NetSage AI — Verification ORM Model.
"""
from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Verification(Base):
    """Stores post-fix verification results."""

    __tablename__ = "verifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("cases.case_id", ondelete="CASCADE"), nullable=False
    )
    review_id: Mapped[int] = mapped_column(
        ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False
    )

    # SUCCESS | FAILED | PARTIAL | NOT_VERIFIED
    verification_status: Mapped[str] = mapped_column(String(30), nullable=False)

    # PING | TRACEROUTE | SHOW_COMMAND | MANUAL | PACKET_TRACER | OTHER
    verification_method: Mapped[str] = mapped_column(String(50), nullable=False, default="MANUAL")

    verification_evidence: Mapped[str] = mapped_column(Text, nullable=True)

    # JSON snapshot of state before fix
    before_state: Mapped[str] = mapped_column(Text, nullable=True)
    # JSON snapshot of state after fix
    after_state: Mapped[str] = mapped_column(Text, nullable=True)

    verified_by: Mapped[str] = mapped_column(String(255), nullable=False, default="anonymous")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_verifications_case_id", "case_id"),
        Index("ix_verifications_review_id", "review_id"),
        Index("ix_verifications_status", "verification_status"),
    )

    @property
    def before_state_dict(self) -> dict:
        try:
            return json.loads(self.before_state or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}

    @property
    def after_state_dict(self) -> dict:
        try:
            return json.loads(self.after_state or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}

    def __repr__(self) -> str:
        return f"<Verification id={self.id} case={self.case_id} status={self.verification_status}>"
