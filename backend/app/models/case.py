"""
NetSage AI — Case ORM Model.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Case(Base):
    """Represents a network troubleshooting case."""

    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    symptom: Mapped[str] = mapped_column(Text, nullable=False)
    topology: Mapped[str] = mapped_column(Text, nullable=False)
    # JSON-encoded dict: {"show ip route": "...", ...}
    show_outputs: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    expected_fault: Mapped[str] = mapped_column(Text, nullable=True)
    expected_osi_layer: Mapped[str] = mapped_column(String(50), nullable=True)
    concept: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM", index=True)
    # JSON-encoded list of fix steps
    expected_fix: Mapped[str] = mapped_column(Text, nullable=True, default="[]")
    next_command: Mapped[str] = mapped_column(String(255), nullable=True)
    # JSON-encoded list of tags
    tags: Mapped[str] = mapped_column(Text, nullable=True, default="[]")
    # Workflow state
    workflow_state: Mapped[str] = mapped_column(String(50), nullable=False, default="CREATED")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Indexes
    __table_args__ = (
        Index("ix_cases_category_severity", "category", "severity"),
        Index("ix_cases_created_at", "created_at"),
    )

    # -------------------------------------------------------------------------
    # Helper properties for JSON fields
    # -------------------------------------------------------------------------

    @property
    def show_outputs_dict(self) -> dict:
        try:
            return json.loads(self.show_outputs or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}

    @show_outputs_dict.setter
    def show_outputs_dict(self, value: dict) -> None:
        self.show_outputs = json.dumps(value)

    @property
    def expected_fix_list(self) -> list:
        try:
            return json.loads(self.expected_fix or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    @expected_fix_list.setter
    def expected_fix_list(self, value: list) -> None:
        self.expected_fix = json.dumps(value)

    @property
    def tags_list(self) -> list:
        try:
            return json.loads(self.tags or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    @tags_list.setter
    def tags_list(self, value: list) -> None:
        self.tags = json.dumps(value)

    def __repr__(self) -> str:
        return f"<Case {self.case_id}: {self.title}>"
