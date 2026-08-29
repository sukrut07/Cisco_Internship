"""
NetSage AI — Trunk Rule.

Detects trunk down and VLAN not allowed on trunk.
"""
from __future__ import annotations

from typing import Any

from app.rules.base import BaseRule, RuleCheckResult
from app.parsers.trunk_parser import parse_interfaces_trunk, vlan_on_trunk


class TrunkRule(BaseRule):
    """Check trunk status and VLAN allowed lists."""

    name = "trunk_check"
    description = "Detects trunk interfaces that are down or missing required VLANs."

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        show_outputs: dict = context.get("show_outputs", {})
        trunks: list[dict] = context.get("trunks", [])
        expected_vlan = context.get("expected_vlan")

        if not trunks:
            raw = show_outputs.get("show interfaces trunk", "")
            if raw:
                trunks = parse_interfaces_trunk(raw)

        if not trunks:
            return self._not_checked("No trunk interface data available.")

        issues = []
        evidence = []

        for trunk in trunks:
            iface = trunk.get("interface", "unknown")
            status = trunk.get("status", "").lower()

            if "trunking" not in status:
                issues.append(f"Trunk {iface} is not in trunking state: {status}")
                evidence.append(f"Trunk {iface} status: {status}")

        if expected_vlan:
            if not vlan_on_trunk(str(expected_vlan), trunks):
                issues.append(f"VLAN {expected_vlan} is not active on any trunk.")
                evidence.append(f"VLAN {expected_vlan} missing from trunk active VLANs")

        if not issues:
            return self._pass(
                f"{len(trunks)} trunk(s) operational. No issues detected.",
                evidence=[f"Trunk count: {len(trunks)}"],
            )

        return self._fail(
            message="Trunk configuration issues detected.",
            severity="HIGH",
            evidence=evidence,
            details={"issues": issues},
        )
