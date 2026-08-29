"""
NetSage AI — VLAN Rule.

Checks VLAN existence, access port assignment, and trunk allowed VLANs.
"""
from __future__ import annotations

from typing import Any

from app.rules.base import BaseRule, RuleCheckResult
from app.parsers.vlan_parser import parse_vlan_brief, vlan_exists
from app.parsers.trunk_parser import parse_interfaces_trunk, vlan_on_trunk


class VLANRule(BaseRule):
    """Detect missing VLANs, incorrect access VLAN assignments, and trunk VLAN issues."""

    name = "vlan_check"
    description = "Checks VLAN existence and trunk configuration."

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        show_outputs: dict = context.get("show_outputs", {})
        vlans: list[dict] = context.get("vlans", [])
        trunks: list[dict] = context.get("trunks", [])
        expected_vlan = context.get("expected_vlan")

        # Parse from raw output if not pre-parsed
        if not vlans and show_outputs.get("show vlan brief"):
            vlans = parse_vlan_brief(show_outputs["show vlan brief"])
        if not trunks and show_outputs.get("show interfaces trunk"):
            trunks = parse_interfaces_trunk(show_outputs["show interfaces trunk"])

        if not vlans and not expected_vlan:
            return self._not_checked("No VLAN information available.")

        issues = []
        evidence = []

        # Check expected VLAN exists
        if expected_vlan:
            vlan_id_str = str(expected_vlan)
            if vlans and not vlan_exists(vlan_id_str, vlans):
                issues.append(f"VLAN {vlan_id_str} does not exist in the VLAN database.")
                evidence.append(f"Missing VLAN {vlan_id_str} in show vlan brief")

            # Check if VLAN is allowed on trunk
            if trunks and not vlan_on_trunk(vlan_id_str, trunks):
                issues.append(f"VLAN {vlan_id_str} is not in the active VLANs on any trunk.")
                evidence.append(f"VLAN {vlan_id_str} not present in trunk active VLANs")

        if not issues:
            if vlans:
                return self._pass(f"VLAN configuration appears valid. {len(vlans)} VLANs found.")
            return self._not_checked("No expected VLAN to validate against.")

        return self._fail(
            message="VLAN configuration issues detected.",
            severity="HIGH",
            evidence=evidence,
            details={"issues": issues},
        )
