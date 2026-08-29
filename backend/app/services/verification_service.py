"""
NetSage AI — Verification Service.
"""
from __future__ import annotations

import json
import logging

from sqlalchemy.orm import Session

from app.core.exceptions import ReviewNotFoundError, VerificationNotFoundError
from app.models.review import Review
from app.models.verification import Verification
from app.schemas.verification import VerificationCreate
from app.services.audit_service import audit_service
from app.services.case_service import case_service

logger = logging.getLogger(__name__)


class VerificationService:
    """Service for recording post-fix verification results."""

    def create_verification(
        self, db: Session, case_id: str, data: VerificationCreate
    ) -> Verification:
        """Record a verification result."""
        # Validate review belongs to this case
        review = db.query(Review).filter(
            Review.id == data.review_id,
            Review.case_id == case_id,
        ).first()
        if not review:
            raise ReviewNotFoundError(
                f"Review {data.review_id} not found for case {case_id}."
            )

        verification = Verification(
            case_id=case_id,
            review_id=data.review_id,
            verification_status=data.verification_status,
            verification_method=data.verification_method,
            verification_evidence=data.verification_evidence,
            before_state=json.dumps(data.before_state or {}),
            after_state=json.dumps(data.after_state or {}),
            verified_by=data.verified_by,
        )
        db.add(verification)
        db.flush()

        # Transition state
        new_state = (
            "VERIFIED" if data.verification_status == "SUCCESS" else "VERIFICATION_FAILED"
        )
        try:
            case_service.transition_state(db, case_id, "VERIFICATION_PENDING")
            case_service.transition_state(db, case_id, new_state)
        except Exception as exc:
            logger.warning("State transition failed: %s", exc)

        audit_service.log(
            db,
            event_type="VERIFICATION_COMPLETED",
            description=f"Verification {data.verification_status} by {data.verified_by} via {data.verification_method}",
            case_id=case_id,
            actor=data.verified_by,
            metadata={
                "review_id": data.review_id,
                "status": data.verification_status,
                "method": data.verification_method,
                "evidence": data.verification_evidence,
            },
        )

        logger.info(
            "Verification recorded: case=%s status=%s", case_id, data.verification_status
        )
        return verification

    def get_verification(self, db: Session, verification_id: int) -> Verification:
        """Return a verification by ID."""
        v = db.query(Verification).filter(Verification.id == verification_id).first()
        if not v:
            raise VerificationNotFoundError(f"Verification {verification_id} not found.")
        return v

    def get_case_verifications(self, db: Session, case_id: str) -> list[Verification]:
        """Return all verifications for a case."""
        return (
            db.query(Verification)
            .filter(Verification.case_id == case_id)
            .order_by(Verification.created_at.desc())
            .all()
        )


verification_service = VerificationService()
