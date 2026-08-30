# CASE-006: Wrong Subnet Mask on Host

**Category:** IP_ADDRESSING  
**OSI Layer:** Layer 3  
**Concept:** IP Addressing  
**Severity:** MEDIUM  
**Next Command:** `ipconfig /all`  

---

## 1. Symptom & Topology
- **Symptom:** PC1 can ping 192.168.1.1 but cannot ping 192.168.1.200. PC1 incorrectly believes 192.168.1.200 is on a different network due to a /25 mask instead of /24.
- **Topology:** `PC1 (192.168.1.10/25) -> SW1 -> R1 (192.168.1.1/24) -> PC2 (192.168.1.200/24)`

---

## 2. Cisco Show Command Telemetry
### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.1.1     YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** PC1 has subnet mask /25 instead of /24, causing it to think 192.168.1.200 is on a different network

---

## 4. Remediation Steps
1. Change PC1 subnet mask from 255.255.255.128 to 255.255.255.0
2. Verify IP configuration
3. Test: ping 192.168.1.200

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
