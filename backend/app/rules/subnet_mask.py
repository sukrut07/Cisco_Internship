"""
NetSage AI — Subnet Mask Rule.
"""
from __future__ import annotations

from typing import Any

from app.rules.base import BaseRule, RuleCheckResult
from app.utils.ip_utils import get_network_for_host, is_valid_ip, is_valid_network


class SubnetMaskRule(BaseRule):
    """Validate that host IPs and subnet masks are consistent with expected networks."""

    name = "subnet_mask"
    description = "Checks IP address and subnet mask consistency."

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        devices: list[dict] = context.get("devices", [])

        if not devices:
            return self._not_checked("No device configuration provided.")

        issues = []
        checked = 0

        for device in devices:
            ip = device.get("ip") or device.get("ip_address")
            mask = device.get("mask") or device.get("subnet_mask")
            expected_network = device.get("expected_network") or device.get("network")
            name = device.get("name", "unknown")

            if not ip or not mask:
                continue

            checked += 1

            if not is_valid_ip(ip):
                issues.append(f"{name}: Invalid IP address '{ip}'")
                continue

            actual_network = get_network_for_host(ip, mask)
            if actual_network is None:
                issues.append(f"{name}: Invalid subnet mask '{mask}'")
                continue

            if expected_network:
                if not is_valid_network(expected_network):
                    issues.append(f"{name}: Invalid expected network '{expected_network}'")
                    continue
                if actual_network != expected_network:
                    issues.append(
                        f"{name}: IP {ip}/{mask} belongs to {actual_network}, "
                        f"expected {expected_network}"
                    )

        if checked == 0:
            return self._not_checked("No devices with IP/mask information found.")

        if not issues:
            return self._pass(f"All {checked} device(s) have valid subnet configurations.")

        return self._fail(
            message=f"Subnet mask inconsistencies detected.",
            severity="HIGH",
            evidence=issues,
            details={"issue_count": len(issues)},
        )
