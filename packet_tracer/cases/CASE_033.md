# CASE-033: RIP Routing — Auto-Summary Causing Issues

**Category:** DYNAMIC_ROUTING  
**OSI Layer:** Layer 3  
**Concept:** Dynamic Routing  
**Severity:** MEDIUM  
**Next Command:** `show ip rip database`  

---

## 1. Symptom & Topology
- **Symptom:** RIP is configured between R1 and R2. R1 has 172.16.1.0/24 and 172.16.2.0/24 subnets but R2 only learns 172.16.0.0/16 (summarized). Specific subnet routes are unreachable.
- **Topology:** `R1 (172.16.1.0/24, 172.16.2.0/24) <-> RIP <-> R2`

---

## 2. Cisco Show Command Telemetry
### show ip route
```
Codes: R - RIP, C - connected
C    10.0.0.0/30 is directly connected, GigabitEthernet0/0
R    172.16.0.0/16 [120/1] via 10.0.0.1
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** RIP auto-summary is enabled — classful summarization prevents specific subnet routes from propagating

---

## 4. Remediation Steps
1. On both routers: router rip
2. no auto-summary
3. version 2
4. Verify: show ip route (should see /24 routes)
5. Test: ping 172.16.1.1 and 172.16.2.1 from R2

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
