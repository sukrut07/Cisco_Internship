# CASE-034: Voice VLAN Not Configured on Access Port

**Category:** VLAN  
**OSI Layer:** Layer 2  
**Concept:** VLAN  
**Severity:** MEDIUM  
**Next Command:** `show interfaces fa0/5 switchport`  

---

## 1. Symptom & Topology
- **Symptom:** IP phones connected to SW1 access ports are not getting proper QoS treatment and are in wrong VLAN. Data traffic (PC behind phone) works but voice quality is poor.
- **Topology:** `IP Phone -> SW1 Fa0/5 (should have voice vlan 10) -> CUCM`

---

## 2. Cisco Show Command Telemetry
### show vlan brief
```
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/5
10   Voice                            active    
20   Data                             active    Fa0/6
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** Voice VLAN 10 not configured on access port Fa0/5 — phone defaulting to VLAN 1

---

## 4. Remediation Steps
1. SW1(config)# interface fa0/5
2. switchport access vlan 20
3. switchport voice vlan 10
4. switchport mode access
5. spanning-tree portfast
6. Verify: show interfaces fa0/5 switchport

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
