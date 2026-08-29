"""
NetSage AI — DHCP Rule.

Detects APIPA addresses and DHCP-related issues.
"""
from __future__ import annotations

from typing import Any

from app.rules.base import BaseRule, RuleCheckResult
from app.utils.ip_utils import is_apipa_address, extract_ips_from_text


class DHCPRule(BaseRule):
    """Detect DHCP failure indicators such as APIPA addresses."""

    name = "dhcp_check"
    description = "Detects APIPA (169.254.x.x) and DHCP binding issues."

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        devices: list[dict] = context.get("devices", [])
        symptom: str = context.get("symptom", "")
        show_outputs: dict = context.get("show_outputs", {})
        dhcp_bindings: list[dict] = context.get("dhcp_bindings", [])

        issues = []
        evidence = []

        # Check device IPs for APIPA
        for device in devices:
            ip = device.get("ip") or device.get("ip_address")
            name = device.get("name", "unknown")
            if ip and is_apipa_address(ip):
                issues.append(f"{name} has APIPA address {ip} — DHCP likely failed.")
                evidence.append(f"APIPA address detected: {ip} on {name}")

        # Check IPs mentioned in symptom text
        for ip in extract_ips_from_text(symptom):
            if is_apipa_address(ip):
                issues.append(f"APIPA address {ip} mentioned in symptom — DHCP failure.")
                evidence.append(f"APIPA address in symptom: {ip}")

        # Check show outputs for APIPA
        for cmd, output in show_outputs.items():
            if "ip interface" in cmd.lower() or "brief" in cmd.lower():
                for ip in extract_ips_from_text(output):
                    if is_apipa_address(ip):
                        issues.append(f"APIPA address {ip} in {cmd}")
                        evidence.append(f"APIPA in {cmd}: {ip}")

        # Check for empty DHCP binding table when bindings are expected
        if dhcp_bindings is not None and len(dhcp_bindings) == 0:
            # Only flag if DHCP is relevant
            if "dhcp" in symptom.lower() or "ip address" in symptom.lower():
                issues.append("DHCP binding table is empty — no active leases.")
                evidence.append("Empty DHCP binding table")

        if not issues:
            if not devices and not dhcp_bindings:
                return self._not_checked("No DHCP-relevant evidence available.")
            return self._pass("No DHCP failure indicators detected.")

        return self._fail(
            message="DHCP failure indicators detected.",
            severity="HIGH",
            evidence=evidence,
            details={"issues": issues},
        )
