# CASE-032: Static NAT Entry Missing for Server

**Category:** NAT  
**OSI Layer:** Layer 3  
**Concept:** NAT  
**Severity:** HIGH  
**Next Command:** `show ip nat translations`  

---

## 1. Symptom & Topology
- **Symptom:** External users cannot reach the internal web server at 192.168.1.100. The server should be accessible via the public IP 203.0.113.10. NAT is configured for dynamic inside hosts.
- **Topology:** `Internet -> R1 (203.0.113.10 should map to 192.168.1.100) -> Web Server`

---

## 2. Cisco Show Command Telemetry
### show ip nat translations
```
Pro Inside global       Inside local        Outside local       Outside global
tcp 203.0.113.2:1025    192.168.1.10:1025   8.8.8.8:80          8.8.8.8:80
```

### show ip nat statistics
```
Total active translations: 1 (0 static, 1 dynamic)
Hits: 45  Misses: 3
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** Static NAT entry for web server (203.0.113.10 -> 192.168.1.100) not configured

---

## 4. Remediation Steps
1. R1(config)# ip nat inside source static 192.168.1.100 203.0.113.10
2. Verify: show ip nat translations
3. Test from external host: curl 203.0.113.10

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
