"""
NetSage AI — Gateway Rule.

Checks whether host IP and default gateway are in the same subnet.
"""
from __future__ import annotations

from typing import Any

from app.rules.base import BaseRule, RuleCheckResult
from app.utils.ip_utils import same_subnet


class GatewayRule(BaseRule):
    """Verify that the default gateway is reachable within the host's subnet."""

    name = "gateway_mismatch"
    description = "Checks that the default gateway is within the host's subnet."

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        devices: list[dict] = context.get("devices", [])

        if not devices:
            return self._not_checked("No device configuration provided.")

        issues = []
        checked = 0

        for device in devices:
            ip = device.get("ip") or device.get("ip_address")
            mask = device.get("mask") or device.get("subnet_mask")
            gateway = device.get("gateway") or device.get("default_gateway")
            name = device.get("name", "unknown")

            if not ip or not mask or not gateway:
                continue

            checked += 1

            if not same_subnet(ip, gateway, mask):
                issues.append(
                    f"{name}: Gateway {gateway} is NOT in subnet {ip}/{mask}"
                )

        if checked == 0:
            return self._not_checked("No devices with gateway information found.")

        if not issues:
            return self._pass(f"All {checked} device(s) have valid gateway configurations.")

        return self._fail(
            message="Default gateway is outside the host subnet.",
            severity="HIGH",
            evidence=issues,
            details={"mismatch_count": len(issues)},
        )
