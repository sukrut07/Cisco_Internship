# CASE-026: VLAN Pruned from Trunk

**Category:** VLAN  
**OSI Layer:** Layer 2  
**Concept:** VLAN  
**Severity:** HIGH  
**Next Command:** `show interfaces trunk`  

---

## 1. Symptom & Topology
- **Symptom:** VLAN 100 traffic is not crossing the trunk between SW1 and SW2. VLAN 100 exists on both switches but hosts cannot communicate across the trunk.
- **Topology:** `PC1 (VLAN 100) on SW1 <-> trunk <-> SW2 (VLAN 100) -> PC2`

---

## 2. Cisco Show Command Telemetry
### show interfaces trunk
```
Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/1       1-99,101-4094

Port        Vlans allowed and active in management domain
Gi0/1       1,10,20
```

### show vlan brief
```
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    
10   Data                             active    Fa0/1
20   Voice                            active    Fa0/2
100  Management                       active    Fa0/10
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** VLAN 100 is not allowed on the trunk (allowed: 1-99, 101-4094 excludes 100)

---

## 4. Remediation Steps
1. SW1(config)# interface gi0/1
2. switchport trunk allowed vlan add 100
3. Repeat on SW2
4. Verify: show interfaces trunk

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
