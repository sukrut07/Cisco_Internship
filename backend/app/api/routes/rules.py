"""
NetSage AI — Rules API Routes.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.rule_result import RuleResult
from app.schemas.rules import RuleResultResponse

router = APIRouter(tags=["Rules"])


@router.get(
    "/cases/{case_id}/rules",
    response_model=list[RuleResultResponse],
    summary="Get rule check results for a case",
)
def get_case_rules(case_id: str, db: Session = Depends(get_db)):
    results = (
        db.query(RuleResult)
        .filter(RuleResult.case_id == case_id)
        .order_by(RuleResult.created_at.desc())
        .all()
    )
    return [RuleResultResponse.from_orm_model(r) for r in results]


@router.get(
    "/diagnoses/{diagnosis_id}/rules",
    response_model=list[RuleResultResponse],
    summary="Get rule results for a specific diagnosis",
)
def get_diagnosis_rules(diagnosis_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(RuleResult)
        .filter(RuleResult.diagnosis_id == diagnosis_id)
        .all()
    )
    return [RuleResultResponse.from_orm_model(r) for r in results]
