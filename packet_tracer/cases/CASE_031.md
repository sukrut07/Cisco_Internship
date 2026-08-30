# CASE-031: ACL Implicit Deny Blocking Required Traffic

**Category:** ACL  
**OSI Layer:** Layer 4  
**Concept:** ACL  
**Severity:** CRITICAL  
**Next Command:** `show access-lists`  

---

## 1. Symptom & Topology
- **Symptom:** After applying ACL 120 to block a specific subnet, all other traffic from the network stopped working. The ACL was added to block only 192.168.99.0/24.
- **Topology:** `Multiple VLANs -> R1 (ACL 120 applied) -> Server farm`

---

## 2. Cisco Show Command Telemetry
### show access-lists
```
Extended IP access list 120
    10 deny ip 192.168.99.0 0.0.0.255 any (0 matches)
    (implicit deny: 0 matches — but blocking everything)
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** ACL 120 missing final 'permit ip any any' — implicit deny blocks all traffic except denied subnet

---

## 4. Remediation Steps
1. access-list 120 permit ip any any
2. Add this as the last line
3. Verify ACL: show access-lists
4. Test connectivity for all VLANs

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
