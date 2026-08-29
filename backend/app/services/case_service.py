"""
NetSage AI — Case Service.

Business logic for case CRUD and workflow state management.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.exceptions import CaseNotFoundError, DuplicateCaseError, InvalidWorkflowTransitionError
from app.models.case import Case
from app.schemas.case import CaseCreate, CaseUpdate
from app.services.audit_service import audit_service

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Workflow State Machine
# ---------------------------------------------------------------------------

VALID_TRANSITIONS: dict[str, list[str]] = {
    "CREATED": ["READY_FOR_DIAGNOSIS", "DIAGNOSING", "AWAITING_HUMAN_REVIEW"],
    "READY_FOR_DIAGNOSIS": ["DIAGNOSING", "AWAITING_HUMAN_REVIEW"],
    "DIAGNOSING": ["AWAITING_HUMAN_REVIEW"],
    "AWAITING_HUMAN_REVIEW": ["ACCEPTED", "EDITED", "REJECTED", "DIAGNOSING"],
    "ACCEPTED": ["FIX_RECORDED", "VERIFICATION_PENDING", "VERIFIED"],
    "EDITED": ["FIX_RECORDED", "VERIFICATION_PENDING", "VERIFIED"],
    "REJECTED": ["DIAGNOSING", "AWAITING_HUMAN_REVIEW", "READY_FOR_DIAGNOSIS"],
    "FIX_RECORDED": ["VERIFICATION_PENDING", "VERIFIED", "VERIFICATION_FAILED"],
    "VERIFICATION_PENDING": ["VERIFIED", "VERIFICATION_FAILED"],
    "VERIFIED": ["READY_FOR_DIAGNOSIS", "DIAGNOSING", "AWAITING_HUMAN_REVIEW"],
    "VERIFICATION_FAILED": ["VERIFICATION_PENDING", "DIAGNOSING", "READY_FOR_DIAGNOSIS"],
}


class CaseService:
    """Service for case CRUD and workflow transitions."""

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------

    def create_case(self, db: Session, data: CaseCreate) -> Case:
        """Create a new case."""
        existing = db.query(Case).filter(Case.case_id == data.case_id).first()
        if existing:
            raise DuplicateCaseError(f"Case '{data.case_id}' already exists.")

        case = Case(
            case_id=data.case_id,
            category=data.category,
            title=data.title,
            symptom=data.symptom,
            topology=data.topology,
            expected_fault=data.expected_fault,
            expected_osi_layer=data.expected_osi_layer,
            concept=data.concept,
            severity=data.severity,
            next_command=data.next_command,
            workflow_state="CREATED",
        )
        case.show_outputs_dict = data.show_outputs
        case.expected_fix_list = data.expected_fix
        case.tags_list = data.tags

        db.add(case)
        db.flush()

        audit_service.log(
            db,
            event_type="CASE_CREATED",
            description=f"Case {data.case_id} created: {data.title}",
            case_id=data.case_id,
            actor="api",
            metadata={"category": data.category, "severity": data.severity},
        )

        logger.info("Case created: %s", data.case_id)
        return case

    def get_case(self, db: Session, case_id: str) -> Case:
        """Return a case by case_id or raise CaseNotFoundError."""
        case = db.query(Case).filter(Case.case_id == case_id.upper()).first()
        if not case:
            raise CaseNotFoundError(f"Case '{case_id}' was not found.")
        return case

    def get_case_by_db_id(self, db: Session, id: int) -> Case:
        """Return a case by database primary key."""
        case = db.query(Case).filter(Case.id == id).first()
        if not case:
            raise CaseNotFoundError(f"Case with id {id} was not found.")
        return case

    def list_cases(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        concept: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[list[Case], int]:
        """Return paginated and filtered list of cases."""
        q = db.query(Case)

        if category:
            q = q.filter(Case.category == category.upper())
        if severity:
            q = q.filter(Case.severity == severity.upper())
        if concept:
            q = q.filter(Case.concept.ilike(f"%{concept}%"))
        if search:
            q = q.filter(
                or_(
                    Case.title.ilike(f"%{search}%"),
                    Case.symptom.ilike(f"%{search}%"),
                    Case.case_id.ilike(f"%{search}%"),
                )
            )

        total = q.count()
        cases = (
            q.order_by(Case.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return cases, total

    def update_case(self, db: Session, case_id: str, data: CaseUpdate) -> Case:
        """Update a case's fields."""
        case = self.get_case(db, case_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "show_outputs":
                case.show_outputs_dict = value
            elif field == "expected_fix":
                case.expected_fix_list = value
            elif field == "tags":
                case.tags_list = value
            else:
                setattr(case, field, value)

        db.flush()
        return case

    def delete_case(self, db: Session, case_id: str) -> None:
        """Delete a case."""
        case = self.get_case(db, case_id)
        db.delete(case)
        db.flush()
        logger.info("Case deleted: %s", case_id)

    # -------------------------------------------------------------------------
    # Workflow
    # -------------------------------------------------------------------------

    def transition_state(
        self, db: Session, case_id: str, new_state: str
    ) -> Case:
        """Transition a case to a new workflow state."""
        case = self.get_case(db, case_id)
        current = case.workflow_state

        allowed = VALID_TRANSITIONS.get(current, [])
        if new_state not in allowed:
            raise InvalidWorkflowTransitionError(
                f"Cannot transition case '{case_id}' from '{current}' to '{new_state}'. "
                f"Allowed: {allowed}"
            )

        case.workflow_state = new_state
        db.flush()
        logger.info("Case %s: %s -> %s", case_id, current, new_state)
        return case


case_service = CaseService()
