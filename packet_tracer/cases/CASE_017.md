# CASE-017: Native VLAN Mismatch Between Switches

**Category:** TRUNKING  
**OSI Layer:** Layer 2  
**Concept:** 802.1Q Trunking  
**Severity:** MEDIUM  
**Next Command:** `show interfaces trunk`  

---

## 1. Symptom & Topology
- **Symptom:** Cisco Catalyst logs show '%CDP-4-NATIVE_VLAN_MISMATCH' warnings. Inter-switch traffic on VLAN 1 is partially working but some frames are being dropped.
- **Topology:** `SW1 (native VLAN 1) <-> trunk <-> SW2 (native VLAN 10)`

---

## 2. Cisco Show Command Telemetry
### show interfaces trunk
```
Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/1       1-4094

Port        Vlans allowed and active in management domain
Gi0/1       1,10,20

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/1       1,10,20
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** Native VLAN mismatch — SW1 uses VLAN 1, SW2 uses VLAN 10 as native VLAN

---

## 4. Remediation Steps
1. On SW2: interface gi0/1
2. switchport trunk native vlan 1
3. Or match both sides to same native VLAN
4. Verify: show interfaces trunk
5. Check CDP warnings cleared

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
