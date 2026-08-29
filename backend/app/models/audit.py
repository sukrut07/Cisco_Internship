"""
NetSage AI — Audit Log ORM Model.

Provides a complete, immutable audit trail for every significant event.
"""
from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLog(Base):
    """Immutable audit trail for the Responsible AI record."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(String(50), nullable=True, index=True)

    # Event types:
    # CASE_CREATED | DIAGNOSIS_REQUESTED | RULE_CHECK_COMPLETED |
    # AI_DIAGNOSIS_COMPLETED | COMPARISON_COMPLETED |
    # REVIEW_ACCEPTED | REVIEW_EDITED | REVIEW_REJECTED |
    # FIX_RECORDED | VERIFICATION_COMPLETED
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    actor: Mapped[str] = mapped_column(String(255), nullable=False, default="system")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # JSON-encoded event metadata dict — renamed to avoid SQLAlchemy reserved name clash
    event_metadata: Mapped[str] = mapped_column(Text, nullable=True, default="{}")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    __table_args__ = (
        Index("ix_audit_case_event", "case_id", "event_type"),
        Index("ix_audit_created_at", "created_at"),
    )

    @property
    def metadata_dict(self) -> dict:
        try:
            return json.loads(self.event_metadata or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}

    @metadata_dict.setter
    def metadata_dict(self, value: dict) -> None:
        self.event_metadata = json.dumps(value)

    def __repr__(self) -> str:
        return f"<AuditLog event={self.event_type} case={self.case_id}>"
