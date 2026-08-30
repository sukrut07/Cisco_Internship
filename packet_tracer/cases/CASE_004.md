# CASE-004: Interface Administratively Shut Down

**Category:** IP_ADDRESSING  
**OSI Layer:** Layer 1  
**Concept:** Interface Status  
**Severity:** HIGH  
**Next Command:** `show ip interface brief`  

---

## 1. Symptom & Topology
- **Symptom:** PC1 cannot communicate with any device. The switch port connected to R1 Gi0/1 shows no link. The uplink between SW1 and R1 is suspected to be down.
- **Topology:** `PC1 -> SW1 -> R1 (Gi0/1 shutdown) -> Server1`

---

## 2. Cisco Show Command Telemetry
### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.1.1     YES manual up                    up
GigabitEthernet0/1    10.0.0.1        YES manual administratively down down
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** Interface GigabitEthernet0/1 is administratively shut down

---

## 4. Remediation Steps
1. On R1: interface GigabitEthernet0/1
2. no shutdown
3. Verify: show ip interface brief
4. Test connectivity

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
