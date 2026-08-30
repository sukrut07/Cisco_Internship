from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Case, Diagnosis, HumanReview
from ..schemas import HumanReviewCreate, HumanReviewResponse

router = APIRouter(prefix="/api/cases", tags=["reviews"])

@router.post("/{case_id}/review", response_model=HumanReviewResponse)
def submit_human_review(
    case_id: str, 
    review_in: HumanReviewCreate, 
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    latest_diag = db.query(Diagnosis).filter(Diagnosis.case_id == case_id).order_by(Diagnosis.created_at.desc()).first()
    diag_id = latest_diag.id if latest_diag else None

    decision_upper = review_in.decision.upper()
    if decision_upper not in ["ACCEPT", "EDIT", "REJECT"]:
        raise HTTPException(status_code=400, detail="Decision must be ACCEPT, EDIT, or REJECT")

    if decision_upper == "REJECT" and not (review_in.reviewer_comments and review_in.reviewer_comments.strip()):
        raise HTTPException(status_code=400, detail="Rejection requires a reviewer comment explaining the reason.")

    db_review = HumanReview(
        case_id=case_id,
        diagnosis_id=diag_id,
        decision=decision_upper,
        corrected_root_cause=review_in.corrected_root_cause,
        corrected_osi_layer=review_in.corrected_osi_layer,
        corrected_explanation=review_in.corrected_explanation,
        corrected_fix=review_in.corrected_fix,
        reviewer_comments=review_in.reviewer_comments,
        reviewer_name=review_in.reviewer_name or "Network Engineer"
    )

    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    return db_review


@router.get("/{case_id}/reviews", response_model=List[HumanReviewResponse])
def get_case_reviews(case_id: str, db: Session = Depends(get_db)):
    return db.query(HumanReview).filter(HumanReview.case_id == case_id).order_by(HumanReview.created_at.desc()).all()
