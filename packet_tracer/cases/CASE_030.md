# CASE-030: Routing Loop — Incorrect Static Routes

**Category:** STATIC_ROUTING  
**OSI Layer:** Layer 3  
**Concept:** Static Routing  
**Severity:** CRITICAL  
**Next Command:** `traceroute 10.10.10.10`  

---

## 1. Symptom & Topology
- **Symptom:** Traceroute to 10.10.10.10 shows packets bouncing between R1 and R2 repeatedly until TTL expires. Both routers have static routes pointing to each other for the destination.
- **Topology:** `PC1 -> R1 -> R2 -> (R1 -> R2 loop for 10.10.10.0/24)`

---

## 2. Cisco Show Command Telemetry
### show ip route
```
Codes: C - connected, S - static
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
C    10.0.0.0/30 is directly connected, GigabitEthernet0/1
S    10.10.10.0/24 [1/0] via 10.0.0.2
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** Routing loop — R1 routes to R2, R2 routes back to R1 for 10.10.10.0/24

---

## 4. Remediation Steps
1. Identify the actual location of 10.10.10.0/24
2. On the router directly connected: no ip route, add correct next-hop
3. Remove the incorrect route from the other router
4. Verify with traceroute — no loops

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
