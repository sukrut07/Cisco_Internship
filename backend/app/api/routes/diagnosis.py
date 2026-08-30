"""
NetSage AI — Diagnosis API Routes.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.exceptions import (
    AIAuthenticationError,
    AIProviderError,
    AIProviderTimeout,
    AIQuotaError,
    AIResponseParseError,
    AIUnavailableError,
    CaseNotFoundError,
    DiagnosisNotFoundError,
)
from app.schemas.diagnosis import DiagnoseRequest, DiagnoseResponse, DiagnosisResponse
from app.services.diagnosis_service import diagnosis_service

router = APIRouter(tags=["Diagnosis"])


@router.post(
    "/cases/{case_id}/diagnose",
    response_model=DiagnoseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run AI diagnosis for a case",
    description=(
        "Runs the complete diagnosis pipeline: rule checks + AI analysis + comparison. "
        "The result ALWAYS requires human review before becoming final. "
        "Human review is mandatory — AI cannot autonomously apply changes."
    ),
)
def diagnose_case(
    case_id: str,
    request: Optional[DiagnoseRequest] = None,
    db: Session = Depends(get_db),
):
    try:
        return diagnosis_service.run_diagnosis(db, case_id, request)
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": exc.error_code, "message": exc.message})
    except (AIProviderTimeout, AIQuotaError, AIUnavailableError, AIAuthenticationError, AIProviderError, AIResponseParseError) as exc:
        raise HTTPException(status_code=exc.status_code, detail={"code": exc.error_code, "message": exc.message})
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"code": "DIAGNOSIS_FAILED", "message": str(exc)},
        )


@router.get(
    "/cases/{case_id}/diagnoses",
    response_model=list[DiagnosisResponse],
    summary="Get all diagnoses for a case",
)
def get_case_diagnoses(case_id: str, db: Session = Depends(get_db)):
    try:
        diagnoses = diagnosis_service.get_case_diagnoses(db, case_id)
        return [DiagnosisResponse.from_orm_model(d) for d in diagnoses]
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": exc.error_code, "message": exc.message})


@router.get(
    "/diagnoses/{diagnosis_id}",
    response_model=DiagnosisResponse,
    summary="Get a specific diagnosis",
)
def get_diagnosis(diagnosis_id: int, db: Session = Depends(get_db)):
    try:
        d = diagnosis_service.get_diagnosis(db, diagnosis_id)
        return DiagnosisResponse.from_orm_model(d)
    except DiagnosisNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": exc.error_code, "message": exc.message})
