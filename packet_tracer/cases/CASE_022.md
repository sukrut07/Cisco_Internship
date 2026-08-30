# CASE-022: Router-on-a-Stick — Subinterface Not Configured

**Category:** INTER_VLAN_ROUTING  
**OSI Layer:** Layer 3  
**Concept:** Inter-VLAN Routing  
**Severity:** HIGH  
**Next Command:** `show ip interface brief`  

---

## 1. Symptom & Topology
- **Symptom:** VLAN 30 hosts cannot communicate with VLAN 10 or VLAN 20 hosts. Router R1 has subinterfaces for VLAN 10 and 20 but not VLAN 30.
- **Topology:** `SW1 (trunk Gi0/0) -> R1 (Gi0/0.10, Gi0/0.20, Gi0/0.30 missing) -> inter-VLAN routing`

---

## 2. Cisco Show Command Telemetry
### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    unassigned      YES unset  up                    up
GigabitEthernet0/0.10 192.168.10.1    YES manual up                    up
GigabitEthernet0/0.20 192.168.20.1    YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** Subinterface Gi0/0.30 for VLAN 30 not configured on router

---

## 4. Remediation Steps
1. R1(config)# interface gi0/0.30
2. R1(config-subif)# encapsulation dot1q 30
3. R1(config-subif)# ip address 192.168.30.1 255.255.255.0
4. Verify: show ip interface brief
5. Test inter-VLAN routing for VLAN 30

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
