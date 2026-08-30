"""
NetSage AI — Mock AI Provider.

Produces deterministic, realistic-looking diagnoses based on case category
and rule findings. Works without any API key or internet access.

The mock is clearly separated from real AI providers and labeled in all outputs.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from app.ai.base import BaseAIProvider, DiagnosisContext, AIProviderResponse
from app.ai.prompts import get_prompt_version

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mock diagnosis templates per category/concept
# ---------------------------------------------------------------------------

MOCK_DIAGNOSES: dict[str, dict[str, Any]] = {
    "routing": {
        "root_cause": "Missing route to destination network in routing table.",
        "confidence": "HIGH",
        "confidence_score": 0.87,
        "osi_layer": "Layer 3",
        "concept": "Static Routing",
        "next_command": "show ip route",
        "fix_steps": [
            "Identify the destination network that is unreachable.",
            "Verify the routing table with 'show ip route'.",
            "Configure the appropriate static or dynamic route.",
            "Verify the new route appears in the routing table.",
            "Test connectivity with ping/traceroute.",
        ],
        "limitations": [
            "Analysis based only on supplied show outputs.",
            "ACL blocking is not ruled out without 'show access-lists'.",
        ],
    },
    "vlan": {
        "root_cause": "VLAN not configured or not active on switch.",
        "confidence": "HIGH",
        "confidence_score": 0.85,
        "osi_layer": "Layer 2",
        "concept": "VLAN",
        "next_command": "show vlan brief",
        "fix_steps": [
            "Verify the VLAN exists with 'show vlan brief'.",
            "Create the VLAN if missing: 'vlan <id>'.",
            "Assign ports to the VLAN: 'switchport access vlan <id>'.",
            "Verify port assignments.",
            "Test connectivity.",
        ],
        "limitations": ["Trunk port configuration not analyzed without trunk output."],
    },
    "trunking": {
        "root_cause": "Trunk port not configured or VLAN not allowed on trunk.",
        "confidence": "HIGH",
        "confidence_score": 0.83,
        "osi_layer": "Layer 2",
        "concept": "802.1Q Trunking",
        "next_command": "show interfaces trunk",
        "fix_steps": [
            "Verify trunk configuration with 'show interfaces trunk'.",
            "Ensure trunk mode: 'switchport mode trunk'.",
            "Add required VLANs: 'switchport trunk allowed vlan add <id>'.",
            "Verify VLAN is active on trunk.",
            "Test inter-VLAN connectivity.",
        ],
        "limitations": ["Native VLAN mismatch cannot be ruled out."],
    },
    "inter_vlan_routing": {
        "root_cause": "Inter-VLAN routing not configured correctly — missing SVI or sub-interface.",
        "confidence": "HIGH",
        "confidence_score": 0.82,
        "osi_layer": "Layer 3",
        "concept": "Inter-VLAN Routing",
        "next_command": "show ip interface brief",
        "fix_steps": [
            "Verify SVIs or sub-interfaces exist for each VLAN.",
            "Ensure SVIs are in 'up/up' state.",
            "Verify IP routing is enabled: 'ip routing'.",
            "Check trunk configuration between switch and router.",
            "Test inter-VLAN ping.",
        ],
        "limitations": ["Without 'show ip interface brief' cannot confirm SVI status."],
    },
    "ip_addressing": {
        "root_cause": "Incorrect IP address or subnet mask configuration.",
        "confidence": "HIGH",
        "confidence_score": 0.88,
        "osi_layer": "Layer 3",
        "concept": "IP Addressing",
        "next_command": "show ip interface brief",
        "fix_steps": [
            "Verify IP configuration on all devices.",
            "Ensure IP addresses are in the correct subnet.",
            "Check for duplicate IP addresses.",
            "Correct any misconfigured addresses.",
            "Test connectivity.",
        ],
        "limitations": ["Physical layer issues not ruled out."],
    },
    "gateway": {
        "root_cause": "Default gateway is misconfigured or points to wrong subnet.",
        "confidence": "HIGH",
        "confidence_score": 0.90,
        "osi_layer": "Layer 3",
        "concept": "Default Gateway",
        "next_command": "show ip interface brief",
        "fix_steps": [
            "Verify the host's default gateway setting.",
            "Ensure gateway IP is in the same subnet as the host.",
            "Correct the gateway address if mismatched.",
            "Test gateway reachability with ping.",
            "Test end-to-end connectivity.",
        ],
        "limitations": [],
    },
    "dhcp": {
        "root_cause": "DHCP server not reachable or DHCP pool exhausted — host received APIPA address.",
        "confidence": "HIGH",
        "confidence_score": 0.84,
        "osi_layer": "Layer 3",
        "concept": "DHCP",
        "next_command": "show ip dhcp binding",
        "fix_steps": [
            "Verify DHCP server is running and reachable.",
            "Check DHCP pool configuration.",
            "Verify DHCP helper-address if server is on a different subnet.",
            "Release and renew DHCP lease on client.",
            "Check for IP address pool exhaustion.",
        ],
        "limitations": ["DHCP relay configuration not confirmed."],
    },
    "dns": {
        "root_cause": "DNS server unreachable or misconfigured — IP connectivity works but name resolution fails.",
        "confidence": "MEDIUM",
        "confidence_score": 0.65,
        "osi_layer": "Layer 7",
        "concept": "DNS",
        "next_command": "nslookup <hostname>",
        "fix_steps": [
            "Test DNS resolution with 'nslookup <hostname>'.",
            "Verify DNS server IP configuration on hosts.",
            "Test reachability of DNS server.",
            "Check DNS server configuration.",
            "Try alternate DNS server if available.",
        ],
        "limitations": ["DNS server configuration not directly analyzable from show outputs."],
    },
    "static_routing": {
        "root_cause": "Static route missing or incorrectly configured for destination network.",
        "confidence": "HIGH",
        "confidence_score": 0.86,
        "osi_layer": "Layer 3",
        "concept": "Static Routing",
        "next_command": "show ip route",
        "fix_steps": [
            "Review routing table with 'show ip route'.",
            "Identify the missing destination network.",
            "Add the correct static route: 'ip route <network> <mask> <next-hop>'.",
            "Verify route appears in routing table.",
            "Test end-to-end connectivity.",
        ],
        "limitations": [],
    },
    "dynamic_routing": {
        "root_cause": "OSPF/EIGRP neighbor adjacency not formed — routing updates not being exchanged.",
        "confidence": "MEDIUM",
        "confidence_score": 0.70,
        "osi_layer": "Layer 3",
        "concept": "Dynamic Routing",
        "next_command": "show ip ospf neighbor",
        "fix_steps": [
            "Verify neighbor adjacency: 'show ip ospf neighbor' or 'show ip eigrp neighbors'.",
            "Check network statements in routing protocol config.",
            "Verify hello/dead timers match between neighbors.",
            "Check authentication configuration.",
            "Verify area configuration for OSPF.",
        ],
        "limitations": ["Routing protocol configuration not fully analyzable from routing table alone."],
    },
    "acl": {
        "root_cause": "Access Control List blocking traffic between source and destination.",
        "confidence": "HIGH",
        "confidence_score": 0.88,
        "osi_layer": "Layer 4",
        "concept": "ACL",
        "next_command": "show access-lists",
        "fix_steps": [
            "Review ACL entries: 'show access-lists'.",
            "Identify deny entries with match counts.",
            "Determine if the deny is intentional or misconfigured.",
            "Add a permit entry if traffic should be allowed.",
            "Ensure ACL entries are in correct order.",
            "Re-test connectivity after modification.",
        ],
        "limitations": ["ACL direction (inbound/outbound) and interface application not confirmed."],
    },
    "nat": {
        "root_cause": "NAT translation not configured or failing — inside hosts cannot reach outside.",
        "confidence": "HIGH",
        "confidence_score": 0.82,
        "osi_layer": "Layer 3",
        "concept": "NAT",
        "next_command": "show ip nat translations",
        "fix_steps": [
            "Check NAT translations: 'show ip nat translations'.",
            "Verify NAT statistics: 'show ip nat statistics'.",
            "Ensure inside/outside NAT interfaces are correctly configured.",
            "Verify access list for NAT overload is correct.",
            "Test with 'debug ip nat' if allowed.",
        ],
        "limitations": ["NAT pool and overload configuration not directly visible from translations table."],
    },
    "wireless": {
        "root_cause": "Wireless client cannot associate or authenticate to AP.",
        "confidence": "MEDIUM",
        "confidence_score": 0.60,
        "osi_layer": "Layer 2",
        "concept": "Wireless",
        "next_command": "show wireless client summary",
        "fix_steps": [
            "Verify SSID is broadcasting.",
            "Check authentication settings (PSK/WPA2).",
            "Verify client is associated: 'show wireless client summary'.",
            "Check DHCP for wireless VLAN.",
            "Verify gateway reachability from wireless subnet.",
        ],
        "limitations": ["Wireless controller output not provided — analysis limited to structured evidence."],
    },
}

# Fallback for unknown categories
MOCK_DEFAULT_DIAGNOSIS = {
    "root_cause": "Network misconfiguration detected — further investigation required.",
    "confidence": "LOW",
    "confidence_score": 0.40,
    "osi_layer": "Layer 3",
    "concept": "General Networking",
    "next_command": "show ip interface brief",
    "fix_steps": [
        "Gather more evidence with 'show ip interface brief'.",
        "Check routing table with 'show ip route'.",
        "Verify VLAN configuration.",
        "Review ACL configuration.",
    ],
    "limitations": [
        "Insufficient evidence for a precise diagnosis.",
        "Manual investigation recommended.",
    ],
}


class MockAIProvider(BaseAIProvider):
    """
    Deterministic mock AI provider.

    Returns realistic structured responses without any API key or network access.
    Used for local development, testing, and demo purposes.
    """

    provider_name = "mock"
    default_model = "mock-netsage-v1"

    def diagnose(self, context: DiagnosisContext) -> AIProviderResponse:
        """Return a deterministic mock diagnosis based on category and rule findings."""
        logger.info(
            "MockAIProvider diagnosing case %s (category=%s)",
            context.case_id,
            context.category,
        )

        template = self._select_template(context)
        evidence = self._build_evidence(context, template)

        output = {
            "root_cause": template["root_cause"],
            "confidence": template["confidence"],
            "confidence_score": template["confidence_score"],
            "evidence": evidence,
            "osi_layer": template["osi_layer"],
            "concept": template["concept"],
            "next_command": template["next_command"],
            "fix_steps": template["fix_steps"],
            "limitations": template["limitations"],
        }

        raw_text = json.dumps(output, indent=2)

        return AIProviderResponse(
            raw_text=raw_text,
            provider_name=self.provider_name,
            model_name=self.default_model,
            prompt_version=get_prompt_version(),
            success=True,
            parsed_json=output,
        )

    def _select_template(self, context: DiagnosisContext) -> dict:
        """Select the appropriate mock template based on category."""
        category = (context.category or "").lower().replace(" ", "_").replace("-", "_")

        # Try exact match
        if category in MOCK_DIAGNOSES:
            return MOCK_DIAGNOSES[category]

        # Try partial match
        for key in MOCK_DIAGNOSES:
            if key in category or category in key:
                return MOCK_DIAGNOSES[key]

        # Infer from rule findings
        if context.rule_findings:
            for finding in context.rule_findings:
                rule_name = finding.get("rule_name", "")
                if "route" in rule_name:
                    return MOCK_DIAGNOSES["routing"]
                if "vlan" in rule_name:
                    return MOCK_DIAGNOSES["vlan"]
                if "gateway" in rule_name:
                    return MOCK_DIAGNOSES["gateway"]
                if "dhcp" in rule_name:
                    return MOCK_DIAGNOSES["dhcp"]
                if "interface" in rule_name:
                    return MOCK_DIAGNOSES["ip_addressing"]
                if "acl" in rule_name:
                    return MOCK_DIAGNOSES["acl"]
                if "nat" in rule_name:
                    return MOCK_DIAGNOSES["nat"]

        # Infer from symptom keywords
        symptom = context.symptom.lower()
        if "route" in symptom or "routing" in symptom:
            return MOCK_DIAGNOSES["routing"]
        if "vlan" in symptom:
            return MOCK_DIAGNOSES["vlan"]
        if "gateway" in symptom:
            return MOCK_DIAGNOSES["gateway"]
        if "dhcp" in symptom or "169.254" in symptom or "apipa" in symptom:
            return MOCK_DIAGNOSES["dhcp"]
        if "dns" in symptom:
            return MOCK_DIAGNOSES["dns"]
        if "acl" in symptom or "blocked" in symptom or "denied" in symptom:
            return MOCK_DIAGNOSES["acl"]
        if "nat" in symptom or "internet" in symptom:
            return MOCK_DIAGNOSES["nat"]
        if "wireless" in symptom or "wifi" in symptom or "ssid" in symptom:
            return MOCK_DIAGNOSES["wireless"]
        if "trunk" in symptom:
            return MOCK_DIAGNOSES["trunking"]
        if "subnet" in symptom or "mask" in symptom:
            return MOCK_DIAGNOSES["ip_addressing"]

        return MOCK_DEFAULT_DIAGNOSIS

    def _build_evidence(self, context: DiagnosisContext, template: dict) -> list[dict]:
        """Build evidence list from all available show outputs dynamically."""
        evidence = []

        # Map known command types to specific meaningful observations
        cmd_descriptions = {
            "show ip route": "Routing table analyzed for destination network reachability.",
            "show ip interface brief": "Interface status reviewed for up/down states.",
            "show vlan brief": "VLAN database checked for VLAN existence and port assignments.",
            "show interfaces trunk": "Trunk interfaces reviewed for VLAN allowed lists.",
            "show access-lists": "ACL entries reviewed for deny rules with match counts.",
            "show ip nat translations": "NAT translation table checked for active translations.",
            "show ip nat statistics": "NAT statistics checked for hit counters and interface bindings.",
            "show ip dhcp binding": "DHCP binding table checked for leased IP assignments.",
            "show ip dhcp pool": "DHCP pool utilization checked for available address blocks.",
            "show hosts": "DNS host table reviewed for static entries and nameserver configuration.",
            "show ip hosts": "DNS host table reviewed for static entries and nameserver configuration.",
            "nslookup": "DNS lookup test examined for timeouts or name resolution failures.",
            "show running-config": "Running configuration checked for interface, routing, and service syntax.",
            "show run": "Running configuration checked for interface, routing, and service syntax.",
            "show cdp neighbors": "CDP neighbor adjacency checked for link-level device connectivity.",
            "show ip ospf neighbor": "OSPF neighbor adjacency checked for 2-WAY/FULL states.",
            "show ip eigrp neighbors": "EIGRP neighbor adjacency checked for active peerings.",
            "show spanning-tree": "Spanning-tree topology checked for root bridge and blocked ports.",
            "show etherchannel summary": "Port-channel bundle status checked for protocol negotiation.",
        }

        for cmd_name, cmd_output in context.show_outputs.items():
            if not cmd_output or not cmd_output.strip():
                continue

            # Look up standard observation or extract first non-empty line
            obs = None
            clean_cmd = cmd_name.lower().strip()
            for known_cmd, desc in cmd_descriptions.items():
                if known_cmd in clean_cmd or clean_cmd in known_cmd:
                    obs = desc
                    break

            if not obs:
                # Extract first meaningful telemetry line from output
                lines = [l.strip() for l in cmd_output.splitlines() if l.strip() and not l.startswith("!")]
                obs = f"Telemetry finding from {cmd_name}: {lines[0]}" if lines else f"Command output from {cmd_name} evaluated."

            evidence.append({
                "source": cmd_name,
                "observation": obs,
            })

        # Fallback if no show outputs
        if not evidence:
            evidence.append(
                {
                    "source": "symptom",
                    "observation": f"Analysis based on symptom: {context.symptom[:100]}",
                }
            )

        return evidence
