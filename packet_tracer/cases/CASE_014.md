# CASE-014: OSPF Adjacency Not Forming

**Category:** DYNAMIC_ROUTING  
**OSI Layer:** Layer 3  
**Concept:** Dynamic Routing  
**Severity:** HIGH  
**Next Command:** `show ip ospf neighbor`  

---

## 1. Symptom & Topology
- **Symptom:** R1 and R2 are configured for OSPF but no neighbor adjacency forms. Routes are not being shared. Both routers show no OSPF neighbors.
- **Topology:** `R1 (OSPF Area 0, Gi0/0: 10.1.1.1/30) <-> R2 (OSPF Area 0, Gi0/0: 10.1.1.2/30)`

---

## 2. Cisco Show Command Telemetry
### show ip route
```
Codes: C - connected, O - OSPF
C    10.1.1.0/30 is directly connected, GigabitEthernet0/0
C    192.168.1.0/24 is directly connected, GigabitEthernet0/1
```

### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    10.1.1.1        YES manual up                    up
GigabitEthernet0/1    192.168.1.1     YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** OSPF adjacency not forming — possible hello timer mismatch or missing network statement

---

## 4. Remediation Steps
1. Check OSPF config: show run | section ospf
2. Verify network statements include the connected networks
3. Check hello/dead timers: show ip ospf interface
4. Verify area numbers match
5. Check: show ip ospf neighbor

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
