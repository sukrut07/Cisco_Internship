# CASE-016: Access Port Shutdown on Switch

**Category:** IP_ADDRESSING  
**OSI Layer:** Layer 1  
**Concept:** Interface Status  
**Severity:** HIGH  
**Next Command:** `show ip interface brief`  

---

## 1. Symptom & Topology
- **Symptom:** PC2 suddenly has no network connectivity. The port on the switch Fa0/3 shows as administratively down. All other ports are operational.
- **Topology:** `PC2 -> Fa0/3 (shutdown) -> SW1 -> network`

---

## 2. Cisco Show Command Telemetry
### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
FastEthernet0/1        unassigned      YES unset  up                    up
FastEthernet0/2        unassigned      YES unset  up                    up
FastEthernet0/3        unassigned      YES unset  administratively down down
Vlan1                  192.168.1.1     YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** FastEthernet0/3 is administratively shut down

---

## 4. Remediation Steps
1. SW1(config)# interface fa0/3
2. SW1(config-if)# no shutdown
3. Verify: show ip interface brief
4. Verify PC2 gets IP and can communicate

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
