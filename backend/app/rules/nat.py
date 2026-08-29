"""
NetSage AI — NAT Rule.

Detects missing NAT translations, missing inside/outside interface designations,
and NAT configuration mismatches.
"""
from __future__ import annotations

import re
from typing import Any

from app.rules.base import BaseRule, RuleCheckResult
from app.parsers.nat_parser import parse_nat_translations, parse_nat_statistics


class NATRule(BaseRule):
    """Detect missing NAT translations and NAT configuration issues."""

    name = "nat_check"
    description = "Detects missing NAT translations, inside/outside mismatches, and NAT configuration issues."

    _NAT_KEYWORDS = ["nat", "internet", "outside", "translation", "overload", "pat", "public ip"]

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

        evidence = []
        issues = []

        # 1. Check running-config for NAT inside/outside interface statements
        run_cfg = show_outputs.get("show running-config") or show_outputs.get("show run") or ""
        if run_cfg:
            has_nat_inside = bool(re.search(r"ip\s+nat\s+inside\b", run_cfg, re.IGNORECASE))
            has_nat_outside = bool(re.search(r"ip\s+nat\s+outside\b", run_cfg, re.IGNORECASE))
            has_nat_source = bool(re.search(r"ip\s+nat\s+inside\s+source\b", run_cfg, re.IGNORECASE))

            if nat_relevant:
                if not has_nat_inside:
                    issues.append("Missing 'ip nat inside' on LAN interface.")
                    evidence.append("No 'ip nat inside' found in interface configuration.")
                if not has_nat_outside:
                    issues.append("Missing 'ip nat outside' on WAN interface.")
                    evidence.append("No 'ip nat outside' found in interface configuration.")
                if not has_nat_source and (has_nat_inside or has_nat_outside):
                    issues.append("Missing 'ip nat inside source ...' translation statement.")
                    evidence.append("No NAT source translation rule configured.")

        # 2. Check translation table
        if nat_relevant and len(nat_translations) == 0 and not issues:
            issues.append("NAT translation table is empty.")
            evidence.append("Empty NAT translation table — no active translations.")

        # 3. Check statistics
        misses = nat_stats.get("misses", 0)
        hits = nat_stats.get("hits", 0)
        if misses > 0 and hits == 0:
            issues.append(f"NAT has {misses} misses and 0 hits — translations may not be working.")
            evidence.append(f"NAT statistics: {hits} hits, {misses} misses")

        if not show_outputs.get("show ip nat translations") and not nat_stats and not run_cfg and not nat_relevant:
            return self._not_checked("No NAT evidence available.")

        if not issues:
            if nat_translations:
                return self._pass(
                    f"NAT appears functional. {len(nat_translations)} active translation(s)."
                )
            return self._not_checked("Insufficient NAT evidence to make a determination.")

        return self._fail(
            message=f"NAT failure detected: {'; '.join(issues)}",
            severity="HIGH",
            evidence=evidence,
            details={"issues": issues, "nat_stats": nat_stats},
        )
