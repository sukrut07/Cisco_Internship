# CASE-005: VLAN Not Created in VLAN Database

**Category:** VLAN  
**OSI Layer:** Layer 2  
**Concept:** VLAN  
**Severity:** HIGH  
**Next Command:** `show vlan brief`  

---

## 1. Symptom & Topology
- **Symptom:** PC1 in VLAN 20 (Sales) cannot communicate with PC2 in VLAN 20 on a different switch port. VLAN 20 is not visible in the VLAN database.
- **Topology:** `PC1 (VLAN 20) -> Fa0/1 -> SW1 -> Fa0/2 -> PC2 (VLAN 20)`

---

## 2. Cisco Show Command Telemetry
### show vlan brief
```
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/3, Fa0/4, Fa0/5
1002 fddi-default                     act/unsup
1003 token-ring-default               act/unsup
1004 fddinet-default                  act/unsup
1005 trnet-default                    act/unsup
```

### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
Vlan1                  192.168.1.1     YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** VLAN 20 does not exist in the VLAN database

---

## 4. Remediation Steps
1. SW1(config)# vlan 20
2. SW1(config-vlan)# name Sales
3. SW1(config)# interface fa0/1
4. SW1(config-if)# switchport access vlan 20
5. Verify: show vlan brief

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
