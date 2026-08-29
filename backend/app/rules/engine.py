"""
NetSage AI — Rule Engine.

Central orchestrator that runs all registered rules against a context.
Add new rules by instantiating them in the RULES list.
"""
from __future__ import annotations

import logging
from typing import Any

from app.rules.base import BaseRule, RuleCheckResult
from app.rules.duplicate_ip import DuplicateIPRule
from app.rules.subnet_mask import SubnetMaskRule
from app.rules.gateway import GatewayRule
from app.rules.interface_status import InterfaceStatusRule
from app.rules.vlan import VLANRule
from app.rules.routes import RouteRule
from app.rules.dhcp import DHCPRule
from app.rules.dns import DNSRule
from app.rules.acl import ACLRule
from app.rules.nat import NATRule
from app.rules.trunk import TrunkRule

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Registry — add new rules here
# ---------------------------------------------------------------------------

RULES: list[BaseRule] = [
    DuplicateIPRule(),
    SubnetMaskRule(),
    GatewayRule(),
    InterfaceStatusRule(),
    VLANRule(),
    RouteRule(),
    DHCPRule(),
    DNSRule(),
    ACLRule(),
    NATRule(),
    TrunkRule(),
]


class RuleEngine:
    """
    Runs all registered deterministic rules against a normalized context dict.

    Each rule is independent — a failure in one rule does not affect others.
    """

    def __init__(self, rules: list[BaseRule] | None = None) -> None:
        self.rules = rules if rules is not None else RULES

    def run_all(self, context: dict[str, Any]) -> list[RuleCheckResult]:
        """
        Execute all rules and return results.

        Never raises — errors are captured as NOT_CHECKED results.
        """
        results: list[RuleCheckResult] = []

        for rule in self.rules:
            try:
                result = rule.check(context)
                results.append(result)
                logger.debug(
                    "Rule '%s' → %s (%s)",
                    rule.name,
                    result.status,
                    result.severity,
                )
            except Exception as exc:
                logger.error("Rule '%s' raised an exception: %s", rule.name, exc)
                results.append(
                    RuleCheckResult(
                        rule_name=rule.name,
                        status="NOT_CHECKED",
                        severity="LOW",
                        message=f"Rule execution error: {exc}",
                    )
                )

        return results

    def get_failures(self, results: list[RuleCheckResult]) -> list[RuleCheckResult]:
        """Return only FAIL results."""
        return [r for r in results if r.status == "FAIL"]

    def get_warnings(self, results: list[RuleCheckResult]) -> list[RuleCheckResult]:
        """Return only WARNING results."""
        return [r for r in results if r.status == "WARNING"]

    def has_critical_failures(self, results: list[RuleCheckResult]) -> bool:
        """Return True if any FAIL result has severity HIGH or CRITICAL."""
        return any(
            r.status == "FAIL" and r.severity in ("HIGH", "CRITICAL")
            for r in results
        )

    def summary(self, results: list[RuleCheckResult]) -> dict[str, Any]:
        """Return a summary of rule execution results."""
        return {
            "total": len(results),
            "pass": sum(1 for r in results if r.status == "PASS"),
            "fail": sum(1 for r in results if r.status == "FAIL"),
            "warning": sum(1 for r in results if r.status == "WARNING"),
            "not_checked": sum(1 for r in results if r.status == "NOT_CHECKED"),
            "has_critical_failures": self.has_critical_failures(results),
        }


# Module-level singleton
rule_engine = RuleEngine()
