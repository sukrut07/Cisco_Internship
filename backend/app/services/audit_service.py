"""
NetSage AI — Audit Service.

Creates immutable audit log entries for all significant events.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Service for creating audit log entries."""

    def log(
        self,
        db: Session,
        event_type: str,
        description: str,
        case_id: str | None = None,
        actor: str = "system",
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        entry = AuditLog(
            case_id=case_id,
            event_type=event_type,
            actor=actor,
            description=description,
        )
        entry.metadata_dict = metadata or {}
        db.add(entry)
        db.flush()  # Get ID without committing
        logger.info(
            "AUDIT | event=%s | case=%s | actor=%s | %s",
            event_type,
            case_id,
            actor,
            description,
        )
        return entry

    def get_case_audit_trail(self, db: Session, case_id: str) -> list[AuditLog]:
        """Return all audit events for a case, ordered by time."""
        return (
            db.query(AuditLog)
            .filter(AuditLog.case_id == case_id)
            .order_by(AuditLog.created_at)
            .all()
        )


audit_service = AuditService()
