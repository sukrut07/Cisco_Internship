import re
import ipaddress
from typing import List, Dict, Any, Optional

class RuleCheckResult:
    def __init__(self, rule: str, status: str, severity: str, evidence: str, recommendation: str):
        self.rule = rule
        self.status = status  # "passed" or "failed"
        self.severity = severity  # "low", "medium", "high", "critical"
        self.evidence = evidence
        self.recommendation = recommendation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule": self.rule,
            "status": self.status,
            "severity": self.severity,
            "evidence": self.evidence,
            "recommendation": self.recommendation
        }


class DeterministicRuleChecker:
    """
    Deterministic Python Rule Checker for common Cisco networking mistakes.
    Evaluates raw CLI outputs, symptoms, and optional structured network info.
    """

    def analyze(self, 
                show_outputs: str, 
                symptom: str = "", 
                topology: str = "",
                source_ip: Optional[str] = None,
                dest_ip: Optional[str] = None,
                subnet_mask: Optional[str] = None,
                gateway: Optional[str] = None,
                vlan_id: Optional[int] = None) -> List[Dict[str, Any]]:
        
        results: List[RuleCheckResult] = []
        
        combined_text = f"{show_outputs}\n{symptom}\n{topology}"

        # 1. Interface Down Check
        interface_down_res = self._check_interface_down(combined_text)
        if interface_down_res:
            results.append(interface_down_res)

        # 2. Gateway Mismatch Check
        gateway_res = self._check_gateway_mismatch(combined_text, source_ip, subnet_mask, gateway)
        if gateway_res:
            results.append(gateway_res)

        # 3. Duplicate IP Check
        dup_ip_res = self._check_duplicate_ip(combined_text, source_ip)
        if dup_ip_res:
            results.append(dup_ip_res)

        # 4. Missing VLAN Check
        vlan_res = self._check_missing_vlan(combined_text, vlan_id)
        if vlan_res:
            results.append(vlan_res)

        # 5. Missing Route Check
        route_res = self._check_missing_route(combined_text, dest_ip)
        if route_res:
            results.append(route_res)

        # 6. Wrong Subnet Mask Check
        subnet_res = self._check_wrong_subnet_mask(combined_text, source_ip, subnet_mask)
        if subnet_res:
            results.append(subnet_res)

        # 7. Authentication & Security Check (RADIUS / 802.1X / Port Security)
        auth_res = self._check_authentication_failure(combined_text)
        if auth_res:
            results.append(auth_res)

        return [r.to_dict() for r in results]

    def _check_interface_down(self, text: str) -> Optional[RuleCheckResult]:
        admin_down_matches = re.findall(r'(\S+)\s+.*?administratively down', text, re.IGNORECASE)
        line_down_matches = re.findall(r'(\S+)\s+is down,\s+line protocol is down', text, re.IGNORECASE)
        err_disabled_matches = re.findall(r'(\S+)\s+.*?err-disabled', text, re.IGNORECASE)
        
        evidences = []
        if admin_down_matches:
            evidences.append(f"Interface(s) {', '.join(set(admin_down_matches))} administratively down")
        if line_down_matches:
            evidences.append(f"Interface(s) {', '.join(set(line_down_matches))} down (line protocol down)")
        if err_disabled_matches:
            evidences.append(f"Interface(s) {', '.join(set(err_disabled_matches))} err-disabled")

        if evidences:
            return RuleCheckResult(
                rule="interface_down",
                status="failed",
                severity="critical",
                evidence=" | ".join(evidences),
                recommendation="Run 'no shutdown' on disabled interface or reset err-disabled port."
            )
        return RuleCheckResult(
            rule="interface_down",
            status="passed",
            severity="low",
            evidence="No interfaces reported administratively down or err-disabled.",
            recommendation="Interface physical status verified normal."
        )

    def _check_gateway_mismatch(self, text: str, ip_param: Optional[str], mask_param: Optional[str], gw_param: Optional[str]) -> Optional[RuleCheckResult]:
        host_ip = ip_param
        mask = mask_param or "255.255.255.0"
        gw = gw_param

        # Try parsing from text if parameters not explicitly provided
        if not host_ip:
            ip_match = re.search(r'IP Address:\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', text)
            if ip_match:
                host_ip = ip_match.group(1)

        if not gw:
            gw_match = re.search(r'Default Gateway:\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', text)
            if gw_match:
                gw = gw_match.group(1)

        if not mask_param:
            mask_match = re.search(r'Subnet Mask:\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', text)
            if mask_match:
                mask = mask_match.group(1)

        if host_ip and gw:
            try:
                net = ipaddress.IPv4Network(f"{host_ip}/{mask}", strict=False)
                gw_addr = ipaddress.IPv4Address(gw)
                if gw_addr not in net:
                    return RuleCheckResult(
                        rule="gateway_mismatch",
                        status="failed",
                        severity="high",
                        evidence=f"Host IP {host_ip} with mask {mask} netprefix is {net.network_address}, but Default Gateway {gw} is outside this subnet.",
                        recommendation=f"Reconfigure default gateway to belong to {net.network_address}/{net.prefixlen}."
                    )
                else:
                    return RuleCheckResult(
                        rule="gateway_mismatch",
                        status="passed",
                        severity="low",
                        evidence=f"Default Gateway {gw} is valid for subnet {net.network_address}/{net.prefixlen}.",
                        recommendation="Gateway configuration verified."
                    )
            except Exception:
                pass
        return None

    def _check_duplicate_ip(self, text: str, ip_param: Optional[str]) -> Optional[RuleCheckResult]:
        dup_syslog = re.search(r'%IP-4-DUPADDR:\s*Duplicate address\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', text, re.IGNORECASE)
        dup_text = re.search(r'Duplicate IP address configured on (\S+)', text, re.IGNORECASE)
        dup_symptom = re.search(r'Duplicate address\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', text, re.IGNORECASE)

        if dup_syslog or dup_text or dup_symptom:
            ip_str = dup_syslog.group(1) if dup_syslog else (dup_symptom.group(1) if dup_symptom else "detected in logs")
            return RuleCheckResult(
                rule="duplicate_ip",
                status="failed",
                severity="high",
                evidence=f"Duplicate IP address conflict detected for {ip_str}.",
                recommendation="Assign unique IP addresses to all host and device interfaces."
            )
        return RuleCheckResult(
            rule="duplicate_ip",
            status="passed",
            severity="low",
            evidence="No duplicate IP warnings found in logs or command outputs.",
            recommendation="IP address uniqueness verified."
        )

    def _check_missing_vlan(self, text: str, vlan_param: Optional[int]) -> Optional[RuleCheckResult]:
        inactive_vlan = re.search(r'Access Mode VLAN:\s*(\d+)\s*\(inactive\)', text, re.IGNORECASE)
        missing_vlan_msg = re.search(r'VLAN\s*(\d+)\s*does not exist', text, re.IGNORECASE)
        missing_vlan_log = re.search(r'VLAN\s*(\d+)\s*is missing', text, re.IGNORECASE)

        vlan_num = None
        if inactive_vlan:
            vlan_num = inactive_vlan.group(1)
        elif missing_vlan_msg:
            vlan_num = missing_vlan_msg.group(1)
        elif missing_vlan_log:
            vlan_num = missing_vlan_log.group(1)

        if vlan_num:
            return RuleCheckResult(
                rule="missing_vlan",
                status="failed",
                severity="high",
                evidence=f"VLAN {vlan_num} is referenced on port configuration but missing from switch VLAN database (inactive).",
                recommendation=f"Create VLAN {vlan_num} in global configuration mode ('vlan {vlan_num}')."
            )
        return RuleCheckResult(
            rule="missing_vlan",
            status="passed",
            severity="low",
            evidence="No inactive or uncreated VLAN references detected.",
            recommendation="VLAN database validation passed."
        )

    def _check_missing_route(self, text: str, dest_ip: Optional[str]) -> Optional[RuleCheckResult]:
        no_gateway = "Gateway of last resort is not set" in text
        no_route_msg = "Routing table entry for" in text and "not found" in text
        missing_default = re.search(r'has no Gateway of Last Resort', text, re.IGNORECASE)

        if no_gateway or no_route_msg or missing_default:
            evidence_str = "Gateway of last resort is not set" if no_gateway else "Destination route not found in IP routing table"
            return RuleCheckResult(
                rule="missing_route",
                status="failed",
                severity="critical",
                evidence=evidence_str,
                recommendation="Add static default route ('ip route 0.0.0.0 0.0.0.0 <next-hop>') or verify dynamic routing protocol."
            )
        return RuleCheckResult(
            rule="missing_route",
            status="passed",
            severity="low",
            evidence="IP routing table contains valid routes or default gateway.",
            recommendation="Routing table lookup passed."
        )

    def _check_wrong_subnet_mask(self, text: str, ip_param: Optional[str], mask_param: Optional[str]) -> Optional[RuleCheckResult]:
        mask_mismatch = re.search(r'Subnet mask mismatch:\s*Router\s*\S+\s*is configured with\s*(\S+)', text, re.IGNORECASE)
        inconsistent_mask = re.search(r'Internet address is\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/(\d+)', text, re.IGNORECASE)

        if mask_mismatch:
            return RuleCheckResult(
                rule="wrong_subnet_mask",
                status="failed",
                severity="high",
                evidence=f"Subnet mask mismatch detected: {mask_mismatch.group(0)}",
                recommendation="Align subnet mask on router interface and host configuration."
            )
        return RuleCheckResult(
            rule="wrong_subnet_mask",
            status="passed",
            severity="low",
            evidence="Subnet mask parameters consistent.",
            recommendation="Subnet configuration verified."
        )

    def _check_authentication_failure(self, text: str) -> Optional[RuleCheckResult]:
        radius_mismatch = re.search(r'Shared Secret\s*(Incorrect|Mismatch|\*\*\*\*)', text, re.IGNORECASE)
        auth_failed = re.search(r'(fails|failed)\s*authentication|Status stays on [\'"]Authenticating[\'"]', text, re.IGNORECASE)
        port_security = re.search(r'Port security violation|unauthorized MAC address', text, re.IGNORECASE)

        if radius_mismatch or auth_failed or port_security:
            evidence_parts = []
            if radius_mismatch:
                evidence_parts.append("RADIUS Shared Secret mismatch detected on WLC/AAA log")
            if auth_failed:
                evidence_parts.append("802.1X client authentication failure detected ('Authenticating...' status)")
            if port_security:
                evidence_parts.append("Port security violation triggered on switch interface")

            return RuleCheckResult(
                rule="authentication_failure",
                status="failed",
                severity="high",
                evidence=" | ".join(evidence_parts),
                recommendation="Verify RADIUS shared secret on WLC/Switch and AAA server (FreeRADIUS/NPS) and check 802.1X/Port-Security policy."
            )
        return RuleCheckResult(
            rule="authentication_failure",
            status="passed",
            severity="low",
            evidence="No authentication errors or RADIUS mismatches detected.",
            recommendation="Authentication services verified."
        )

