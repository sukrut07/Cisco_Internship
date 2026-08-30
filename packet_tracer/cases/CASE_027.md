# CASE-027: Physical Link Down — Cable Issue

**Category:** IP_ADDRESSING  
**OSI Layer:** Layer 1  
**Concept:** Interface Status  
**Severity:** HIGH  
**Next Command:** `show ip interface brief`  

---

## 1. Symptom & Topology
- **Symptom:** PC3 has no connectivity to any resource. The switch port Gi0/5 shows down/down status indicating a Layer 1 physical issue.
- **Topology:** `PC3 -> Gi0/5 (down/down) -> SW1 -> network`

---

## 2. Cisco Show Command Telemetry
### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/5    unassigned      YES unset  down                  down
GigabitEthernet0/1    unassigned      YES unset  up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** GigabitEthernet0/5 is physically down (down/down) — Layer 1 failure

---

## 4. Remediation Steps
1. Check physical cable connection
2. Try different cable
3. Try different port on switch
4. Verify PC NIC is operational
5. After fix: show ip interface brief

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
