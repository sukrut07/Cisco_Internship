from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..database import get_db
from ..models import Case, Diagnosis, HumanReview

router = APIRouter(prefix="/api/responsible-ai", tags=["responsible_ai"])

@router.get("", response_model=Dict[str, Any])
def get_responsible_ai_logs(db: Session = Depends(get_db)):
    reviews = db.query(HumanReview).order_by(HumanReview.created_at.desc()).all()
    
    total_reviewed = len(reviews)
    accepted_count = sum(1 for r in reviews if r.decision == "ACCEPT")
    edited_count = sum(1 for r in reviews if r.decision == "EDIT")
    rejected_count = sum(1 for r in reviews if r.decision == "REJECT")
    correction_count = edited_count + rejected_count

    agreement_rate = round((accepted_count / total_reviewed * 100.0), 1) if total_reviewed > 0 else 0.0
    correction_rate = round((correction_count / total_reviewed * 100.0), 1) if total_reviewed > 0 else 0.0

    corrections_log: List[Dict[str, Any]] = []

    for r in reviews:
        if r.decision in ["EDIT", "REJECT"]:
            case = db.query(Case).filter(Case.id == r.case_id).first()
            diagnosis = db.query(Diagnosis).filter(Diagnosis.id == r.diagnosis_id).first() if r.diagnosis_id else None
            
            orig_diag = diagnosis.root_cause if diagnosis else "Initial AI Diagnosis"
            
            if r.decision == "EDIT":
                human_corr = r.corrected_root_cause or r.corrected_explanation or "Human engineer corrected diagnosis details"
                final_diag = r.corrected_root_cause or orig_diag
            else:
                human_corr = "Diagnosis Rejected: " + (r.reviewer_comments or "Incorrect root cause hypothesis")
                final_diag = "Rejected by reviewer"

            corrections_log.append({
                "id": r.id,
                "case_id": r.case_id,
                "case_title": case.title if case else r.case_id,
                "decision": r.decision,
                "original_ai_diagnosis": orig_diag,
                "human_correction": human_corr,
                "reason_for_correction": r.reviewer_comments or "Human reviewer identified edge case mismatch",
                "date": r.created_at.strftime("%Y-%m-%d %H:%M UTC"),
                "reviewer": r.reviewer_name or "Senior NetEng Reviewer",
                "final_diagnosis": final_diag
            })

    return {
        "metrics": {
            "total_reviews": total_reviewed,
            "accepted_count": accepted_count,
            "edited_count": edited_count,
            "rejected_count": rejected_count,
            "correction_count": correction_count,
            "agreement_rate": agreement_rate,
            "correction_rate": correction_rate
        },
        "corrections_log": corrections_log
    }
