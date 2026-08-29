"""
NetSage AI — Cases API Routes.
"""
from __future__ import annotations

import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import CaseNotFoundError, DuplicateCaseError
from app.schemas.case import CaseCreate, CaseResponse, CaseSummary, CaseUpdate
from app.schemas.common import PaginatedResponse
from app.services.case_service import case_service

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post(
    "",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new case",
)
def create_case(data: CaseCreate, db: Session = Depends(get_db)):
    try:
        case = case_service.create_case(db, data)
        return CaseResponse.from_orm_model(case)
    except DuplicateCaseError as exc:
        raise HTTPException(status_code=409, detail={"code": exc.error_code, "message": exc.message})


@router.get(
    "",
    response_model=PaginatedResponse[CaseSummary],
    summary="List cases with filtering and pagination",
)
def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    concept: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    cases, total = case_service.list_cases(
        db, page=page, page_size=page_size,
        category=category, severity=severity, concept=concept, search=search
    )
    items = [
        CaseSummary(
            case_id=c.case_id,
            category=c.category,
            title=c.title,
            severity=c.severity,
            concept=c.concept,
            workflow_state=c.workflow_state,
            created_at=c.created_at,
        )
        for c in cases
    ]
    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        pages=max(1, math.ceil(total / page_size)),
    )


@router.get(
    "/{case_id}",
    response_model=CaseResponse,
    summary="Get a case by ID",
)
def get_case(case_id: str, db: Session = Depends(get_db)):
    try:
        case = case_service.get_case(db, case_id)
        return CaseResponse.from_orm_model(case)
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": exc.error_code, "message": exc.message})


@router.put(
    "/{case_id}",
    response_model=CaseResponse,
    summary="Update a case",
)
def update_case(case_id: str, data: CaseUpdate, db: Session = Depends(get_db)):
    try:
        case = case_service.update_case(db, case_id, data)
        return CaseResponse.from_orm_model(case)
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": exc.error_code, "message": exc.message})


@router.delete(
    "/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a case",
)
def delete_case(case_id: str, db: Session = Depends(get_db)):
    try:
        case_service.delete_case(db, case_id)
    except CaseNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": exc.error_code, "message": exc.message})
