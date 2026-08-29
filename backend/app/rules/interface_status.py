"""
NetSage AI — Interface Status Rule.

Parses 'show ip interface brief' and classifies interface issues.
"""
from __future__ import annotations

from typing import Any

from app.rules.base import BaseRule, RuleCheckResult
from app.parsers.interface_parser import parse_ip_interface_brief, classify_interface_issue


class InterfaceStatusRule(BaseRule):
    """Detect interfaces that are administratively down, physically down, or up/down."""

    name = "interface_status"
    description = "Detects down interfaces from 'show ip interface brief'."

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        show_outputs: dict = context.get("show_outputs", {})
        interfaces: list[dict] = context.get("interfaces", [])

        # Try to get from already-parsed data first
        if not interfaces:
            raw = show_outputs.get("show ip interface brief", "")
            if raw:
                interfaces = parse_ip_interface_brief(raw)

        if not interfaces:
            return self._not_checked(
                "No 'show ip interface brief' output available."
            )

        admin_down = []
        physical_down = []
        up_down = []

        for iface in interfaces:
            status = (iface.get("status") or "").lower()
            protocol = (iface.get("protocol") or "").lower()
            name = iface.get("name", "unknown")

            issue = classify_interface_issue(status, protocol)
            if issue == "admin_down":
                admin_down.append(name)
            elif issue == "physical_down":
                physical_down.append(name)
            elif issue == "up_down":
                up_down.append(name)

        evidence = []
        if admin_down:
            evidence.append(f"Administratively down: {', '.join(admin_down)}")
        if physical_down:
            evidence.append(f"Physically down (down/down): {', '.join(physical_down)}")
        if up_down:
            evidence.append(f"Line protocol down (up/down): {', '.join(up_down)}")

        if not evidence:
            return self._pass("All interfaces are up/up.")

        # Severity: admin_down is most likely intentional, physical_down is serious
        severity = "HIGH" if physical_down or up_down else "MEDIUM"
        return self._fail(
            message="Interface issues detected.",
            severity=severity,
            evidence=evidence,
            details={
                "admin_down": admin_down,
                "physical_down": physical_down,
                "up_down": up_down,
            },
        )
