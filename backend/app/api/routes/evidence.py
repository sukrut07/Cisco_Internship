"""
NetSage AI — Evidence API Routes.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import CaseNotFoundError
from app.schemas.evidence import CaseEvidenceResponse
from app.services.evidence_service import evidence_service

router = APIRouter(tags=["Evidence"])


@router.get(
    "/cases/{case_id}/evidence",
    response_model=CaseEvidenceResponse,
    summary="Get all raw and structured evidence for a case",
    description="Returns the full set of Cisco show-command outputs and their parsed representations for a case.",
)
def get_case_evidence(case_id: str, db: Session = Depends(get_db)):
    try:
        return evidence_service.get_case_evidence(db, case_id)
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": exc.error_code, "message": exc.message})
