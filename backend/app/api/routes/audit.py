"""
NetSage AI — Audit Trail API Routes.
"""
from __future__ import annotations

from typing import List, Optional
import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import CaseNotFoundError
from app.schemas.audit import AuditLogResponse
from app.schemas.common import PaginatedResponse
from app.services.audit_service import audit_service
from app.services.case_service import case_service

router = APIRouter(tags=["Audit"])


@router.get(
    "/audit/logs",
    response_model=PaginatedResponse[AuditLogResponse],
    summary="List all audit trail entries with filtering and pagination",
    description="Returns global audit events across all cases and operational actions.",
)
def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    event_type: Optional[str] = Query(None),
    case_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    logs, total = audit_service.get_all_audit_logs(
        db, page=page, page_size=page_size, event_type=event_type, case_id=case_id, search=search
    )
    items = [AuditLogResponse.from_orm_model(log) for log in logs]
    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        pages=max(1, math.ceil(total / page_size)),
    )


@router.get(
    "/cases/{case_id}/audit-trail",
    response_model=List[AuditLogResponse],
    summary="Get full immutable audit trail for a case",
    description="Returns all lifecycle events recorded for a case in chronological order.",
)
def get_case_audit_trail(case_id: str, db: Session = Depends(get_db)):
    # Verify case exists
    try:
        case_service.get_case(db, case_id)
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": exc.error_code, "message": exc.message})

    logs = audit_service.get_case_audit_trail(db, case_id)
    return [AuditLogResponse.from_orm_model(log) for log in logs]
