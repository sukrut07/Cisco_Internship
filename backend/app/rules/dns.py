"""
NetSage AI — DNS Rule.

Detects DNS failure when IP connectivity exists but name resolution fails.
"""
from __future__ import annotations

from typing import Any

from app.rules.base import BaseRule, RuleCheckResult


class DNSRule(BaseRule):
    """Detect DNS resolution failure when IP connectivity is confirmed."""

    name = "dns_check"
    description = "Detects DNS failure when IP works but names don't resolve."

    _DNS_KEYWORDS = [
        "dns", "name resolution", "cannot resolve", "nslookup", "domain",
        "resolve", "hostname", "ping by name", "name server",
    ]
    _IP_WORKS_KEYWORDS = [
        "can ping", "can reach", "ip connectivity", "ping successful",
        "ping works", "can connect by ip",
    ]

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        symptom: str = (context.get("symptom") or "").lower()
        topology: str = (context.get("topology") or "").lower()

        if not symptom:
            return self._not_checked("No symptom provided.")

        dns_issue = any(kw in symptom for kw in self._DNS_KEYWORDS)
        ip_works = any(kw in symptom for kw in self._IP_WORKS_KEYWORDS)

        if not dns_issue:
            return self._not_checked("No DNS-related keywords found in symptom.")

        if dns_issue and ip_works:
            return self._fail(
                message="DNS resolution failure detected — IP connectivity works but name resolution fails.",
                severity="MEDIUM",
                evidence=[
                    "Symptom indicates IP connectivity works",
                    "Symptom indicates DNS/name resolution fails",
                ],
                details={"layer": "Layer 7"},
            )

        if dns_issue:
            return self._warning(
                message="Possible DNS issue detected in symptom. Verify IP connectivity separately.",
                severity="MEDIUM",
                evidence=["DNS-related keywords found in symptom"],
            )

        return self._pass("No DNS failure pattern detected.")
