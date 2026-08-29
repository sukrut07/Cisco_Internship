"""
NetSage AI — Review Service.

Enforces human review business rules:
- ACCEPTED → AI diagnosis becomes FINAL
- EDITED → Human diagnosis becomes FINAL
- REJECTED → AI cannot become FINAL; human diagnosis required
"""
from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import (
    DiagnosisNotFoundError,
    InvalidReviewStateError,
    ReviewNotFoundError,
)
from app.models.diagnosis import Diagnosis
from app.models.review import Review
from app.schemas.review import ReviewCreate
from app.services.audit_service import audit_service
from app.services.case_service import case_service

logger = logging.getLogger(__name__)


class ReviewService:
    """Service for human review business logic."""

    def create_review(self, db: Session, case_id: str, data: ReviewCreate) -> Review:
        """
        Submit a human review for a diagnosis.

        ACCEPTED  → final_diagnosis = AI diagnosis
        EDITED    → final_diagnosis = human-edited diagnosis
        REJECTED  → No final diagnosis created; further action required
        """
        # Validate diagnosis exists and belongs to this case
        diagnosis = db.query(Diagnosis).filter(
            Diagnosis.id == data.diagnosis_id,
            Diagnosis.case_id == case_id,
        ).first()

        if not diagnosis:
            raise DiagnosisNotFoundError(
                f"Diagnosis {data.diagnosis_id} not found for case {case_id}."
            )

        # Build original AI snapshot
        ai_snapshot = {
            "root_cause": diagnosis.root_cause,
            "confidence": diagnosis.confidence,
            "confidence_score": diagnosis.confidence_score,
            "evidence": diagnosis.evidence_list,
            "osi_layer": diagnosis.osi_layer,
            "concept": diagnosis.concept,
            "next_command": diagnosis.next_command,
            "fix_steps": diagnosis.fix_steps_list,
            "limitations": diagnosis.limitations_list,
        }

        # Determine final diagnosis
        if data.decision == "ACCEPTED":
            final = ai_snapshot.copy()
        elif data.decision == "EDITED":
            if not data.edited_diagnosis:
                raise InvalidReviewStateError("EDITED review requires edited_diagnosis.")
            final = data.edited_diagnosis.model_dump()
        elif data.decision == "REJECTED":
            final = {}  # No final diagnosis from AI
        else:
            raise InvalidReviewStateError(f"Invalid decision: {data.decision}")

        # Create review
        review = Review(
            case_id=case_id,
            diagnosis_id=data.diagnosis_id,
            decision=data.decision,
            reviewer=data.reviewer,
            review_reason=data.review_reason,
            review_notes=data.review_notes,
        )
        review.original_ai_diagnosis_dict = ai_snapshot
        review.edited_diagnosis_dict = (
            data.edited_diagnosis.model_dump() if data.edited_diagnosis else {}
        )
        review.final_diagnosis_dict = final

        db.add(review)
        db.flush()

        # Transition workflow state
        state_map = {
            "ACCEPTED": "ACCEPTED",
            "EDITED": "EDITED",
            "REJECTED": "REJECTED",
        }
        try:
            case_service.transition_state(db, case_id, state_map[data.decision])
        except Exception as exc:
            logger.warning("Could not transition state: %s", exc)

        # Audit event
        event_map = {
            "ACCEPTED": "REVIEW_ACCEPTED",
            "EDITED": "REVIEW_EDITED",
            "REJECTED": "REVIEW_REJECTED",
        }
        audit_service.log(
            db,
            event_type=event_map[data.decision],
            description=f"Review {data.decision} by {data.reviewer}: {data.review_reason or ''}",
            case_id=case_id,
            actor=data.reviewer,
            metadata={
                "diagnosis_id": data.diagnosis_id,
                "decision": data.decision,
                "reviewer": data.reviewer,
            },
        )

        logger.info("Review created: case=%s decision=%s reviewer=%s", case_id, data.decision, data.reviewer)
        return review

    def get_review(self, db: Session, review_id: int) -> Review:
        """Return a review by ID."""
        r = db.query(Review).filter(Review.id == review_id).first()
        if not r:
            raise ReviewNotFoundError(f"Review {review_id} not found.")
        return r

    def get_case_reviews(self, db: Session, case_id: str) -> list[Review]:
        """Return all reviews for a case."""
        return (
            db.query(Review)
            .filter(Review.case_id == case_id)
            .order_by(Review.created_at.desc())
            .all()
        )

    def record_fix(
        self,
        db: Session,
        case_id: str,
        review_id: int,
        commands: list[str],
        description: str,
        performed_by: str,
    ) -> None:
        """
        Record that a human applied a fix.

        IMPORTANT: This does NOT execute Cisco commands.
        It records the fix performed by the human engineer.
        Commands are stored as data strings only.
        """
        review = self.get_review(db, review_id)
        if review.case_id != case_id:
            raise ReviewNotFoundError(f"Review {review_id} does not belong to case {case_id}.")

        # Transition state
        try:
            case_service.transition_state(db, case_id, "FIX_RECORDED")
        except Exception as exc:
            logger.warning("State transition to FIX_RECORDED failed: %s", exc)

        audit_service.log(
            db,
            event_type="FIX_RECORDED",
            description=f"Fix recorded by {performed_by}: {description}",
            case_id=case_id,
            actor=performed_by,
            metadata={
                "review_id": review_id,
                "commands": commands,
                "description": description,
                "performed_by": performed_by,
                "applied_by": "HUMAN_APPLIED",  # Explicitly not auto-applied
            },
        )
        logger.info("Fix recorded: case=%s performed_by=%s", case_id, performed_by)


review_service = ReviewService()
