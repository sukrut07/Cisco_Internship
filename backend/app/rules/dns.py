"""
NetSage AI — DNS Rule.

Detects DNS failure via nslookup outputs, host table parsing, running-config,
and symptom patterns when IP connectivity exists but name resolution fails.
"""
from __future__ import annotations

import re
from typing import Any

from app.parsers.dns_parser import parse_nslookup, parse_show_hosts
from app.rules.base import BaseRule, RuleCheckResult


class DNSRule(BaseRule):
    """Detect DNS resolution failure from outputs and symptom evidence."""

    name = "dns_check"
    description = "Detects DNS failure when IP works but names don't resolve, or DNS output shows errors."

    _DNS_KEYWORDS = [
        "dns", "name resolution", "cannot resolve", "nslookup", "domain",
        "resolve", "hostname", "ping by name", "name server",
    ]
    _IP_WORKS_KEYWORDS = [
        "can ping", "can reach", "ip connectivity", "ping successful",
        "ping works", "can connect by ip",
    ]

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        symptom: str = (context.get("symptom") or "").lower()
        show_outputs: dict[str, str] = context.get("show_outputs") or {}

        evidence: list[str] = []
        issues: list[str] = []

        # 1. Check nslookup output if provided
        nslookup_out = show_outputs.get("nslookup") or show_outputs.get("nslookup test")
        if nslookup_out:
            ns_parsed = parse_nslookup(nslookup_out)
            if ns_parsed["timed_out"]:
                issues.append("DNS server timed out / did not respond to queries")
                evidence.append(f"nslookup: timeout reaching server {ns_parsed.get('server') or 'configured DNS'}")
            elif ns_parsed["server_failure"]:
                issues.append("DNS server returned SERVFAIL")
                evidence.append("nslookup: server failure reported")
            elif ns_parsed["non_existent_domain"]:
                issues.append("DNS record does not exist on server (NXDOMAIN)")
                evidence.append("nslookup: domain name not found")

        # 2. Check 'show hosts' output if provided
        hosts_out = show_outputs.get("show hosts") or show_outputs.get("show ip hosts")
        if hosts_out:
            hosts_parsed = parse_show_hosts(hosts_out)
            if not hosts_parsed["name_servers"] and "no ip domain lookup" in hosts_out.lower():
                issues.append("DNS lookup disabled ('no ip domain lookup') and no name servers configured")
                evidence.append("show hosts: no name servers configured")

        # 3. Check running-config for DNS settings
        run_cfg = (show_outputs.get("show running-config") or show_outputs.get("show run") or "").lower()
        if "no ip domain-lookup" in run_cfg or "no ip domain lookup" in run_cfg:
            evidence.append("Configuration has domain lookup disabled ('no ip domain-lookup')")

        # 4. Check symptom indications
        dns_issue = any(kw in symptom for kw in self._DNS_KEYWORDS)
        ip_works = any(kw in symptom for kw in self._IP_WORKS_KEYWORDS)

        if issues:
            return self._fail(
                message=f"DNS failure detected: {'; '.join(issues)}",
                severity="HIGH",
                evidence=evidence or issues,
                details={"layer": "Layer 7", "issues": issues},
            )

        if dns_issue and ip_works:
            return self._fail(
                message="DNS resolution failure detected — IP connectivity works but name resolution fails.",
                severity="MEDIUM",
                evidence=[
                    "Symptom indicates IP connectivity works",
                    "Symptom indicates DNS/name resolution fails",
                ] + evidence,
                details={"layer": "Layer 7"},
            )

        if dns_issue:
            return self._warning(
                message="Possible DNS issue detected in symptom. Verify IP connectivity separately.",
                severity="MEDIUM",
                evidence=["DNS-related keywords found in symptom"] + evidence,
            )

        if not show_outputs and not symptom:
            return self._not_checked("No DNS outputs or symptom provided.")

        return self._pass("No DNS failure pattern detected.")
