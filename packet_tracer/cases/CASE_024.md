# CASE-024: ACL Blocking ICMP — Ping Fails but Telnet Works

**Category:** ACL  
**OSI Layer:** Layer 4  
**Concept:** ACL  
**Severity:** LOW  
**Next Command:** `show access-lists`  

---

## 1. Symptom & Topology
- **Symptom:** Network engineer cannot ping Router R2 but can telnet to it. Other services are working but ICMP is blocked.
- **Topology:** `Admin PC -> R1 -> R2 (ACL blocking ICMP)`

---

## 2. Cisco Show Command Telemetry
### show access-lists
```
Extended IP access list MGMT-IN
    10 deny icmp any any (234 matches)
    20 permit tcp any any eq 23 (12 matches)
    30 permit ip any any (89 matches)
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** ACL MGMT-IN seq 10 blocks ICMP before the permit ip any any rule

---

## 4. Remediation Steps
1. Evaluate if ICMP block is intentional
2. If not: no ip access-list extended MGMT-IN
3. Recreate without ICMP deny, or reorder: permit icmp any any before deny
4. Apply updated ACL
5. Test: ping R2

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
