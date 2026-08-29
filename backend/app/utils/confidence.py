"""
NetSage AI — Diagnostic Confidence Utilities.

IMPORTANT: This is a *diagnostic confidence score*, not a probability of correctness.
It is a composite signal combining AI output, rule agreement, evidence grounding,
and optional expected-diagnosis matching.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


CONFIDENCE_THRESHOLDS = {
    "HIGH": 0.70,
    "MEDIUM": 0.45,
    "LOW": 0.0,
}


@dataclass
class ConfidenceSignals:
    """Input signals used to calculate the composite confidence score."""

    ai_confidence: str = "LOW"          # LOW | MEDIUM | HIGH (from AI)
    ai_confidence_score: float = 0.0    # 0.0–1.0 (from AI)
    rule_agreement: bool = False         # Did rule engine agree with AI?
    rule_fail_count: int = 0            # Number of FAIL/WARNING rules
    grounding_status: str = "UNKNOWN"   # GROUNDED | PARTIALLY_GROUNDED | UNGROUNDED | UNKNOWN
    expected_match: Optional[bool] = None  # None when expected answer is hidden


def _ai_score(ai_confidence: str, ai_score: float) -> float:
    """Normalize AI confidence to a 0–1 float."""
    base = {
        "HIGH": 0.8,
        "MEDIUM": 0.55,
        "LOW": 0.3,
    }.get(ai_confidence.upper(), 0.3)
    # Blend label with numeric score if provided
    if 0.0 < ai_score <= 1.0:
        return (base + ai_score) / 2.0
    return base


def _grounding_multiplier(grounding_status: str) -> float:
    return {
        "GROUNDED": 1.0,
        "PARTIALLY_GROUNDED": 0.80,
        "UNGROUNDED": 0.50,
        "UNKNOWN": 0.85,
    }.get(grounding_status.upper(), 0.85)


def calculate_confidence(signals: ConfidenceSignals) -> tuple[float, str]:
    """
    Calculate composite diagnostic confidence score and label.

    Returns (score: float 0.0-1.0, label: str LOW|MEDIUM|HIGH).
    """
    score = _ai_score(signals.ai_confidence, signals.ai_confidence_score)

    # Rule agreement boost
    if signals.rule_agreement:
        score = min(score + 0.10, 1.0)
    elif signals.rule_fail_count > 0:
        # Rules found issues but AI and rules disagree — slight penalty
        score = max(score - 0.05, 0.0)

    # Grounding multiplier
    score *= _grounding_multiplier(signals.grounding_status)

    # Expected match boost (only used in evaluation mode)
    if signals.expected_match is True:
        score = min(score + 0.08, 1.0)
    elif signals.expected_match is False:
        score = max(score - 0.15, 0.0)

    score = round(score, 4)

    # Determine label
    if score >= CONFIDENCE_THRESHOLDS["HIGH"]:
        label = "HIGH"
    elif score >= CONFIDENCE_THRESHOLDS["MEDIUM"]:
        label = "MEDIUM"
    else:
        label = "LOW"

    return score, label


def score_to_label(score: float) -> str:
    """Convert a confidence score to a label."""
    if score >= CONFIDENCE_THRESHOLDS["HIGH"]:
        return "HIGH"
    elif score >= CONFIDENCE_THRESHOLDS["MEDIUM"]:
        return "MEDIUM"
    return "LOW"
