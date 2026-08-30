# CASE-021: SVI Interface Down — Inter-VLAN Routing Fails

**Category:** INTER_VLAN_ROUTING  
**OSI Layer:** Layer 3  
**Concept:** Inter-VLAN Routing  
**Severity:** HIGH  
**Next Command:** `show ip interface brief`  

---

## 1. Symptom & Topology
- **Symptom:** Users in VLAN 20 (192.168.20.0/24) cannot reach users in VLAN 10 (192.168.10.0/24). Intra-VLAN communication works. The multilayer switch appears healthy.
- **Topology:** `PC1 (VLAN 10) -> MLS1 (SVI Vlan10: down) -> PC2 (VLAN 20)`

---

## 2. Cisco Show Command Telemetry
### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
Vlan1                  192.168.1.1     YES manual up                    up
Vlan10                 192.168.10.1    YES manual administratively down down
Vlan20                 192.168.20.1    YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** SVI Vlan10 is administratively shutdown — inter-VLAN routing fails for VLAN 10

---

## 4. Remediation Steps
1. MLS(config)# interface vlan 10
2. MLS(config-if)# no shutdown
3. Verify: show ip interface brief
4. Test: ping 192.168.10.1 from PC2

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
