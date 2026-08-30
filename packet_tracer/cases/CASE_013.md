# CASE-013: Incorrect Next-Hop in Static Route

**Category:** STATIC_ROUTING  
**OSI Layer:** Layer 3  
**Concept:** Static Routing  
**Severity:** HIGH  
**Next Command:** `show ip route`  

---

## 1. Symptom & Topology
- **Symptom:** PC1 cannot reach server1. The routing table on R1 shows a route to 192.168.30.0/24 but the next-hop 10.0.0.5 is unreachable. Traffic is being blackholed.
- **Topology:** `PC1 -> R1 (incorrect route: 192.168.30.0/24 via 10.0.0.5) -> Server1 (actual path via 10.0.0.2)`

---

## 2. Cisco Show Command Telemetry
### show ip route
```
Codes: C - connected, S - static
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
C    10.0.0.0/30 is directly connected, GigabitEthernet0/1
S    192.168.30.0/24 [1/0] via 10.0.0.5
```

### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.1.1     YES manual up                    up
GigabitEthernet0/1    10.0.0.1        YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** Static route next-hop 10.0.0.5 is incorrect (should be 10.0.0.2)

---

## 4. Remediation Steps
1. Remove incorrect route: no ip route 192.168.30.0 255.255.255.0 10.0.0.5
2. Add correct route: ip route 192.168.30.0 255.255.255.0 10.0.0.2
3. Verify: show ip route 192.168.30.0
4. Test: ping 192.168.30.10

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
