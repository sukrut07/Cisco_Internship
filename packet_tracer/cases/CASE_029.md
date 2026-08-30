# CASE-029: Trunk Not Forming — Mode Mismatch

**Category:** TRUNKING  
**OSI Layer:** Layer 2  
**Concept:** 802.1Q Trunking  
**Severity:** HIGH  
**Next Command:** `show interfaces trunk`  

---

## 1. Symptom & Topology
- **Symptom:** SW1 and SW2 are connected but the link is not trunking. VLANs 10 and 20 cannot pass between the switches. Both ports appear up/up but as access ports.
- **Topology:** `SW1 (Gi0/1: mode access) <-> SW2 (Gi0/1: mode trunk)`

---

## 2. Cisco Show Command Telemetry
### show interfaces trunk
```
Port        Mode         Encapsulation  Status        Native vlan
(No output — no trunks active)
```

### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/1    unassigned      YES unset  up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** Trunk not forming — SW1 port in access mode while SW2 port in trunk mode

---

## 4. Remediation Steps
1. SW1(config)# interface gi0/1
2. SW1(config-if)# switchport mode trunk
3. SW1(config-if)# switchport trunk encapsulation dot1q
4. Verify: show interfaces trunk

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
