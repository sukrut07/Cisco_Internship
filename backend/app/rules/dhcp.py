"""
NetSage AI — DHCP Rule.

Detects APIPA addresses, DHCP pool exhaustion, missing helper-addresses, and binding issues.
"""
from __future__ import annotations

import re
from typing import Any

from app.rules.base import BaseRule, RuleCheckResult
from app.utils.ip_utils import is_apipa_address, extract_ips_from_text


class DHCPRule(BaseRule):
    """Detect DHCP failure indicators: APIPA addresses, pool exhaustion, missing relay/pool."""

    name = "dhcp_check"
    description = "Detects APIPA (169.254.x.x), DHCP binding, pool exhaustion, and relay issues."

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        devices: list[dict] = context.get("devices", [])
        symptom: str = context.get("symptom", "")
        show_outputs: dict = context.get("show_outputs", {})
        dhcp_bindings: list[dict] = context.get("dhcp_bindings", [])

        issues = []
        evidence = []

        # 1. Check device IPs for APIPA
        for device in devices:
            ip = device.get("ip") or device.get("ip_address")
            name = device.get("name", "unknown")
            if ip and is_apipa_address(ip):
                issues.append(f"{name} has APIPA address {ip} — DHCP likely failed.")
                evidence.append(f"APIPA address detected: {ip} on {name}")

        # 2. Check IPs mentioned in symptom text
        for ip in extract_ips_from_text(symptom):
            if is_apipa_address(ip):
                issues.append(f"APIPA address {ip} mentioned in symptom — DHCP failure.")
                evidence.append(f"APIPA address in symptom: {ip}")

        # 3. Check show outputs for APIPA
        for cmd, output in show_outputs.items():
            if "ip interface" in cmd.lower() or "brief" in cmd.lower():
                for ip in extract_ips_from_text(output):
                    if is_apipa_address(ip):
                        issues.append(f"APIPA address {ip} in {cmd}")
                        evidence.append(f"APIPA in {cmd}: {ip}")

        # 4. Check DHCP pool exhaustion / utilization from show ip dhcp pool
        pool_out = show_outputs.get("show ip dhcp pool", "")
        if pool_out:
            # Check for 100% leased / 0 free addresses
            if "100%" in pool_out or re.search(r"Leased addresses\s*:\s*(\d+)\s+Free addresses\s*:\s*0\b", pool_out, re.IGNORECASE):
                issues.append("DHCP pool is exhausted (0 free addresses).")
                evidence.append("show ip dhcp pool: 0 free addresses remaining in pool.")

        # 5. Check running-config for DHCP relay (ip helper-address) if cross-router DHCP is indicated
        run_cfg = show_outputs.get("show running-config") or show_outputs.get("show run") or ""
        if run_cfg and ("relay" in symptom.lower() or "different subnet" in symptom.lower() or "remote dhcp" in symptom.lower()):
            if not re.search(r"ip\s+helper-address\b", run_cfg, re.IGNORECASE):
                issues.append("DHCP relay missing: no 'ip helper-address' configured on router interface.")
                evidence.append("Router configuration lacks 'ip helper-address'.")

        # 6. Check for empty DHCP binding table when bindings are expected
        if dhcp_bindings is not None and len(dhcp_bindings) == 0:
            if "dhcp" in symptom.lower() or "ip address" in symptom.lower():
                issues.append("DHCP binding table is empty — no active leases.")
                evidence.append("Empty DHCP binding table")

        if not issues:
            if not devices and not dhcp_bindings and not pool_out:
                return self._not_checked("No DHCP-relevant evidence available.")
            return self._pass("No DHCP failure indicators detected.")

        return self._fail(
            message=f"DHCP failure detected: {'; '.join(issues)}",
            severity="HIGH",
            evidence=evidence,
            details={"issues": issues},
        )
