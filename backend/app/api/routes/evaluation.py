"""
NetSage AI — Evaluation API Routes.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.dashboard_service import evaluation_service

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.post(
    "/run",
    summary="Run internal AI evaluation",
    description=(
        "Evaluates AI diagnoses against cases with known expected faults. "
        "Results are INTERNAL ONLY and not statistically calibrated accuracy measurements."
    ),
)
def run_evaluation(db: Session = Depends(get_db)):
    return evaluation_service.run_evaluation(db)


@router.get(
    "/summary",
    summary="Get evaluation summary",
)
def evaluation_summary(db: Session = Depends(get_db)):
    return evaluation_service.run_evaluation(db)
