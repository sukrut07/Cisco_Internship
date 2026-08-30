# Responsible AI & Human-in-the-Loop Oversight Ledger

NetSage AI enforces **mandatory human engineer oversight** before any diagnostic hypothesis is accepted or remediation command is staged.

---

## 1. Human Decision Gateway Workflow

```
               ┌───────────────────────────┐
               │    AI DIAGNOSTIC OUTPUT   │
               │   (Hypothesis, Evidence)  │
               └─────────────┬─────────────┘
                             │
               ┌─────────────▼─────────────┐
               │    DETERMINISTIC RULES    │
               │   (Pass/Fail Validation)  │
               └─────────────┬─────────────┘
                             │
                             ▼
               ┌───────────────────────────┐
               │   HUMAN ENGINEER REVIEW   │
               └─────────────┬─────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │ ACCEPTED  │       │  EDITED   │       │ REJECTED  │
   └─────┬─────┘       └─────┬─────┘       └─────┬─────┘
         │                   │                   │
         ▼                   ▼                   ▼
   Stage Fix &         Log Override &      Halt Workflow &
   Verify Network      Stage Edited Fix    Log Correction
```

### Review Decisions
- **`ACCEPTED`**: The engineer validates that the AI root cause, cited evidence, and proposed fix steps are completely accurate.
- **`EDITED`**: The engineer adjusts the diagnosis or stages corrected fix commands because the AI missed critical context or prioritized a secondary symptom.
- **`REJECTED`**: The engineer rejects an inaccurate or unsafe AI recommendation, preventing misconfiguration.

---

## 2. Documented Responsible AI Discrepancies (5 Human Correction Cases)

The Cisco-AICTE VIP 2026 rubric explicitly requires documenting at least **5 cases where AI recommendations were corrected by a human engineer**. Rather than claiming artificial 100% accuracy, NetSage AI tracks discrepancies to calibrate confidence models and prevent network outages.

### Case 1: CASE-003 (Duplicate IP vs Interface Flapping)
- **AI Hypothesis:** Interface flapping counter incrementing on switchport.
- **Evidence AI Used:** Port state transitions and error counters in `show ip interface brief`.
- **What AI Missed:** A secondary ARP table entry with a duplicate MAC address colliding on `192.168.1.10`.
- **Human Decision:** `EDITED`
- **Human Correction:** Duplicate static IP address assigned to rogue device conflicting with PC1 ARP entry. Switchport isolated.

### Case 2: CASE-009 (Missing Route vs Extended ACL Filter)
- **AI Hypothesis:** Extended ACL 101 blocking TCP port 80 traffic.
- **Evidence AI Used:** Presence of `deny tcp any host 192.168.30.10 eq www` in `show access-lists`.
- **What AI Missed:** The ACL match counter was 0; the gateway routing table had no route for `192.168.30.0/24`, causing drops before ACL evaluation.
- **Human Decision:** `EDITED`
- **Human Correction:** Missing static route on gateway router. Configured `ip route 192.168.30.0 255.255.255.0 10.0.0.2`.

### Case 3: CASE-012 (OSPF MTU Mismatch Rejection)
- **AI Hypothesis:** OSPF adjacency failure due to MTU mismatch; recommended issuing `ip ospf mtu-ignore`.
- **Evidence AI Used:** OSPF neighbor state stuck in `EXSTART` in `show ip ospf neighbor`.
- **What AI Missed:** Applying `ip ospf mtu-ignore` is dangerous in production because it causes silent packet fragmentation and data corruption.
- **Human Decision:** `REJECTED`
- **Human Correction:** Aligned physical MTU (1500 bytes) on both sides of the transit link instead of ignoring the MTU mismatch.

### Case 4: CASE-018 (Dead VLAN Assignment vs DHCP Pool Exhaustion)
- **AI Hypothesis:** DHCP pool exhaustion on core router.
- **Evidence AI Used:** Client received APIPA `169.254.x.x` address.
- **What AI Missed:** Access switchport `FastEthernet0/5` was accidentally placed in dead/isolated VLAN 99 where no DHCP server exists.
- **Human Decision:** `EDITED`
- **Human Correction:** Reassigned switchport `Fa0/5` to Client Data VLAN 10 (`switchport access vlan 10`).

### Case 5: CASE-022 (Default Gateway Route vs DNS Timeout)
- **AI Hypothesis:** Primary DNS server resolution timeout.
- **Evidence AI Used:** `nslookup` query timed out after 2000ms.
- **What AI Missed:** The DNS server (`8.8.8.8`) was external, and the Core Switch `S1` was missing its default route (`0.0.0.0/0`), preventing all off-subnet UDP traffic.
- **Human Decision:** `EDITED`
- **Human Correction:** Configured default route on Core Switch S1 (`ip route 0.0.0.0 0.0.0.0 192.168.1.1`).
