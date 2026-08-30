# CASE-011: ACL Blocking Traffic Between VLANs

**Category:** ACL  
**OSI Layer:** Layer 4  
**Concept:** ACL  
**Severity:** HIGH  
**Next Command:** `show access-lists`  

---

## 1. Symptom & Topology
- **Symptom:** PC1 (192.168.10.0/24) cannot reach servers in 192.168.30.0/24. Ping returns 'destination host unreachable'. Traffic in the opposite direction works fine.
- **Topology:** `PC1 (192.168.10.0/24) -> R1 (ACL 101 applied inbound on Gi0/0) -> Server1 (192.168.30.0/24)`

---

## 2. Cisco Show Command Telemetry
### show access-lists
```
Extended IP access list 101
    10 deny ip 192.168.10.0 0.0.0.255 192.168.30.0 0.0.0.255 (127 matches)
    20 permit ip any any (45 matches)
```

### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.10.1    YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** ACL 101 seq 10 explicitly denies traffic from 192.168.10.0 to 192.168.30.0

---

## 4. Remediation Steps
1. Review ACL 101 purpose: show access-lists
2. If deny is unintentional: no access-list 101 10
3. Add permit: access-list 101 10 permit ip 192.168.10.0 0.0.0.255 192.168.30.0 0.0.0.255
4. Reorder if needed
5. Test connectivity

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
