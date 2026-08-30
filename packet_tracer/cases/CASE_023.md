# CASE-023: EIGRP Network Statement Missing

**Category:** DYNAMIC_ROUTING  
**OSI Layer:** Layer 3  
**Concept:** Dynamic Routing  
**Severity:** HIGH  
**Next Command:** `show ip eigrp topology`  

---

## 1. Symptom & Topology
- **Symptom:** R1 and R2 are EIGRP neighbors but R2 is not advertising the 192.168.50.0/24 network. Hosts in that network cannot be reached from R1.
- **Topology:** `R1 (EIGRP AS 100) <-> R2 (EIGRP AS 100, has 192.168.50.0/24)`

---

## 2. Cisco Show Command Telemetry
### show ip route
```
Codes: D - EIGRP, C - connected
C    10.0.0.0/30 is directly connected, GigabitEthernet0/0
D    192.168.40.0/24 [90/2172416] via 10.0.0.2
C    192.168.1.0/24 is directly connected, GigabitEthernet0/1
```

### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    10.0.0.1        YES manual up                    up
GigabitEthernet0/1    192.168.1.1     YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** EIGRP network statement missing for 192.168.50.0/24 on R2

---

## 4. Remediation Steps
1. On R2: router eigrp 100
2. network 192.168.50.0 0.0.0.255
3. Verify: show ip eigrp topology
4. Test: ping 192.168.50.x from R1

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
