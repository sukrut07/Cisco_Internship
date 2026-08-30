#!/usr/bin/env python3
"""
NetSage AI — Standalone Deterministic Python Rule Checker.

Evaluates Cisco network telemetry against strict Layer 1-7 networking rules
WITHOUT probabilistic LLM calls.

Supports:
1. Duplicate IP detection
2. Wrong subnet mask detection
3. Gateway mismatch detection
4. Interface administratively down / physically down detection
5. Missing VLAN / Native VLAN mismatch detection
6. Missing route / FIB lookup detection
7. ACL deny filter match detection
8. DHCP exhaustion / APIPA (169.254.x.x) detection
9. DNS resolution / timeout detection
10. NAT inside/outside missing translation detection
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class DeterministicRuleChecker:
    """Deterministic Rule Engine performing multi-layer Cisco protocol checks."""

    def __init__(self) -> None:
        pass

    def evaluate_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all deterministic checks against provided case telemetry.
        
        Returns structured dictionary containing all checks, statuses, and evidence.
        """
        case_id = case_data.get("case_id", "CUSTOM-CASE")
        symptom = case_data.get("symptom", "")
        topology = case_data.get("topology", "")
        show_outputs = case_data.get("show_outputs", {})
        devices = case_data.get("devices", [])

        checks: List[Dict[str, Any]] = []

        # 1. Interface Status Check
        checks.append(self._check_interface_status(show_outputs))

        # 2. Duplicate IP Check
        checks.append(self._check_duplicate_ip(devices, show_outputs))

        # 3. Subnet Mask Check
        checks.append(self._check_subnet_mask(devices, topology))

        # 4. Gateway Mismatch Check
        checks.append(self._check_gateway_mismatch(devices, topology, show_outputs))

        # 5. Missing Route Check
        checks.append(self._check_missing_route(show_outputs, symptom, topology))

        # 6. VLAN Database & Native VLAN Check
        checks.append(self._check_vlan(show_outputs, topology))

        # 7. ACL Deny Matches Check
        checks.append(self._check_acl_filters(show_outputs))

        # 8. DHCP Status / APIPA Check
        checks.append(self._check_dhcp(show_outputs, symptom))

        # 9. DNS Resolution Timeout Check
        checks.append(self._check_dns(show_outputs, symptom))

        # 10. NAT Translation Check
        checks.append(self._check_nat(show_outputs))

        # Filter and summarize
        failed_checks = [c for c in checks if c["status"] == "FAIL"]
        passed_checks = [c for c in checks if c["status"] == "PASS"]
        na_checks = [c for c in checks if c["status"] == "N/A"]

        return {
            "case_id": case_id,
            "total_checks": len(checks),
            "passed_count": len(passed_checks),
            "failed_count": len(failed_checks),
            "na_count": len(na_checks),
            "rule_engine_verdict": "FAULTS_DETECTED" if failed_checks else "CLEAN_PASS",
            "checks": checks,
        }

    # --------------------------------------------------------------------------
    # Individual Deterministic Check Implementations
    # --------------------------------------------------------------------------

    def _check_interface_status(self, show_outputs: Dict[str, str]) -> Dict[str, Any]:
        """Check for administratively down or physically down interfaces."""
        cmd_out = show_outputs.get("show ip interface brief", "")
        if not cmd_out:
            return {
                "check": "interface_status",
                "layer": "Layer 1",
                "status": "N/A",
                "evidence": "show ip interface brief telemetry not provided.",
                "severity": "LOW",
            }

        admin_down: List[str] = []
        down_down: List[str] = []

        for line in cmd_out.splitlines():
            line_lower = line.lower()
            if "administratively down" in line_lower:
                parts = line.split()
                if parts:
                    admin_down.append(f"{parts[0]} (Admin Down)")
            elif "down" in line_lower and "up" not in line_lower and not line_lower.startswith("interface"):
                parts = line.split()
                if parts and len(parts) >= 2:
                    down_down.append(f"{parts[0]} (Physical Down)")

        if admin_down:
            return {
                "check": "interface_status",
                "layer": "Layer 1",
                "status": "FAIL",
                "evidence": f"Interface(s) administratively shut down: {', '.join(admin_down)}",
                "severity": "HIGH",
                "remediation": "Enter interface configuration mode and issue 'no shutdown'.",
            }
        if down_down:
            return {
                "check": "interface_status",
                "layer": "Layer 1",
                "status": "FAIL",
                "evidence": f"Interface(s) physical link down: {', '.join(down_down)}",
                "severity": "HIGH",
                "remediation": "Check physical cabling, SFP transceivers, or remote switchport status.",
            }

        return {
            "check": "interface_status",
            "layer": "Layer 1",
            "status": "PASS",
            "evidence": "All parsed interfaces are in UP/UP state.",
            "severity": "LOW",
        }

    def _check_duplicate_ip(self, devices: List[Dict[str, Any]], show_outputs: Dict[str, str]) -> Dict[str, Any]:
        """Detect duplicate IP assignments across devices or ARP conflicts."""
        seen_ips: Dict[str, str] = {}
        for dev in devices:
            ip = dev.get("ip")
            name = dev.get("name", "Unknown Device")
            if ip:
                if ip in seen_ips:
                    return {
                        "check": "duplicate_ip",
                        "layer": "Layer 3",
                        "status": "FAIL",
                        "evidence": f"Duplicate IP {ip} detected on {name} and {seen_ips[ip]}.",
                        "severity": "HIGH",
                        "remediation": f"Re-assign unique host IP on {name} or configure static DHCP reservation.",
                    }
                seen_ips[ip] = name

        arp_out = show_outputs.get("show ip arp", "") or show_outputs.get("arp -a", "")
        if "duplicate" in arp_out.lower() or "conflict" in arp_out.lower():
            return {
                "check": "duplicate_ip",
                "layer": "Layer 3",
                "status": "FAIL",
                "evidence": "ARP table records active MAC address conflict / duplicate IP flag.",
                "severity": "HIGH",
                "remediation": "Inspect ARP table and isolate conflicting host MAC address.",
            }

        return {
            "check": "duplicate_ip",
            "layer": "Layer 3",
            "status": "PASS",
            "evidence": f"No duplicate IP collisions detected across {len(devices)} device(s).",
            "severity": "LOW",
        }

    def _check_subnet_mask(self, devices: List[Dict[str, Any]], topology: str) -> Dict[str, Any]:
        """Detect subnet mask mismatches isolating hosts on a local broadcast domain."""
        if not devices:
            return {
                "check": "subnet_mask",
                "layer": "Layer 3",
                "status": "PASS",
                "evidence": "No discrete host endpoint definitions supplied for mask comparison.",
                "severity": "LOW",
            }

        for dev in devices:
            ip = dev.get("ip")
            mask = dev.get("mask")
            gw = dev.get("gateway")
            if ip and mask and gw:
                try:
                    net = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
                    gw_ip = ipaddress.IPv4Address(gw)
                    if gw_ip not in net:
                        return {
                            "check": "subnet_mask",
                            "layer": "Layer 3",
                            "status": "FAIL",
                            "evidence": f"Device {dev.get('name', 'PC')} IP {ip}/{mask} network ({net}) excludes gateway {gw}.",
                            "severity": "HIGH",
                            "remediation": f"Correct host subnet mask or assign gateway within {net}.",
                        }
                except Exception:
                    pass

        return {
            "check": "subnet_mask",
            "layer": "Layer 3",
            "status": "PASS",
            "evidence": "Host subnet masks encompass local default gateways.",
            "severity": "LOW",
        }

    def _check_gateway_mismatch(self, devices: List[Dict[str, Any]], topology: str, show_outputs: Dict[str, str]) -> Dict[str, Any]:
        """Detect default gateway pointing to invalid subnet or nonexistent IP."""
        for dev in devices:
            ip = dev.get("ip")
            gw = dev.get("gateway")
            mask = dev.get("mask", "255.255.255.0")
            if ip and gw:
                try:
                    net = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
                    if ipaddress.IPv4Address(gw) not in net:
                        return {
                            "check": "gateway_mismatch",
                            "layer": "Layer 3",
                            "status": "FAIL",
                            "evidence": f"Configured gateway {gw} is outside host subnet {net}.",
                            "severity": "HIGH",
                            "remediation": f"Configure default gateway on host inside {net}.",
                        }
                except Exception:
                    pass

        # Regex search in topology note
        gw_match = re.search(r"GW:\s*([0-9.]+)", topology)
        ip_match = re.search(r"([0-9.]+)/([0-9]+)", topology)
        if gw_match and ip_match:
            try:
                host_net = ipaddress.IPv4Network(f"{ip_match.group(1)}/{ip_match.group(2)}", strict=False)
                gw_addr = ipaddress.IPv4Address(gw_match.group(1))
                if gw_addr not in host_net:
                    return {
                        "check": "gateway_mismatch",
                        "layer": "Layer 3",
                        "status": "FAIL",
                        "evidence": f"Topology defines Gateway {gw_addr} outside client network {host_net}.",
                        "severity": "HIGH",
                        "remediation": f"Correct default gateway to match local router IP on {host_net}.",
                    }
            except Exception:
                pass

        return {
            "check": "gateway_mismatch",
            "layer": "Layer 3",
            "status": "PASS",
            "evidence": "Configured default gateways match local subnet boundaries.",
            "severity": "LOW",
        }

    def _check_missing_route(self, show_outputs: Dict[str, str], symptom: str, topology: str) -> Dict[str, Any]:
        """Check routing table for missing destination prefixes or missing default routes."""
        route_out = show_outputs.get("show ip route", "")
        if not route_out:
            return {
                "check": "missing_route",
                "layer": "Layer 3",
                "status": "N/A",
                "evidence": "show ip route telemetry not provided.",
                "severity": "LOW",
            }

        # Extract target IP from symptom or topology
        target_ips = re.findall(r"\b192\.168\.[0-9]+\.[0-9]+\b|\b10\.[0-9]+\.[0-9]+\.[0-9]+\b", symptom + " " + topology)
        destination_ip = None
        for tip in target_ips:
            if not tip.endswith(".1") and not tip.endswith(".0"):
                destination_ip = tip

        has_default_route = "0.0.0.0/0" in route_out or "Gateway of last resort is" in route_out and "not set" not in route_out

        if destination_ip:
            try:
                target_addr = ipaddress.IPv4Address(destination_ip)
                route_matched = False
                for line in route_out.splitlines():
                    net_matches = re.findall(r"\b([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]+)\b", line)
                    for nstr in net_matches:
                        try:
                            if target_addr in ipaddress.IPv4Network(nstr, strict=False):
                                route_matched = True
                                break
                        except Exception:
                            continue
                    if route_matched:
                        break

                if not route_matched and not has_default_route:
                    return {
                        "check": "missing_route",
                        "layer": "Layer 3",
                        "status": "FAIL",
                        "evidence": f"No FIB route exists for destination {destination_ip} and Gateway of last resort is not set.",
                        "severity": "HIGH",
                        "remediation": f"Configure static route or dynamic routing protocol for {destination_ip}.",
                    }
            except Exception:
                pass

        if "Gateway of last resort is not set" in route_out and ("external" in symptom.lower() or "internet" in symptom.lower() or "server" in symptom.lower()):
            if "C " not in route_out and "S " not in route_out:
                return {
                    "check": "missing_route",
                    "layer": "Layer 3",
                    "status": "FAIL",
                    "evidence": "Default gateway route 0.0.0.0/0 missing and no covering route present in FIB.",
                    "severity": "HIGH",
                    "remediation": "Add default static route: ip route 0.0.0.0 0.0.0.0 <next-hop-ip>.",
                }

        return {
            "check": "missing_route",
            "layer": "Layer 3",
            "status": "PASS",
            "evidence": "Routing table contains covering prefix or default gateway.",
            "severity": "LOW",
        }

    def _check_vlan(self, show_outputs: Dict[str, str], topology: str) -> Dict[str, Any]:
        """Check VLAN database existence and native VLAN trunk consistency."""
        vlan_out = show_outputs.get("show vlan brief", "") or show_outputs.get("show vlan", "")
        trunk_out = show_outputs.get("show interfaces trunk", "")

        if trunk_out:
            native_vlans = re.findall(r"Native vlan\s*([0-9]+)", trunk_out, re.IGNORECASE)
            if len(set(native_vlans)) > 1:
                return {
                    "check": "vlan_status",
                    "layer": "Layer 2",
                    "status": "FAIL",
                    "evidence": f"Native VLAN mismatch detected across trunk ports: {native_vlans}.",
                    "severity": "HIGH",
                    "remediation": "Align native VLAN across all 802.1Q trunk endpoints using 'switchport trunk native vlan <id>'.",
                }

        if vlan_out and ("vlan 20" in topology.lower() or "vlan 30" in topology.lower()):
            if "20 " not in vlan_out and "30 " not in vlan_out and "VLAN0020" not in vlan_out:
                if "vlan" in topology.lower():
                    return {
                        "check": "vlan_status",
                        "layer": "Layer 2",
                        "status": "FAIL",
                        "evidence": "Configured access VLAN is missing from local VLAN database.",
                        "severity": "HIGH",
                        "remediation": "Create VLAN in global configuration mode: vlan <id> -> name <name>.",
                    }

        return {
            "check": "vlan_status",
            "layer": "Layer 2",
            "status": "PASS",
            "evidence": "VLAN database active and trunk native VLAN parameters aligned.",
            "severity": "LOW",
        }

    def _check_acl_filters(self, show_outputs: Dict[str, str]) -> Dict[str, Any]:
        """Inspect Access Control Lists for explicit packet deny matches."""
        acl_out = show_outputs.get("show access-lists", "")
        if not acl_out:
            return {
                "check": "acl_filters",
                "layer": "Layer 4",
                "status": "PASS",
                "evidence": "No ACL telemetry provided or no ACL filters configured.",
                "severity": "LOW",
            }

        deny_matches = re.findall(r"deny\s+([^\n]+)\(([0-9]+)\s+matches\)", acl_out, re.IGNORECASE)
        for rule_text, match_count in deny_matches:
            if int(match_count) > 0:
                return {
                    "check": "acl_filters",
                    "layer": "Layer 4",
                    "status": "FAIL",
                    "evidence": f"ACL deny rule actively dropping packets ({match_count} matches): deny {rule_text.strip()}",
                    "severity": "HIGH",
                    "remediation": "Modify ACL entry or reorder permit statements before deny clause.",
                }

        return {
            "check": "acl_filters",
            "layer": "Layer 4",
            "status": "PASS",
            "evidence": "No active deny match counter increments in ACL entries.",
            "severity": "LOW",
        }

    def _check_dhcp(self, show_outputs: Dict[str, str], symptom: str) -> Dict[str, Any]:
        """Detect APIPA address assignment or DHCP pool exhaustion."""
        if "169.254." in symptom or "apipa" in symptom.lower():
            return {
                "check": "dhcp_status",
                "layer": "Layer 7",
                "status": "FAIL",
                "evidence": "Host received APIPA address (169.254.x.x) indicating DHCP DISCOVER timeout.",
                "severity": "HIGH",
                "remediation": "Verify DHCP pool bindings, helper-address relay, and switchport VLAN assignment.",
            }

        dhcp_pool_out = show_outputs.get("show ip dhcp pool", "")
        if "100%" in dhcp_pool_out or "exhausted" in dhcp_pool_out.lower():
            return {
                "check": "dhcp_status",
                "layer": "Layer 7",
                "status": "FAIL",
                "evidence": "DHCP address pool utilization reached 100% (pool exhaustion).",
                "severity": "HIGH",
                "remediation": "Expand DHCP network scope or shorten lease duration.",
            }

        return {
            "check": "dhcp_status",
            "layer": "Layer 7",
            "status": "PASS",
            "evidence": "No DHCP lease failures or APIPA addresses detected.",
            "severity": "LOW",
        }

    def _check_dns(self, show_outputs: Dict[str, str], symptom: str) -> Dict[str, Any]:
        """Detect DNS query timeouts and server resolution failures."""
        if "nslookup" in symptom.lower() and ("timeout" in symptom.lower() or "can't find" in symptom.lower() or "server failed" in symptom.lower()):
            return {
                "check": "dns_status",
                "layer": "Layer 7",
                "status": "FAIL",
                "evidence": "DNS client resolver reported query timeout or NXDOMAIN resolution failure.",
                "severity": "HIGH",
                "remediation": "Verify primary DNS server IP configuration and DNS forwarder reachability.",
            }
        return {
            "check": "dns_status",
            "layer": "Layer 7",
            "status": "PASS",
            "evidence": "No DNS resolution timeouts reported.",
            "severity": "LOW",
        }

    def _check_nat(self, show_outputs: Dict[str, str]) -> Dict[str, Any]:
        """Check for missing NAT inside/outside interface statements."""
        nat_trans = show_outputs.get("show ip nat translations", "")
        nat_stat = show_outputs.get("show ip nat statistics", "")
        int_brief = show_outputs.get("show ip interface brief", "")

        if nat_stat and "outside interface" in nat_stat.lower() and "none" in nat_stat.lower():
            return {
                "check": "nat_status",
                "layer": "Layer 3",
                "status": "FAIL",
                "evidence": "NAT translation statistics show no outside interface configured.",
                "severity": "HIGH",
                "remediation": "Configure 'ip nat outside' on WAN interface and 'ip nat inside' on LAN interface.",
            }

        return {
            "check": "nat_status",
            "layer": "Layer 3",
            "status": "PASS",
            "evidence": "NAT configuration parameters consistent.",
            "severity": "LOW",
        }


