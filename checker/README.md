# Standalone Deterministic Python Rule Checker

The NetSage AI Rule Checker provides **probabilistically independent, deterministic validation** of Cisco network configurations and telemetry outputs across OSI Layers 1 through 7.

---

## 1. Architecture: AI vs Deterministic Validation

```
┌────────────────────────────────────────────────────────┐
│                   INCOMING TELEMETRY                   │
│         (Symptoms, Topology, Cisco Show Outputs)       │
└──────────────────────────┬─────────────────────────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│     NetSage AI LLM      │ │ Deterministic Checker   │
│  (Probabilistic Engine) │ │ (Python L1-L7 Rules)    │
└────────────┬────────────┘ └────────────┬────────────┘
             │                           │
             │ AI Diagnostic Hypothesis  │ Deterministic Pass/Fail
             │                           │
             └─────────────┬─────────────┘
                           ▼
             ┌───────────────────────────┐
             │  HYBRID COMPARISON ENGINE │
             │   (Agreement / Conflict)  │
             └─────────────┬─────────────┘
                           ▼
             ┌───────────────────────────┐
             │  MANDATORY HUMAN REVIEW   │
             │ (ACCEPTED/EDITED/REJECTED)│
             └───────────────────────────┘
```

---

## 2. Supported Layer 1–7 Checks

1. **Interface Status (`interface_status` - Layer 1):** Detects `administratively down` interfaces and physical layer link down states in `show ip interface brief`.
2. **Duplicate IP (`duplicate_ip` - Layer 3):** Identifies static IP collisions across devices and active ARP MAC address conflicts.
3. **Subnet Mask (`subnet_mask` - Layer 3):** Verifies that host subnet masks encompass the default gateway IP.
4. **Gateway Mismatch (`gateway_mismatch` - Layer 3):** Flags when a host default gateway points outside the local IPv4 subnet.
5. **Missing Route (`missing_route` - Layer 3):** Inspects the routing table (`show ip route`) for missing destination prefixes or absence of a default route (`0.0.0.0/0`).
6. **VLAN & Trunk Status (`vlan_status` - Layer 2):** Detects missing VLANs in the VLAN database and native VLAN mismatches across 802.1Q trunks.
7. **ACL Filter Hits (`acl_filters` - Layer 4):** Identifies active packet drops caused by explicit `deny` lines with match counters in `show access-lists`.
8. **DHCP Status / APIPA (`dhcp_status` - Layer 7):** Detects APIPA address (`169.254.x.x`) assignments and 100% pool utilization.
9. **DNS Resolution (`dns_status` - Layer 7):** Flags client resolver query timeouts and NXDOMAIN errors.
10. **NAT Configuration (`nat_status` - Layer 3):** Identifies missing `ip nat outside` or `ip nat inside` interface designations.

---

## 3. CLI Usage

### Check a Specific Case
```bash
python checker/rule_checker.py --case CASE-001
```

### Check a Custom JSON File
```bash
python checker/rule_checker.py --file path/to/telemetry.json
```

### Evaluate All 35 Seed Cases
```bash
python checker/rule_checker.py --all
```

---

## 4. Python API Usage

```python
from checker.rule_checker import DeterministicRuleChecker

checker = DeterministicRuleChecker()

telemetry = {
    "case_id": "CASE-001",
    "symptom": "PC cannot reach server at 192.168.30.10",
    "show_outputs": {
        "show ip route": "Gateway of last resort is not set\nC 192.168.10.0/24 is directly connected..."
    }
}

result = checker.evaluate_case(telemetry)
print(f"Verdict: {result['rule_engine_verdict']}")
for check in result["checks"]:
    if check["status"] == "FAIL":
        print(f"❌ {check['check']}: {check['evidence']}")
```
