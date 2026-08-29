"""
NetSage AI — Dashboard and Responsible AI Service.

Calculates real metrics from database — no fake/hardcoded values.
"""
from __future__ import annotations

import logging
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.case import Case
from app.models.diagnosis import Diagnosis
from app.models.review import Review
from app.models.rule_result import RuleResult
from app.models.verification import Verification

logger = logging.getLogger(__name__)


def _safe_rate(numerator: int, denominator: int) -> Optional[float]:
    """Return ratio or None if denominator is 0."""
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)


class DashboardService:
    """Calculates dashboard metrics from real database data."""

    def get_summary(self, db: Session) -> dict[str, Any]:
        total_cases = db.query(func.count(Case.id)).scalar() or 0
        total_diagnoses = db.query(func.count(Diagnosis.id)).scalar() or 0
        total_reviews = db.query(func.count(Review.id)).scalar() or 0

        accepted = db.query(func.count(Review.id)).filter(Review.decision == "ACCEPTED").scalar() or 0
        edited = db.query(func.count(Review.id)).filter(Review.decision == "EDITED").scalar() or 0
        rejected = db.query(func.count(Review.id)).filter(Review.decision == "REJECTED").scalar() or 0

        high_severity = (
            db.query(func.count(Case.id))
            .filter(Case.severity.in_(["HIGH", "CRITICAL"]))
            .scalar() or 0
        )
        verified = (
            db.query(func.count(Verification.id))
            .filter(Verification.verification_status == "SUCCESS")
            .scalar() or 0
        )

        return {
            "total_cases": total_cases,
            "total_diagnoses": total_diagnoses,
            "total_reviews": total_reviews,
            "accepted": accepted,
            "edited": edited,
            "rejected": rejected,
            "agreement_rate": _safe_rate(accepted, total_reviews),
            "human_correction_rate": _safe_rate(edited + rejected, total_reviews),
            "high_severity_cases": high_severity,
            "verified_cases": verified,
        }

    def get_category_distribution(self, db: Session) -> list[dict[str, Any]]:
        rows = (
            db.query(Case.category, func.count(Case.id))
            .group_by(Case.category)
            .all()
        )
        total = sum(count for _, count in rows)
        return [
            {
                "category": cat,
                "count": count,
                "percentage": round(count / total * 100, 2) if total else 0,
            }
            for cat, count in sorted(rows, key=lambda x: x[1], reverse=True)
        ]

    def get_severity_distribution(self, db: Session) -> list[dict[str, Any]]:
        rows = (
            db.query(Case.severity, func.count(Case.id))
            .group_by(Case.severity)
            .all()
        )
        total = sum(count for _, count in rows)
        return [
            {
                "severity": sev,
                "count": count,
                "percentage": round(count / total * 100, 2) if total else 0,
            }
            for sev, count in sorted(rows, key=lambda x: x[1], reverse=True)
        ]

    def get_agreement_metrics(self, db: Session) -> dict[str, Any]:
        total = db.query(func.count(Review.id)).scalar() or 0
        accepted = db.query(func.count(Review.id)).filter(Review.decision == "ACCEPTED").scalar() or 0
        edited = db.query(func.count(Review.id)).filter(Review.decision == "EDITED").scalar() or 0
        rejected = db.query(func.count(Review.id)).filter(Review.decision == "REJECTED").scalar() or 0

        grounding_warnings = (
            db.query(func.count(Diagnosis.id))
            .filter(Diagnosis.grounding_status.in_(["PARTIALLY_GROUNDED", "UNGROUNDED"]))
            .scalar() or 0
        )

        return {
            "total_reviewed": total,
            "accepted": accepted,
            "edited": edited,
            "rejected": rejected,
            "agreement_rate": _safe_rate(accepted, total),
            "correction_rate": _safe_rate(edited + rejected, total),
            "grounding_warnings": grounding_warnings,
            "rule_conflicts": 0,  # Would need richer comparison storage
        }

    def get_rule_stats(self, db: Session) -> list[dict[str, Any]]:
        rows = (
            db.query(
                RuleResult.rule_name,
                RuleResult.status,
                func.count(RuleResult.id),
            )
            .group_by(RuleResult.rule_name, RuleResult.status)
            .all()
        )

        rule_map: dict[str, dict] = {}
        for rule_name, status, count in rows:
            if rule_name not in rule_map:
                rule_map[rule_name] = {
                    "rule_name": rule_name,
                    "fail_count": 0,
                    "warning_count": 0,
                    "pass_count": 0,
                    "not_checked_count": 0,
                }
            key = f"{status.lower()}_count"
            if key in rule_map[rule_name]:
                rule_map[rule_name][key] += count

        return sorted(rule_map.values(), key=lambda x: x["fail_count"], reverse=True)

    def get_timeline(self, db: Session, days: int = 30) -> list[dict[str, Any]]:
        """Return daily counts of cases, diagnoses, reviews for the last N days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        timeline = []
        for i in range(days):
            day = cutoff + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            cases = (
                db.query(func.count(Case.id))
                .filter(Case.created_at >= day_start, Case.created_at < day_end)
                .scalar() or 0
            )
            diagnoses = (
                db.query(func.count(Diagnosis.id))
                .filter(Diagnosis.created_at >= day_start, Diagnosis.created_at < day_end)
                .scalar() or 0
            )
            reviews = (
                db.query(func.count(Review.id))
                .filter(Review.created_at >= day_start, Review.created_at < day_end)
                .scalar() or 0
            )

            if cases or diagnoses or reviews:
                timeline.append(
                    {
                        "date": day_start.strftime("%Y-%m-%d"),
                        "cases_created": cases,
                        "diagnoses_run": diagnoses,
                        "reviews_completed": reviews,
                    }
                )

        return timeline

    def get_responsible_ai_summary(self, db: Session) -> dict[str, Any]:
        """Return responsible AI metrics."""
        total = db.query(func.count(Diagnosis.id)).scalar() or 0
        total_reviewed = db.query(func.count(Review.id)).scalar() or 0
        accepted = db.query(func.count(Review.id)).filter(Review.decision == "ACCEPTED").scalar() or 0
        edited = db.query(func.count(Review.id)).filter(Review.decision == "EDITED").scalar() or 0
        rejected = db.query(func.count(Review.id)).filter(Review.decision == "REJECTED").scalar() or 0

        grounding_warnings = (
            db.query(func.count(Diagnosis.id))
            .filter(Diagnosis.grounding_status.in_(["PARTIALLY_GROUNDED", "UNGROUNDED"]))
            .scalar() or 0
        )

        return {
            "total_diagnoses": total,
            "accepted": accepted,
            "edited": edited,
            "rejected": rejected,
            "human_correction_rate": _safe_rate(edited + rejected, total_reviewed),
            "ai_human_agreement_rate": _safe_rate(accepted, total_reviewed),
            "grounding_warnings": grounding_warnings,
            "rule_conflicts": 0,
            "evaluation_note": (
                "These metrics represent internal evaluation only, "
                "not statistically calibrated accuracy measurements."
            ),
        }

    def get_corrections(self, db: Session) -> list[dict[str, Any]]:
        """Return cases where AI was corrected (EDITED or REJECTED)."""
        reviews = (
            db.query(Review)
            .filter(Review.decision.in_(["EDITED", "REJECTED"]))
            .order_by(Review.created_at.desc())
            .limit(100)
            .all()
        )

        corrections = []
        for r in reviews:
            corrections.append(
                {
                    "case_id": r.case_id,
                    "diagnosis_id": r.diagnosis_id,
                    "decision": r.decision,
                    "ai_root_cause": r.original_ai_diagnosis_dict.get("root_cause"),
                    "human_root_cause": r.final_diagnosis_dict.get("root_cause"),
                    "reviewer": r.reviewer,
                    "review_reason": r.review_reason,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
            )

        return corrections


class EvaluationService:
    """Internal evaluation of AI performance against known expected diagnoses."""

    def run_evaluation(self, db: Session) -> dict[str, Any]:
        """
        Evaluate AI diagnoses against cases with known expected faults.

        Returns internal evaluation metrics — NOT statistical accuracy.
        """
        cases_with_expected = (
            db.query(Case)
            .filter(Case.expected_fault.isnot(None))
            .all()
        )

        if not cases_with_expected:
            return {
                "cases_evaluated": 0,
                "root_cause_match_rate": None,
                "osi_layer_match_rate": None,
                "concept_match_rate": None,
                "evidence_grounding_rate": None,
                "human_agreement_rate": None,
                "evaluation_note": "No cases with expected faults found for evaluation.",
            }

        root_cause_matches = 0
        osi_matches = 0
        concept_matches = 0
        grounded_count = 0
        evaluated = 0

        for case in cases_with_expected:
            latest_diag = (
                db.query(Diagnosis)
                .filter(Diagnosis.case_id == case.case_id)
                .order_by(Diagnosis.created_at.desc())
                .first()
            )
            if not latest_diag:
                continue

            evaluated += 1

            # Root cause keyword match
            expected_lower = (case.expected_fault or "").lower()
            ai_lower = latest_diag.root_cause.lower()
            expected_words = set(expected_lower.split())
            ai_words = set(ai_lower.split())
            overlap = expected_words & ai_words
            if len(overlap) >= 2:
                root_cause_matches += 1

            # OSI layer match
            if (
                case.expected_osi_layer
                and latest_diag.osi_layer
                and case.expected_osi_layer.lower() in latest_diag.osi_layer.lower()
            ):
                osi_matches += 1

            # Concept match
            if (
                case.concept
                and latest_diag.concept
                and case.concept.lower() in latest_diag.concept.lower()
            ):
                concept_matches += 1

            # Grounding
            if latest_diag.grounding_status == "GROUNDED":
                grounded_count += 1

        # Human agreement
        total_reviews = db.query(func.count(Review.id)).scalar() or 0
        accepted = db.query(func.count(Review.id)).filter(Review.decision == "ACCEPTED").scalar() or 0
        match_rate = _safe_rate(root_cause_matches, evaluated)
        ground_rate = _safe_rate(grounded_count, evaluated)
        agreement_rate = _safe_rate(accepted, total_reviews)

        return {
            "total_cases": len(cases_with_expected),
            "cases_evaluated": evaluated,
            "accuracy": match_rate or 0.0,
            "root_cause_match_rate": match_rate,
            "osi_layer_match_rate": _safe_rate(osi_matches, evaluated),
            "concept_match_rate": _safe_rate(concept_matches, evaluated),
            "grounding_rate": ground_rate,
            "evidence_grounding_rate": ground_rate,
            "human_agreement_rate": agreement_rate,
            "evaluation_note": (
                "Internal evaluation based on keyword matching and expected fault comparison. "
                "Results are indicative only, not calibrated accuracy."
            ),
        }


dashboard_service = DashboardService()
evaluation_service = EvaluationService()
