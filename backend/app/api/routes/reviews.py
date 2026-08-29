"""
NetSage AI — Reviews API Routes.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import (
    DiagnosisNotFoundError,
    InvalidReviewStateError,
    ReviewNotFoundError,
)
from app.schemas.review import FixRecordCreate, ReviewCreate, ReviewResponse
from app.services.review_service import review_service

router = APIRouter(tags=["Reviews"])


@router.post(
    "/cases/{case_id}/review",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit human review for a diagnosis",
    description=(
        "Submit ACCEPTED, EDITED, or REJECTED decision. "
        "ACCEPTED: AI diagnosis becomes final. "
        "EDITED: human diagnosis becomes final. "
        "REJECTED: no final diagnosis; AI cannot proceed. "
        "Human review is MANDATORY before any diagnosis becomes final."
    ),
)
def create_review(case_id: str, data: ReviewCreate, db: Session = Depends(get_db)):
    try:
        review = review_service.create_review(db, case_id, data)
        return ReviewResponse.from_orm_model(review)
    except DiagnosisNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": exc.error_code, "message": exc.message})
    except InvalidReviewStateError as exc:
        raise HTTPException(status_code=400, detail={"code": exc.error_code, "message": exc.message})
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"code": "REVIEW_ERROR", "message": str(exc)})


@router.get(
    "/cases/{case_id}/reviews",
    response_model=list[ReviewResponse],
    summary="Get all reviews for a case",
)
def get_case_reviews(case_id: str, db: Session = Depends(get_db)):
    reviews = review_service.get_case_reviews(db, case_id)
    return [ReviewResponse.from_orm_model(r) for r in reviews]


@router.get(
    "/reviews/{review_id}",
    response_model=ReviewResponse,
    summary="Get a specific review",
)
def get_review(review_id: int, db: Session = Depends(get_db)):
    try:
        review = review_service.get_review(db, review_id)
        return ReviewResponse.from_orm_model(review)
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": exc.error_code, "message": exc.message})


@router.post(
    "/cases/{case_id}/fix",
    status_code=status.HTTP_201_CREATED,
    summary="Record a human-applied fix",
    description=(
        "Records the fix performed by the human engineer. "
        "IMPORTANT: This does NOT execute any Cisco commands. "
        "Commands are stored as data strings only. "
        "The fix must be manually applied by a qualified network engineer."
    ),
)
def record_fix(case_id: str, data: FixRecordCreate, db: Session = Depends(get_db)):
    try:
        review_service.record_fix(
            db, case_id, data.review_id, data.commands, data.description, data.performed_by
        )
        return {
            "message": "Fix recorded successfully.",
            "case_id": case_id,
            "review_id": data.review_id,
            "performed_by": data.performed_by,
            "applied_by": "HUMAN_APPLIED",
            "note": "Commands were NOT automatically executed. Human applied manually.",
        }
    except ReviewNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": exc.error_code, "message": exc.message})
