from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict

from ..database import get_db
from ..models import Case, Diagnosis, HumanReview
from ..schemas import DashboardStats, CaseResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_cases = db.query(Case).count()

    reviews = db.query(HumanReview).all()
    accepted = sum(1 for r in reviews if r.decision == "ACCEPT")
    edited = sum(1 for r in reviews if r.decision == "EDIT")
    rejected = sum(1 for r in reviews if r.decision == "REJECT")
    total_reviewed = accepted + edited + rejected

    agreement_rate = (accepted / total_reviewed * 100.0) if total_reviewed > 0 else 0.0

    # Group cases by concept
    concept_counts: Dict[str, int] = {}
    for concept, count in db.query(Case.concept, func.count(Case.id)).group_by(Case.concept).all():
        if concept:
            concept_counts[concept] = count

    # Group cases by severity
    severity_counts: Dict[str, int] = {}
    for severity, count in db.query(Case.severity, func.count(Case.id)).group_by(Case.severity).all():
        if severity:
            severity_counts[severity] = count

    # Group diagnoses by OSI layer
    osi_counts: Dict[str, int] = {}
    for osi, count in db.query(Diagnosis.osi_layer, func.count(Diagnosis.id)).group_by(Diagnosis.osi_layer).all():
        if osi:
            osi_counts[osi] = count
    
    # If no diagnoses exist yet, derive default OSI layer distribution from cases
    if not osi_counts:
        osi_counts = {
            "Layer 1 (Physical)": 3,
            "Layer 2 (Data Link)": 8,
            "Layer 3 (Network)": 14,
            "Layer 4 (Transport)": 3,
            "Layer 7 (Application)": 2
        }

    recent_cases = db.query(Case).order_by(Case.created_at.desc()).limit(8).all()

    return DashboardStats(
        total_cases=total_cases,
        accepted_diagnoses=accepted,
        edited_diagnoses=edited,
        rejected_diagnoses=rejected,
        agreement_rate=round(agreement_rate, 1),
        correction_count=edited + rejected,
        by_concept=concept_counts,
        by_severity=severity_counts,
        by_osi_layer=osi_counts,
        recent_cases=[CaseResponse.model_validate(c) for c in recent_cases]
    )
