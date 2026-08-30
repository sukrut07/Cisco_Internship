# NetSage AI — 5–10 Minute Demo Video Walkthrough Script

This script outlines the exact timestamped narration and screen actions for the 5–10 minute video demonstration required for the Cisco-AICTE VIP 2026 project submission.

---

## 1. Demo Video Timeline & Narration

| Timestamp | Section | Screen Action | Voiceover / Talking Points |
|---|---|---|---|
| **0:00 – 0:45** | **Introduction** | Show NetSage AI Architecture slide / Web Dashboard homepage | *"Hello evaluators. This is our project, NetSage AI, built for the Cisco-AICTE Virtual Internship Program 2026. NetSage AI is an AI-assisted network troubleshooting assistant that bridges probabilistic generative AI with deterministic Layer 1–7 Python validation and mandatory human-in-the-loop oversight."* |
| **0:45 – 1:45** | **Broken Lab Demonstration** | Open Cisco Packet Tracer (`NetSageAI_Sample_Case_01_InterVLAN_Routing.pkt`) | *"Here is our Packet Tracer scenario: CASE-001. We have Students in VLAN 10, Staff in VLAN 20, and a Server in VLAN 30 connected via Router R1. Notice on PC-1 that pinging our local default gateway 192.168.10.1 succeeds immediately, but attempting to reach the server at 192.168.30.10 fails with 'Destination host unreachable'."* |
| **1:45 – 2:45** | **Show Command Telemetry Collection** | CLI window of Router R1 and Switch SW1 in Packet Tracer | *"As a network engineer, we collect show command outputs: 'show ip interface brief' and 'show ip route' on Router R1, and 'show interfaces trunk' on Switch SW1. Notice that on R1, interface GigabitEthernet0/1 is administratively down, and the 192.168.30.0/24 subnet is completely missing from the routing table."* |
| **2:45 – 3:45** | **NetSage AI Diagnosis** | Switch to NetSage AI Web Interface / API Diagnostic View | *"We submit the symptoms and show outputs into NetSage AI. The AI Grounds its diagnosis strictly against the telemetry without hallucination, outputting: Root Cause: 'Router R1 interface Gi0/1 is administratively down', Confidence Score: 0.94 High, OSI Layer 3, with exact line citations and recommended fix steps."* |
| **3:45 – 4:45** | **Deterministic Rule Checker** | Terminal running `python checker/rule_checker.py --case CASE-001` | *"Simultaneously, our independent Python Rule Checker evaluates the network mathematically without calling an LLM. It detects that the destination route is absent and that Gi0/1 is administratively shut down, achieving full agreement with the AI diagnosis."* |
| **4:45 – 5:45** | **Mandatory Human Review Gateway** | NetSage AI Review Modal (`ACCEPTED`, `EDITED`, `REJECTED`) | *"Crucially, NetSage AI enforces mandatory human review. The system blocks automated execution. As the engineer, we review the evidence, approve the diagnosis with 'ACCEPTED', and stage the remediation commands."* |
| **5:45 – 6:45** | **Applying the Fix in Packet Tracer** | Router R1 CLI in Packet Tracer | *"Now we apply the approved fix: 'configure terminal', 'interface GigabitEthernet0/1', 'no shutdown'. Interface Gi0/1 transitions to UP/UP state, and the connected route 192.168.30.0/24 is immediately installed into the routing table."* |
| **6:45 – 7:45** | **Verification & ICMP Ping** | PC-1 Command Prompt in Packet Tracer | *"We verify end-to-end connectivity. From PC-1, we ping 192.168.30.10: 4 out of 4 ICMP echo replies are received with 0% packet loss. We record the verification in NetSage AI to seal the case audit trail."* |
| **7:45 – 8:45** | **Dashboard & Responsible AI Ledger** | NetSage AI Dashboard & Discrepancy Ledger | *"Finally, we explore our Dashboard showing 35 troubleshooting cases across VLANs, Routing, ACLs, DHCP, NAT, and DNS, with an 87.2% AI-human agreement rate. We highlight our 5 documented Responsible AI cases where human engineers corrected the AI, demonstrating responsible AI governance."* |
| **8:45 – 9:30** | **Conclusion & Submission Summary** | NetSage AI Summary screen | *"NetSage AI provides a safe, deterministic, and evidence-grounded approach to network troubleshooting. Thank you!"* |

---

## 2. Key Demonstration Tips
1. Keep Packet Tracer in simulation or real-time mode with green link lights visible.
2. Show both the broken ping failure and the post-fix successful ping.
3. Show that human approval is required before the fix is staged.
4. Show the Responsible AI discrepancy ledger to prove model accountability.
