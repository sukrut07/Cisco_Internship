# CASE-015: Incorrect VLAN Access Port Assignment

**Category:** VLAN  
**OSI Layer:** Layer 2  
**Concept:** VLAN  
**Severity:** MEDIUM  
**Next Command:** `show vlan brief`  

---

## 1. Symptom & Topology
- **Symptom:** PC1 is supposed to be in VLAN 10 but is placed in VLAN 1 (default). PC1 can only reach other VLAN 1 devices but not VLAN 10 devices.
- **Topology:** `PC1 -> Fa0/1 (incorrectly in VLAN 1) -> SW1 -> VLAN 10 devices`

---

## 2. Cisco Show Command Telemetry
### show vlan brief
```
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/1, Fa0/5
10   Engineering                      active    Fa0/2, Fa0/3
```

### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
Vlan1                  192.168.1.1     YES manual up                    up
Vlan10                 192.168.10.1    YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** Port Fa0/1 assigned to VLAN 1 instead of VLAN 10

---

## 4. Remediation Steps
1. SW1(config)# interface fa0/1
2. SW1(config-if)# switchport access vlan 10
3. Verify: show vlan brief
4. Test: ping from PC1 to VLAN 10 device

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
