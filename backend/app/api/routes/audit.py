"""
NetSage AI — Audit Trail API Routes.
"""
from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import CaseNotFoundError
from app.schemas.audit import AuditLogResponse
from app.services.audit_service import audit_service
from app.services.case_service import case_service

router = APIRouter(tags=["Audit"])


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
