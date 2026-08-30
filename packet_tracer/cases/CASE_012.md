# CASE-012: NAT Translation Missing — Internet Access Fails

**Category:** NAT  
**OSI Layer:** Layer 3  
**Concept:** NAT  
**Severity:** HIGH  
**Next Command:** `show ip nat statistics`  

---

## 1. Symptom & Topology
- **Symptom:** Internal hosts (192.168.1.0/24) cannot access the internet. Pinging 8.8.8.8 fails. The ISP router is reachable from R1 but internal hosts cannot reach external IPs.
- **Topology:** `PC1 (192.168.1.10) -> R1 (inside: Gi0/0, outside: Gi0/1) -> ISP (203.0.113.1) -> Internet`

---

## 2. Cisco Show Command Telemetry
### show ip nat translations
```
Pro Inside global       Inside local        Outside local       Outside global
```

### show ip nat statistics
```
Total active translations: 0 (0 static, 0 dynamic)
Outside interfaces: GigabitEthernet0/1
Inside interfaces: GigabitEthernet0/0
Hits: 0  Misses: 47
```

### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.1.1     YES manual up                    up
GigabitEthernet0/1    203.0.113.2     YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** NAT overload (PAT) not configured — no translations being created despite traffic

---

## 4. Remediation Steps
1. Create access-list: access-list 1 permit 192.168.1.0 0.0.0.255
2. Configure NAT: ip nat inside source list 1 interface gi0/1 overload
3. Verify interfaces: ip nat inside / ip nat outside
4. Test: show ip nat translations

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
