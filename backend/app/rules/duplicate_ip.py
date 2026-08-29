"""
NetSage AI — Duplicate IP Rule.
"""
from __future__ import annotations

from typing import Any

from app.rules.base import BaseRule, RuleCheckResult


class DuplicateIPRule(BaseRule):
    """Detect duplicate IP addresses across devices in the topology."""

    name = "duplicate_ip"
    description = "Checks for duplicate IP addresses across all devices."

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        devices: list[dict] = context.get("devices", [])

        if not devices:
            return self._not_checked("No device list provided.")

        ip_map: dict[str, list[str]] = {}
        for device in devices:
            ip = device.get("ip") or device.get("ip_address")
            name = device.get("name") or device.get("hostname", "unknown")
            if not ip:
                continue
            ip_map.setdefault(ip, []).append(name)

        duplicates = {ip: names for ip, names in ip_map.items() if len(names) > 1}

        if not duplicates:
            return self._pass("No duplicate IP addresses detected.")

        messages = []
        all_details = []
        for ip, names in duplicates.items():
            messages.append(f"Duplicate IP {ip} on: {', '.join(names)}")
            all_details.append({"ip": ip, "devices": names})

        return self._fail(
            message=f"Duplicate IP addresses detected: {'; '.join(messages)}",
            severity="HIGH",
            evidence=messages,
            details={"duplicates": all_details},
        )
