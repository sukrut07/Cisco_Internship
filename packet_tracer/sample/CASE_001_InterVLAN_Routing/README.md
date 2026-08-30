# CASE-001: Inter-VLAN Routing Failure (Primary Sample Case)

**Topology Name:** Inter-VLAN Routing & Server Connectivity  
**Target Sample File:** `NetSageAI_Sample_Case_01_InterVLAN_Routing.pkt`  
**OSI Layer:** Layer 3 (Network)  
**Concept:** Inter-VLAN Routing / Router-on-a-Stick / Missing Route  
**Severity:** HIGH  

---

## 1. Case Overview

Students in VLAN 10 (IP: `192.168.10.10`) can reach their local default gateway on router `R1` (`192.168.10.1`), but cannot access the application server located in the Server VLAN 30 (`192.168.30.10`).

This case demonstrates the full NetSage AI workflow:
1. **Broken State:** PC-1 pings gateway successfully, server fails.
2. **Telemetry Ingestion:** `show ip route`, `show ip interface brief`, and `show interfaces trunk` provided to NetSage AI.
3. **AI Diagnosis:** Identifies missing route / missing subinterface for `192.168.30.0/24`.
4. **Deterministic Rule Validation:** Python rule checker confirms destination route absence in routing table.
5. **Human Review:** Engineer approves diagnosis and stages CLI remediation commands.
6. **Fix Applied:** Router configuration updated.
7. **Verification:** ICMP echo replies succeed from PC-1 to Server-1.

---

## 2. Directory Contents

- [topology.md](file:///Users/sukrutdusane/Documents/Projects%20/Sy/cisco/packet_tracer/sample/CASE_001_InterVLAN_Routing/topology.md): ASCII diagrams and interface connection table.
- [configuration.md](file:///Users/sukrutdusane/Documents/Projects%20/Sy/cisco/packet_tracer/sample/CASE_001_InterVLAN_Routing/configuration.md): Cisco IOS configuration commands for SW1, SW2, and R1.
- [broken_state.md](file:///Users/sukrutdusane/Documents/Projects%20/Sy/cisco/packet_tracer/sample/CASE_001_InterVLAN_Routing/broken_state.md): Fault specification, ping results, and evidence.
- [fixed_state.md](file:///Users/sukrutdusane/Documents/Projects%20/Sy/cisco/packet_tracer/sample/CASE_001_InterVLAN_Routing/fixed_state.md): Remediation commands and verification tests.
- [show_commands.md](file:///Users/sukrutdusane/Documents/Projects%20/Sy/cisco/packet_tracer/sample/CASE_001_InterVLAN_Routing/show_commands.md): Explanation of diagnostic commands.
- [show_outputs_before.txt](file:///Users/sukrutdusane/Documents/Projects%20/Sy/cisco/packet_tracer/sample/CASE_001_InterVLAN_Routing/show_outputs_before.txt): Telemetry before remediation.
- [show_outputs_after.txt](file:///Users/sukrutdusane/Documents/Projects%20/Sy/cisco/packet_tracer/sample/CASE_001_InterVLAN_Routing/show_outputs_after.txt): Telemetry after remediation.
- [expected_diagnosis.json](file:///Users/sukrutdusane/Documents/Projects%20/Sy/cisco/packet_tracer/sample/CASE_001_InterVLAN_Routing/expected_diagnosis.json): Strict JSON diagnostic contract.
