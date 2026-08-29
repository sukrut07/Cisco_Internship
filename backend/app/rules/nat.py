"""
NetSage AI — NAT Rule.

Detects missing NAT translations when inside-outside connectivity is expected.
"""
from __future__ import annotations

from typing import Any

from app.rules.base import BaseRule, RuleCheckResult
from app.parsers.nat_parser import parse_nat_translations, parse_nat_statistics


class NATRule(BaseRule):
    """Detect missing NAT translations."""

    name = "nat_check"
    description = "Detects missing NAT translations and NAT configuration issues."

    _NAT_KEYWORDS = ["nat", "internet", "outside", "translation", "overload", "pat"]

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        show_outputs: dict = context.get("show_outputs", {})
        nat_translations: list[dict] = context.get("nat_translations", [])
        symptom: str = (context.get("symptom") or "").lower()

        if not nat_translations:
            raw = show_outputs.get("show ip nat translations", "")
            if raw:
                nat_translations = parse_nat_translations(raw)

        nat_stats = {}
        raw_stats = show_outputs.get("show ip nat statistics", "")
        if raw_stats:
            nat_stats = parse_nat_statistics(raw_stats)

        nat_relevant = any(kw in symptom for kw in self._NAT_KEYWORDS)

        if not show_outputs.get("show ip nat translations") and not nat_stats:
            if not nat_relevant:
                return self._not_checked("No NAT evidence available.")

        evidence = []
        issues = []

        if nat_relevant and len(nat_translations) == 0:
            issues.append("NAT translation table is empty.")
            evidence.append("Empty NAT translation table — no active translations.")

        misses = nat_stats.get("misses", 0)
        hits = nat_stats.get("hits", 0)
        if misses > 0 and hits == 0:
            issues.append(f"NAT has {misses} misses and 0 hits — translations may not be working.")
            evidence.append(f"NAT statistics: {hits} hits, {misses} misses")

        if not issues:
            if nat_translations:
                return self._pass(
                    f"NAT appears functional. {len(nat_translations)} active translation(s)."
                )
            return self._not_checked("Insufficient NAT evidence to make a determination.")

        return self._fail(
            message="Possible NAT translation failure.",
            severity="HIGH",
            evidence=evidence,
            details={"issues": issues, "nat_stats": nat_stats},
        )
