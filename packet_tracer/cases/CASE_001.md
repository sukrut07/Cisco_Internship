# CASE-001: Missing Static Route to Server Network

**Category:** STATIC_ROUTING  
**OSI Layer:** Layer 3  
**Concept:** Static Routing  
**Severity:** HIGH  
**Next Command:** `show ip route`  

---

## 1. Symptom & Topology
- **Symptom:** PC can ping the default gateway (192.168.1.1) but cannot reach the server at 192.168.30.10. Traceroute shows the packet is dropped at the router.
- **Topology:** `PC1 (192.168.1.10/24) -> SW1 -> R1 (Gi0/0: 192.168.1.1, Gi0/1: 10.0.0.1) -> R2 (Gi0/0: 10.0.0.2, Gi0/1: 192.168.30.1) -> Server1 (192.168.30.10/24)`

---

## 2. Cisco Show Command Telemetry
### show ip route
```
Codes: C - connected, S - static, R - RIP
Gateway of last resort is not set
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
C    10.0.0.0/30 is directly connected, GigabitEthernet0/1
```

### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.1.1     YES manual up                    up
GigabitEthernet0/1    10.0.0.1        YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** Missing static route to 192.168.30.0/24 via 10.0.0.2

---

## 4. Remediation Steps
1. On R1: ip route 192.168.30.0 255.255.255.0 10.0.0.2
2. Verify: show ip route 192.168.30.0
3. Test: ping 192.168.30.10 from PC1

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
