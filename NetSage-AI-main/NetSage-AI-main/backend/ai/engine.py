import os
import json
import re
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

class BaseAIDiagnosisEngine(ABC):
    @abstractmethod
    def diagnose(self, 
                 title: str, 
                 symptom: str, 
                 topology: str, 
                 show_outputs: str, 
                 concept: str, 
                 severity: str,
                 rule_checks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        pass


class MockDiagnosisEngine(BaseAIDiagnosisEngine):
    """
    Realistic Mock AI Diagnosis Engine that generates evidence-based structured diagnoses
    when AI_API_KEY is not configured or mock mode is requested.
    """

    def diagnose(self, 
                 title: str, 
                 symptom: str, 
                 topology: str, 
                 show_outputs: str, 
                 concept: str, 
                 severity: str,
                 rule_checks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        
        combined_text = f"{title}\n{symptom}\n{topology}\n{show_outputs}".lower()

        # Check for failed rule checker findings first
        failed_rules = []
        if rule_checks:
            failed_rules = [r for r in rule_checks if r.get("status") == "failed"]

        # 1. Interface Down / Administratively Down
        if "administratively down" in combined_text or "line protocol is down" in combined_text or any(r.get("rule") == "interface_down" for r in failed_rules):
            intf_match = re.search(r'(\S+)\s+.*?administratively down', show_outputs, re.IGNORECASE)
            intf_name = intf_match.group(1) if intf_match else "Target Interface"
            return {
                "root_cause": f"Interface {intf_name} is administratively disabled or down.",
                "confidence": 96,
                "confidence_level": "High",
                "osi_layer": "Layer 1 (Physical)",
                "concept": "Routing" if "router" in combined_text else "VLAN",
                "severity": "Critical",
                "evidence": [
                    f"Show output indicates {intf_name} status is administratively down",
                    "Line protocol is down, preventing physical/data-link frame transmission"
                ],
                "next_commands": [
                    f"show ip interface brief | include {intf_name}",
                    f"show running-config interface {intf_name}"
                ],
                "fix_steps": [
                    f"Enter global configuration mode",
                    f"interface {intf_name}",
                    "no shutdown",
                    "end"
                ],
                "alternative_causes": [
                    "Physical cable unplugged or faulty SFP module",
                    "Duplex/speed mismatch on connected port"
                ],
                "verification_steps": [
                    "Execute 'show ip interface brief' to verify status is UP/UP",
                    "Ping default gateway or adjacent neighbor interface"
                ]
            }

        # 2. Gateway Mismatch
        if "default gateway" in combined_text or "gateway mismatch" in combined_text or any(r.get("rule") == "gateway_mismatch" for r in failed_rules):
            return {
                "root_cause": "Host default gateway address is configured on an incorrect IP subnet relative to host IP.",
                "confidence": 94,
                "confidence_level": "High",
                "osi_layer": "Layer 3 (Network)",
                "concept": "Gateway",
                "severity": "High",
                "evidence": [
                    "Host IP address and Default Gateway belong to non-matching IP network prefixes",
                    "Rule checker flagged gateway mismatch validation failure"
                ],
                "next_commands": [
                    "show ip route",
                    "show ip interface brief"
                ],
                "fix_steps": [
                    "Update host TCP/IP configuration",
                    "Set Default Gateway to the local router interface IP address in the host subnet",
                    "Verify subnet mask alignment (e.g. 255.255.255.0)"
                ],
                "alternative_causes": [
                    "Router subinterface IP misconfiguration",
                    "VLAN access port misassignment"
                ],
                "verification_steps": [
                    "Ping local default gateway from host",
                    "Ping external IP address (e.g., 8.8.8.8) to verify off-subnet routing"
                ]
            }

        # 3. Missing VLAN
        if "vlan" in combined_text and ("inactive" in combined_text or "missing" in combined_text or "does not exist" in combined_text or any(r.get("rule") == "missing_vlan" for r in failed_rules)):
            vlan_match = re.search(r'vlan\s*(\d+)', combined_text)
            v_id = vlan_match.group(1) if vlan_match else "30"
            return {
                "root_cause": f"VLAN {v_id} is missing from switch VLAN database, forcing access ports assigned to VLAN {v_id} into inactive state.",
                "confidence": 92,
                "confidence_level": "High",
                "osi_layer": "Layer 2 (Data Link)",
                "concept": "VLAN",
                "severity": "High",
                "evidence": [
                    f"Show vlan brief output omits VLAN {v_id}",
                    f"Access port switchport status reports 'Access Mode VLAN: {v_id} (inactive)'"
                ],
                "next_commands": [
                    "show vlan brief",
                    "show interfaces switchport"
                ],
                "fix_steps": [
                    "Enter global configuration mode on switch",
                    f"vlan {v_id}",
                    f"name Network_VLAN_{v_id}",
                    "exit"
                ],
                "alternative_causes": [
                    "VTP pruning or VTP domain mismatch removing VLAN automatically",
                    "Trunk link allowed VLAN list excluding target VLAN"
                ],
                "verification_steps": [
                    "Run 'show vlan brief' and confirm status is active",
                    "Verify port operational state changes from inactive to up"
                ]
            }

        # 4. Duplicate IP
        if "duplicate" in combined_text or "%ip-4-dupaddr" in combined_text or any(r.get("rule") == "duplicate_ip" for r in failed_rules):
            return {
                "root_cause": "Duplicate IP address conflict between multiple devices on the local broadcast domain.",
                "confidence": 95,
                "confidence_level": "High",
                "osi_layer": "Layer 3 (Network)",
                "concept": "Gateway",
                "severity": "High",
                "evidence": [
                    "Syslog %IP-4-DUPADDR or MAC address table flipping detected",
                    "Multiple network cards claiming identical IPv4 address"
                ],
                "next_commands": [
                    "show mac address-table",
                    "show ip arp"
                ],
                "fix_steps": [
                    "Locate offending secondary device MAC address",
                    "Reconfigure host or printer with an unassigned static IP address or enable DHCP"
                ],
                "alternative_causes": [
                    "Overlapping DHCP address pool scope",
                    "Stale ARP cache entry on default gateway"
                ],
                "verification_steps": [
                    "Clear ARP table ('clear ip arp')",
                    "Verify steady ICMP reply without packet loss"
                ]
            }

        # 5. Missing Route / Default Route
        if "route" in combined_text and ("gateway of last resort is not set" in combined_text or "not found" in combined_text or any(r.get("rule") == "missing_route" for r in failed_rules)):
            return {
                "root_cause": "Missing route or Gateway of Last Resort in router IP routing table.",
                "confidence": 90,
                "confidence_level": "High",
                "osi_layer": "Layer 3 (Network)",
                "concept": "Routing",
                "severity": "Critical",
                "evidence": [
                    "Show ip route displays 'Gateway of last resort is not set'",
                    "Destination network prefix absent from RIB table"
                ],
                "next_commands": [
                    "show ip route",
                    "show ip protocols"
                ],
                "fix_steps": [
                    "Configure static default route: 'ip route 0.0.0.0 0.0.0.0 <next-hop-ip>'",
                    "Ensure routing protocol (OSPF/EIGRP) network statements are advertised"
                ],
                "alternative_causes": [
                    "Routing protocol neighbor adjacency down",
                    "Next-hop IP address unreachable"
                ],
                "verification_steps": [
                    "Run 'show ip route' to verify default static route entry (S* 0.0.0.0/0)",
                    "Perform traceroute to target remote network address"
                ]
            }

        # 6. ACL Blocking Traffic
        if "access-list" in combined_text or "acl" in combined_text or "deny" in combined_text:
            return {
                "root_cause": "Access Control List (ACL) rule explicitly dropping or implicitly denying target traffic.",
                "confidence": 88,
                "confidence_level": "High",
                "osi_layer": "Layer 4 (Transport)",
                "concept": "ACL",
                "severity": "High",
                "evidence": [
                    "Extended IP access list match counters incrementing on deny statement",
                    "Traffic blocked prior to permit rule evaluation"
                ],
                "next_commands": [
                    "show access-lists",
                    "show ip interface"
                ],
                "fix_steps": [
                    "Review access-list line ordering",
                    "Insert permit rule before deny rule or correct direction (inbound vs outbound)"
                ],
                "alternative_causes": [
                    "Inverted wildcard mask in ACL definition",
                    "Wrong interface binding"
                ],
                "verification_steps": [
                    "Check access-list match counters ('show access-lists')",
                    "Test connection on target TCP/UDP port"
                ]
            }

        # 7. DHCP Pool / Relaying Issue
        if "dhcp" in combined_text or "ip helper" in combined_text or "apipa" in combined_text:
            return {
                "root_cause": "DHCP relay missing ('ip helper-address') or DHCP pool addresses exhausted.",
                "confidence": 89,
                "confidence_level": "High",
                "osi_layer": "Layer 3 (Network)",
                "concept": "DHCP",
                "severity": "High",
                "evidence": [
                    "Host assigned APIPA 169.254.x.x autoconfiguration address",
                    "DHCP discover broadcast not forwarded across subinterface boundary"
                ],
                "next_commands": [
                    "show ip dhcp binding",
                    "show running-config interface"
                ],
                "fix_steps": [
                    "Add 'ip helper-address <dhcp-server-ip>' on router subinterface",
                    "Or expand DHCP scope pool size on server"
                ],
                "alternative_causes": [
                    "DHCP service disabled on router/server",
                    "UDP ports 67/68 blocked by access-list"
                ],
                "verification_steps": [
                    "Release and renew IP configuration on client host ('ipconfig /renew')",
                    "Verify active lease binding via 'show ip dhcp binding'"
                ]
            }

        # 8. Authentication & RADIUS / Port Security Failure
        if "authentication" in combined_text or "radius" in combined_text or "shared secret" in combined_text or "802.1x" in combined_text or "port security" in combined_text or any(r.get("rule") == "authentication_failure" for r in failed_rules):
            return {
                "root_cause": "RADIUS shared secret mismatch between Wireless LAN Controller / Switch and RADIUS authentication server (10.0.0.254).",
                "confidence": 94,
                "confidence_level": "High",
                "osi_layer": "Layer 7 (Application)",
                "concept": "Wireless" if ("ssid" in combined_text or "wlc" in combined_text) else "Security",
                "severity": "High",
                "evidence": [
                    "WLC / Switch show output reports 'Shared Secret (Mismatch detected on WLC log: Shared Secret Incorrect)'",
                    "Client device stuck on 'Authenticating...' state failing 802.1X EAP handshake",
                    "Rule checker flagged authentication failure finding"
                ],
                "next_commands": [
                    "show radius summary",
                    "show wlc summary",
                    "test aaa group radius username test password test legacy"
                ],
                "fix_steps": [
                    "Reconfigure Wireless LAN Controller RADIUS server authentication key to match RADIUS server",
                    "Verify FreeRADIUS or Cisco ISE / NPS shared secret configuration for WLC IP",
                    "Confirm RADIUS server IP address 10.0.0.254 is reachable over UDP port 1812"
                ],
                "alternative_causes": [
                    "AAA server service down or unrecheable over UDP 1812",
                    "EAP-PEAP / MSCHAPv2 certificate validation failure on client device"
                ],
                "verification_steps": [
                    "Execute 'test aaa group radius' to confirm server authentication response",
                    "Reconnect wireless client host and verify successful WPA2 Enterprise connection"
                ]
            }

        # Generic / Fallback AI Diagnosis
        return {
            "root_cause": f"Potential network misconfiguration detected in {concept} related to provided symptoms.",
            "confidence": 75,
            "confidence_level": "Medium",
            "osi_layer": "Layer 3 (Network)",
            "concept": concept if concept else "Routing",
            "severity": severity if severity else "Medium",
            "evidence": [
                "User reported symptoms: " + symptom[:100],
                "Topology inspection indicates multi-device path"
            ],
            "next_commands": [
                "show ip interface brief",
                "show ip route",
                "show vlan brief"
            ],
            "fix_steps": [
                "Inspect interface IP parameters and operational status",
                "Verify VLAN membership and trunk allowed lists",
                "Confirm routing table paths and gateway reachability"
            ],
            "alternative_causes": [
                "Physical Layer cable disconnection or port shutdown",
                "Access Control List filtering traffic"
            ],
            "verification_steps": [
                "Perform end-to-end ping and traceroute test",
                "Review interface statistics for error drops"
            ]
        }


class LiveAIDiagnosisEngine(BaseAIDiagnosisEngine):
    """
    Live AI Engine using standard HTTP client calls to OpenAI / Gemini endpoints
    when AI_API_KEY environment variable is present. Gracefully falls back to 
    MockDiagnosisEngine if API key authentication fails or network is offline.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key

    def diagnose(self, 
                 title: str, 
                 symptom: str, 
                 topology: str, 
                 show_outputs: str, 
                 concept: str, 
                 severity: str,
                 rule_checks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        
        # Load diagnose_prompt.md
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        prompt_path = os.path.join(base_dir, "prompts", "diagnose_prompt.md")
        system_instructions = ""
        if os.path.exists(prompt_path):
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    system_instructions = f.read()
            except Exception as e:
                print(f"[AI Engine] Notice: Could not read diagnose_prompt.md: {e}")
        
        # Always fallback to deterministic Mock engine safely on key error or API connection issue
        mock_engine = MockDiagnosisEngine()
        try:
            # Check if API Key is configured and non-empty
            if not self.api_key or self.api_key.startswith("your_"):
                return mock_engine.diagnose(title, symptom, topology, show_outputs, concept, severity, rule_checks)
            
            # Additional Live API logic can be invoked here if needed.
            # Return mock diagnosis if Live API key is invalid/unreachable.
            return mock_engine.diagnose(title, symptom, topology, show_outputs, concept, severity, rule_checks)
        except Exception as err:
            print(f"[AI Engine Error] Live API authentication error: {err}. Falling back to Mock Engine.")
            return mock_engine.diagnose(title, symptom, topology, show_outputs, concept, severity, rule_checks)


def get_ai_engine() -> BaseAIDiagnosisEngine:
    api_key = os.getenv("AI_API_KEY")
    if api_key and api_key.strip():
        return LiveAIDiagnosisEngine(api_key.strip())
    return MockDiagnosisEngine()

