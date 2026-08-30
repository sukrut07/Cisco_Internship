# CASE-007: VLAN Not Allowed on Trunk

**Category:** TRUNKING  
**OSI Layer:** Layer 2  
**Concept:** 802.1Q Trunking  
**Severity:** HIGH  
**Next Command:** `show interfaces trunk`  

---

## 1. Symptom & Topology
- **Symptom:** Inter-switch communication works for VLAN 1 but not for VLAN 10 (Engineering). VLAN 10 hosts can only ping devices on the same switch.
- **Topology:** `SW1 (Gi0/1 trunk) <-> (Gi0/1 trunk) SW2; PC1 (VLAN 10) on SW1; PC2 (VLAN 10) on SW2`

---

## 2. Cisco Show Command Telemetry
### show interfaces trunk
```
Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/1       1-9,11-4094

Port        Vlans allowed and active in management domain
Gi0/1       1

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/1       1
```

### show vlan brief
```
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    
10   Engineering                      active    Fa0/1
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** VLAN 10 is not allowed on the trunk link between SW1 and SW2

---

## 4. Remediation Steps
1. SW1(config)# interface gi0/1
2. SW1(config-if)# switchport trunk allowed vlan add 10
3. Repeat on SW2
4. Verify: show interfaces trunk

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
