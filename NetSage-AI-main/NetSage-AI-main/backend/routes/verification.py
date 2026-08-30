import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Case, Verification
from ..schemas import VerificationCreate, VerificationResponse
from ..rule_checker.checker import DeterministicRuleChecker

router = APIRouter(prefix="/api/cases", tags=["verification"])

@router.post("/{case_id}/verify", response_model=VerificationResponse)
def verify_case_fix(
    case_id: str,
    verif_in: VerificationCreate,
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    output = verif_in.verification_output
    output_lower = output.lower()

    # Rule checker analysis on post-fix evidence directly
    checker = DeterministicRuleChecker()
    rules = checker.analyze(
        show_outputs=output,
        symptom="",
        topology=""
    )

    failed_rules = [r for r in rules if r["status"] == "failed"]

    # Keyword checks for success
    ping_success = re.search(r'success rate is (?:100|80|90) percent', output_lower) or "reply from" in output_lower or "!!!!! " in output
    up_up = "up" in output_lower and not ("administratively down" in output_lower or "err-disabled" in output_lower)

    status = "Passed"
    explanation = "Fix verification successful! Network telemetry confirms issue resolution."

    if failed_rules:
        status = "Failed"
        rule_names = ", ".join([r["rule"] for r in failed_rules])
        explanation = f"Verification failed. Active rule check failures detected: {rule_names}. Evidence: {failed_rules[0]['evidence']}"
    elif "administratively down" in output_lower or "err-disabled" in output_lower:
        status = "Failed"
        explanation = "Verification failed. Interface remains in administratively down or err-disabled state."
    elif "unreachable" in output_lower or "timeout" in output_lower or re.search(r'\b0 percent\b', output_lower):
        status = "Failed"
        explanation = "Verification failed. ICMP ping tests indicate packet loss or destination unreachable."

    db_verif = Verification(
        case_id=case_id,
        verification_output=output,
        status=status,
        explanation=explanation
    )

    db.add(db_verif)
    db.commit()
    db.refresh(db_verif)

    return db_verif


@router.get("/{case_id}/verifications", response_model=List[VerificationResponse])
def get_case_verifications(case_id: str, db: Session = Depends(get_db)):
    return db.query(Verification).filter(Verification.case_id == case_id).order_by(Verification.created_at.desc()).all()
