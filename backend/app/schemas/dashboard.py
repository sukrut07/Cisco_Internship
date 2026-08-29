"""
NetSage AI — Dashboard Pydantic Schemas.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_cases: int
    total_diagnoses: int
    total_reviews: int
    accepted: int
    edited: int
    rejected: int
    agreement_rate: Optional[float]      # ACCEPTED / total_reviews
    human_correction_rate: Optional[float]  # (EDITED + REJECTED) / total_reviews
    high_severity_cases: int
    verified_cases: int


class CategoryDistribution(BaseModel):
    category: str
    count: int
    percentage: float


class SeverityDistribution(BaseModel):
    severity: str
    count: int
    percentage: float


class AgreementMetrics(BaseModel):
    total_reviewed: int
    accepted: int
    edited: int
    rejected: int
    agreement_rate: Optional[float]
    correction_rate: Optional[float]
    grounding_warnings: int
    rule_conflicts: int


class RuleStat(BaseModel):
    rule_name: str
    fail_count: int
    warning_count: int
    pass_count: int
    not_checked_count: int


class TimelinePoint(BaseModel):
    date: str
    cases_created: int
    diagnoses_run: int
    reviews_completed: int


class ResponsibleAISummary(BaseModel):
    total_diagnoses: int
    accepted: int
    edited: int
    rejected: int
    human_correction_rate: Optional[float]
    ai_human_agreement_rate: Optional[float]
    grounding_warnings: int
    rule_conflicts: int
    evaluation_note: str = (
        "These metrics represent internal evaluation only, "
        "not statistically calibrated accuracy measurements."
    )


class EvaluationSummary(BaseModel):
    cases_evaluated: int
    root_cause_match_rate: Optional[float]
    osi_layer_match_rate: Optional[float]
    concept_match_rate: Optional[float]
    evidence_grounding_rate: Optional[float]
    human_agreement_rate: Optional[float]
    evaluation_note: str = (
        "Internal evaluation based on a small dataset. "
        "Results are indicative only."
    )
