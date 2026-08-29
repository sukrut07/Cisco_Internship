"""
NetSage AI — Dashboard API Routes.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", summary="Dashboard summary metrics")
def dashboard_summary(db: Session = Depends(get_db)):
    return dashboard_service.get_summary(db)


@router.get("/categories", summary="Case distribution by category")
def category_distribution(db: Session = Depends(get_db)):
    return dashboard_service.get_category_distribution(db)


@router.get("/severity", summary="Case distribution by severity")
def severity_distribution(db: Session = Depends(get_db)):
    return dashboard_service.get_severity_distribution(db)


@router.get("/agreement", summary="AI-human agreement metrics")
def agreement_metrics(db: Session = Depends(get_db)):
    return dashboard_service.get_agreement_metrics(db)


@router.get("/rules", summary="Rule engine statistics")
def rule_stats(db: Session = Depends(get_db)):
    return dashboard_service.get_rule_stats(db)


@router.get("/timeline", summary="Activity timeline")
def timeline(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    return dashboard_service.get_timeline(db, days)
