"""
NetSage AI — VLAN Rule.

Checks VLAN existence, access port assignment, native VLAN, and trunk allowed VLANs.
"""
from __future__ import annotations

import re
from typing import Any

from app.rules.base import BaseRule, RuleCheckResult
from app.parsers.vlan_parser import parse_vlan_brief, vlan_exists
from app.parsers.trunk_parser import parse_interfaces_trunk, vlan_on_trunk


class VLANRule(BaseRule):
    """Detect missing VLANs, incorrect access VLAN assignments, native VLAN mismatches, and trunk VLAN issues."""

    name = "vlan_check"
    description = "Checks VLAN existence, trunk configuration, and access port assignments."

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

        issues = []
        evidence = []

        # 1. Native VLAN mismatch detection in trunk output or CDP/log output
        trunk_raw = (show_outputs.get("show interfaces trunk") or "").lower()
        log_raw = (show_outputs.get("show logging") or show_outputs.get("show log") or "").lower()
        if "%CDP-4-NATIVE_VLAN_MISMATCH" in trunk_raw or "native vlan mismatch" in trunk_raw or "native vlan mismatch" in log_raw:
            issues.append("Native VLAN mismatch detected between connected switchports.")
            evidence.append("Native VLAN mismatch message found in trunk/log outputs.")

        # 2. Access port switchport analysis from running-config or switchport output
        sw_output = show_outputs.get("show interfaces switchport") or show_outputs.get("show running-config") or ""
        if sw_output and expected_vlan:
            exp_str = str(expected_vlan)
            # Find access ports configured for a different VLAN
            access_matches = re.findall(r"switchport access vlan\s+(\d+)", sw_output, re.IGNORECASE)
            if access_matches and exp_str not in access_matches and not vlans:
                evidence.append(f"Switchport access VLAN is configured as {', '.join(access_matches)}, expected VLAN {exp_str}")

        # 3. Check expected VLAN exists
        if expected_vlan:
            vlan_id_str = str(expected_vlan)
            if vlans and not vlan_exists(vlan_id_str, vlans):
                issues.append(f"VLAN {vlan_id_str} does not exist in the VLAN database.")
                evidence.append(f"Missing VLAN {vlan_id_str} in show vlan brief")

            # Check if VLAN is allowed on trunk
            if trunks and not vlan_on_trunk(vlan_id_str, trunks):
                issues.append(f"VLAN {vlan_id_str} is not in the active VLANs on any trunk.")
                evidence.append(f"VLAN {vlan_id_str} not present in trunk active VLANs")

        if not vlans and not trunks and not expected_vlan and not issues:
            return self._not_checked("No VLAN information available.")

        if not issues:
            if vlans or trunks:
                return self._pass(f"VLAN configuration appears valid. {len(vlans)} VLANs found.")
            return self._not_checked("No expected VLAN to validate against.")

        return self._fail(
            message=f"VLAN configuration issues detected: {'; '.join(issues)}",
            severity="HIGH",
            evidence=evidence,
            details={"issues": issues},
        )
