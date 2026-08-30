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
            .order_by(AuditLog.created_at.asc())
            .all()
        )

    def get_all_audit_logs(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 50,
        event_type: str | None = None,
        case_id: str | None = None,
        search: str | None = None,
    ) -> tuple[list[AuditLog], int]:
        """Return paginated audit log entries with optional filters."""
        q = db.query(AuditLog)

        if event_type and event_type != "ALL":
            q = q.filter(AuditLog.event_type == event_type)
        if case_id:
            q = q.filter(AuditLog.case_id == case_id.upper())
        if search:
            from sqlalchemy import or_
            q = q.filter(
                or_(
                    AuditLog.actor.ilike(f"%{search}%"),
                    AuditLog.description.ilike(f"%{search}%"),
                    AuditLog.case_id.ilike(f"%{search}%"),
                    AuditLog.event_type.ilike(f"%{search}%"),
                )
            )

        total = q.count()
        logs = (
            q.order_by(AuditLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return logs, total


audit_service = AuditService()
