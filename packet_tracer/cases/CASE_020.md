# CASE-020: Default Route Missing on Router

**Category:** STATIC_ROUTING  
**OSI Layer:** Layer 3  
**Concept:** Static Routing  
**Severity:** HIGH  
**Next Command:** `show ip route`  

---

## 1. Symptom & Topology
- **Symptom:** Internal users cannot reach any external internet resources. The router R1 has correct routes to all internal networks but no route to external networks. ISP link is up.
- **Topology:** `Internal (192.168.0.0/16) -> R1 (Gi0/1: 203.0.113.2) -> ISP Router (203.0.113.1) -> Internet`

---

## 2. Cisco Show Command Telemetry
### show ip route
```
Codes: C - connected, S - static
Gateway of last resort is not set
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
C    192.168.2.0/24 is directly connected, GigabitEthernet0/2
C    203.0.113.0/30 is directly connected, GigabitEthernet0/1
```

### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.1.1     YES manual up                    up
GigabitEthernet0/1    203.0.113.2     YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** No default route configured — 'Gateway of last resort is not set'

---

## 4. Remediation Steps
1. R1(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1
2. Verify: show ip route
3. Test: ping 8.8.8.8

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