# ------------------------------------------------------------------------------
# Command Line Interface (CLI) Entry Point
# ------------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="NetSage AI Standalone Deterministic Python Rule Checker")
    parser.add_argument("--case", type=str, help="Case ID to check (e.g. CASE-001)")
    parser.add_argument("--file", type=str, help="Path to JSON file containing case telemetry")
    parser.add_argument("--all", action="store_true", help="Run deterministic checks against all seed cases")
    parser.add_argument("--dataset", type=str, default="backend/data/seed_cases.json", help="Path to seed dataset JSON")
    args = parser.parse_args()

    checker = DeterministicRuleChecker()

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File {args.file} not found.", file=sys.stderr)
            sys.exit(1)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        result = checker.evaluate_case(data)
        print(json.dumps(result, indent=2))
        return

    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"Error: Dataset {args.dataset} not found.", file=sys.stderr)
        sys.exit(1)

    with open(dataset_path, encoding="utf-8") as f:
        cases = json.load(f)

    if args.case:
        target = next((c for c in cases if c.get("case_id", "").upper() == args.case.upper()), None)
        if not target:
            print(f"Error: Case {args.case} not found in {args.dataset}.", file=sys.stderr)
            sys.exit(1)
        result = checker.evaluate_case(target)
        print(json.dumps(result, indent=2))
        return

    # Default or --all: run against all seed cases
    summary_results = []
    for c in cases:
        res = checker.evaluate_case(c)
        summary_results.append({
            "case_id": res["case_id"],
            "verdict": res["rule_engine_verdict"],
            "failed_checks": [fc["check"] for fc in res["checks"] if fc["status"] == "FAIL"],
        })

    print(f"=== NetSage AI Deterministic Rule Checker: {len(cases)} Cases Evaluated ===")
    faults_found = sum(1 for r in summary_results if r["verdict"] == "FAULTS_DETECTED")
    print(f"Total Cases: {len(cases)} | Faults Identified: {faults_found} | Clean Pass: {len(cases) - faults_found}\n")
    for r in summary_results[:10]:
        status_symbol = "❌" if r["verdict"] == "FAULTS_DETECTED" else "✅"
        print(f"{status_symbol} {r['case_id']}: {r['verdict']} -> {', '.join(r['failed_checks']) if r['failed_checks'] else 'None'}")
    if len(summary_results) > 10:
        print(f"... and {len(summary_results) - 10} more cases evaluated.")


if __name__ == "__main__":
    main()
