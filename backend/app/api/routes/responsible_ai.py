"""
NetSage AI — Responsible AI API Routes.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/responsible-ai", tags=["Responsible AI"])


@router.get(
    "/summary",
    summary="Responsible AI metrics summary",
    description=(
        "Returns AI performance metrics including human correction rate and AI-human agreement rate. "
        "NOTE: These are internal evaluation metrics only, not statistically calibrated accuracy."
    ),
)
def responsible_ai_summary(db: Session = Depends(get_db)):
    return dashboard_service.get_responsible_ai_summary(db)


@router.get(
    "/corrections",
    summary="Cases where AI was corrected",
    description="Returns cases where the human reviewer edited or rejected the AI diagnosis.",
)
def ai_corrections(db: Session = Depends(get_db)):
    corrections = dashboard_service.get_corrections(db)
    return {
        "total_corrections": len(corrections),
        "corrections": corrections,
        "note": "Human corrections are valuable evaluation data for future improvement.",
    }
