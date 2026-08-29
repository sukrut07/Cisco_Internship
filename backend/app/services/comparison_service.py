"""
NetSage AI — Comparison Service.

Compares AI diagnosis findings with deterministic rule engine findings.
"""
from __future__ import annotations

import logging
from typing import Any

from app.rules.base import RuleCheckResult

logger = logging.getLogger(__name__)

# Keywords mapping rule names to concept domains
RULE_CONCEPT_MAP = {
    "missing_route": ["routing", "route", "static", "ospf", "eigrp"],
    "gateway_mismatch": ["gateway", "default gateway"],
    "duplicate_ip": ["ip", "addressing", "duplicate"],
    "subnet_mask": ["subnet", "mask", "addressing"],
    "interface_status": ["interface", "physical", "admin", "layer 1", "layer 2"],
    "vlan_check": ["vlan", "layer 2"],
    "trunk_check": ["trunk", "trunking", "vlan"],
    "dhcp_check": ["dhcp", "apipa", "169.254"],
    "dns_check": ["dns", "name resolution", "layer 7"],
    "acl_blocking": ["acl", "access list", "layer 4", "blocked"],
    "nat_check": ["nat", "pat", "translation"],
}


class ComparisonService:
    """Compares AI diagnosis with deterministic rule findings."""

    def compare(
        self,
        ai_root_cause: str,
        ai_osi_layer: str | None,
        rule_results: list[RuleCheckResult],
        grounding_status: str,
        expected_fault: str | None = None,
    ) -> dict[str, Any]:
        """
        Compare AI output with rule engine results.

        Returns a comparison dict including agreement type and conflicts.
        Human review is ALWAYS required regardless of agreement level.
        """
        failed_rules = [r for r in rule_results if r.status == "FAIL"]
        rule_findings = [r.message for r in failed_rules]

        # Check semantic agreement
        agreement, agreement_type, conflicts = self._check_agreement(
            ai_root_cause, ai_osi_layer, failed_rules
        )

        # Check expected fault match (for evaluation)
        expected_match = None
        if expected_fault:
            expected_lower = expected_fault.lower()
            ai_lower = ai_root_cause.lower()
            # Rough keyword overlap
            expected_words = set(expected_lower.split())
            ai_words = set(ai_lower.split())
            overlap = expected_words & ai_words
            expected_match = len(overlap) >= 2

        result = {
            "agreement": agreement,
            "agreement_type": agreement_type,
            "ai_root_cause": ai_root_cause,
            "rule_findings": rule_findings,
            "conflicts": conflicts,
            "grounding_status": grounding_status,
            "failed_rule_count": len(failed_rules),
            "expected_match": expected_match,
            "requires_human_review": True,  # ALWAYS mandatory
        }

        logger.info(
            "Comparison: agreement=%s type=%s grounding=%s",
            agreement,
            agreement_type,
            grounding_status,
        )

        return result

    def _check_agreement(
        self,
        ai_root_cause: str,
        ai_osi_layer: str | None,
        failed_rules: list[RuleCheckResult],
    ) -> tuple[bool, str, list[str]]:
        """
        Determine agreement type between AI and rules.

        Returns (agreement: bool, agreement_type: str, conflicts: list[str])
        """
        if not failed_rules:
            # No rule failures — could be that rules don't have enough evidence
            return True, "NO_RULE_EVIDENCE", []

        ai_lower = ai_root_cause.lower()
        agreements = []
        conflicts = []

        for rule in failed_rules:
            rule_keywords = RULE_CONCEPT_MAP.get(rule.rule_name, [])
            matched = any(kw in ai_lower for kw in rule_keywords)

            if matched:
                agreements.append(rule.rule_name)
            else:
                conflicts.append(
                    f"Rule '{rule.rule_name}' flagged '{rule.message}' "
                    f"but AI diagnosis mentions '{ai_root_cause[:80]}'"
                )

        if len(agreements) == len(failed_rules):
            return True, "STRONG", []
        elif agreements:
            return True, "PARTIAL", conflicts
        else:
            return False, "CONFLICT", conflicts


comparison_service = ComparisonService()
