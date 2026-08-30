"""
NetSage AI — Verification API Routes.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, verify_api_key
from app.core.exceptions import ReviewNotFoundError
from app.schemas.verification import VerificationCreate, VerificationResponse
from app.services.verification_service import verification_service

router = APIRouter(tags=["Verification"])


@router.post(
    "/cases/{case_id}/verify",
    response_model=VerificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record post-fix verification result",
)
@router.post(
    "/cases/{case_id}/verification",
    response_model=VerificationResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_verification(
    case_id: str, data: VerificationCreate, db: Session = Depends(get_db)
):
    try:
        v = verification_service.create_verification(db, case_id, data)
        return VerificationResponse.from_orm_model(v)
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": exc.error_code, "message": exc.message})
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail={"code": "VERIFICATION_ERROR", "message": str(exc)}
        )


@router.get(
    "/cases/{case_id}/verifications",
    response_model=list[VerificationResponse],
    summary="Get all verifications for a case",
)
def get_case_verifications(case_id: str, db: Session = Depends(get_db)):
    vs = verification_service.get_case_verifications(db, case_id)
    return [VerificationResponse.from_orm_model(v) for v in vs]
