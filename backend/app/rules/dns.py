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
    """
    Detect DNS resolution failure from outputs and symptom evidence.

    Distinguishes:
    - DNS unreachable (server timeout / connection refused)
    - DNS server misconfigured (no name-server, domain-lookup disabled)
    - DNS record missing (NXDOMAIN / server failure)
    - DNS not primary issue (Layer 1/2/3 broken, suppressing false positives)
    """

    name = "dns_check"
    description = "Detects DNS resolution failure, misconfiguration, or missing records while isolating Layer 1-3 root causes."

    _DNS_KEYWORDS = [
        "dns", "name resolution", "cannot resolve", "nslookup", "domain",
        "resolve", "hostname", "ping by name", "name server", "fqdn",
    ]
    _IP_WORKS_KEYWORDS = [
        "can ping", "can reach", "ip connectivity", "ping successful",
        "ping works", "can connect by ip", "ping by ip works", "ip ping succeeds",
    ]
    _L1_L3_DOWN_KEYWORDS = [
        "cannot ping default gateway", "gateway unreachable", "no ip address",
        "administratively down", "line protocol is down", "port down", "link down",
    ]

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        symptom: str = (context.get("symptom") or "").lower()
        show_outputs: dict[str, str] = context.get("show_outputs") or {}
        interfaces: list[dict] = context.get("interfaces") or []

        evidence: list[str] = []
        issues: list[str] = []
        dns_subtype = "UNKNOWN"

        # Check if underlying physical or IP connectivity is down
        has_admin_down = any(i.get("status") == "administratively down" for i in interfaces)
        has_proto_down = any(i.get("protocol") == "down" for i in interfaces)
        l1_l3_down = any(kw in symptom for kw in self._L1_L3_DOWN_KEYWORDS) or has_admin_down or (has_proto_down and not interfaces)

        # 1. Check nslookup output if provided
        nslookup_out = show_outputs.get("nslookup") or show_outputs.get("nslookup test") or show_outputs.get("nslookup server")
        if nslookup_out:
            ns_parsed = parse_nslookup(nslookup_out)
            if ns_parsed["timed_out"]:
                dns_subtype = "DNS_UNREACHABLE"
                issues.append("DNS server timed out / did not respond to queries")
                evidence.append(f"nslookup: timeout reaching DNS server {ns_parsed.get('server') or 'configured address'}")
            elif ns_parsed["server_failure"]:
                dns_subtype = "DNS_RECORD_MISSING"
                issues.append("DNS server returned SERVFAIL")
                evidence.append("nslookup: server failure reported for query")
            elif ns_parsed["non_existent_domain"]:
                dns_subtype = "DNS_RECORD_MISSING"
                issues.append("DNS record does not exist on server (NXDOMAIN)")
                evidence.append("nslookup: domain name not found in DNS zone")

        # 2. Check 'show hosts' or 'show ip hosts' output
        hosts_out = show_outputs.get("show hosts") or show_outputs.get("show ip hosts")
        if hosts_out:
            hosts_parsed = parse_show_hosts(hosts_out)
            if not hosts_parsed["name_servers"] and ("no ip domain lookup" in hosts_out.lower() or "domain lookup disabled" in hosts_out.lower()):
                dns_subtype = "DNS_MISCONFIGURED"
                issues.append("DNS lookup disabled ('no ip domain lookup') and no name servers configured")
                evidence.append("show hosts: no name servers configured and domain lookup disabled")

        # 3. Check running-config for DNS settings
        run_cfg = (show_outputs.get("show running-config") or show_outputs.get("show run") or "").lower()
        if "no ip domain-lookup" in run_cfg or "no ip domain lookup" in run_cfg:
            evidence.append("Configuration has domain lookup disabled ('no ip domain-lookup')")
            if not issues:
                dns_subtype = "DNS_MISCONFIGURED"
                issues.append("DNS lookup explicitly disabled in router configuration")
        elif "ip name-server" in run_cfg:
            evidence.append("Configuration defines 'ip name-server'")

        # 4. Check symptom indications
        dns_issue = any(kw in symptom for kw in self._DNS_KEYWORDS)
        ip_works = any(kw in symptom for kw in self._IP_WORKS_KEYWORDS)

        # If lower layers are completely down, DNS is likely not the primary issue
        if dns_issue and l1_l3_down and not ip_works and not issues:
            return self._warning(
                message="DNS symptoms noted, but Layer 1-3 network connectivity issues appear to be the primary blocker.",
                severity="LOW",
                evidence=["Symptom/interfaces indicate underlying network connectivity is down"] + evidence,
                details={"layer": "Layer 7", "subtype": "DNS_NOT_PRIMARY_ISSUE"},
            )

        if issues:
            return self._fail(
                message=f"DNS failure detected ({dns_subtype}): {'; '.join(issues)}",
                severity="HIGH",
                evidence=evidence or issues,
                details={"layer": "Layer 7", "subtype": dns_subtype, "issues": issues},
            )

        if dns_issue and ip_works:
            return self._fail(
                message="DNS resolution failure detected — IP connectivity works but name resolution fails.",
                severity="MEDIUM",
                evidence=[
                    "Symptom indicates IP connectivity works",
                    "Symptom indicates DNS/name resolution fails",
                ] + evidence,
                details={"layer": "Layer 7", "subtype": "DNS_RESOLUTION_FAILURE"},
            )

        if dns_issue:
            return self._warning(
                message="Possible DNS issue indicated in symptoms. Verify name server reachability.",
                severity="MEDIUM",
                evidence=["DNS-related keywords found in symptom"] + evidence,
                details={"layer": "Layer 7", "subtype": "DNS_POSSIBLE"},
            )

        if not show_outputs and not symptom:
            return self._not_checked("No DNS outputs or symptom provided.")

        return self._pass("No DNS failure pattern detected.")
