# CASE-025: NAT Inside Interface Not Configured

**Category:** NAT  
**OSI Layer:** Layer 3  
**Concept:** NAT  
**Severity:** HIGH  
**Next Command:** `show ip nat statistics`  

---

## 1. Symptom & Topology
- **Symptom:** Internal hosts cannot reach the internet. NAT statistics show 0 translations despite traffic being sent. NAT overload is configured but inside interface designation is missing.
- **Topology:** `PC1 (192.168.1.10) -> R1 (Gi0/0: inside? Gi0/1: outside) -> Internet`

---

## 2. Cisco Show Command Telemetry
### show ip nat translations
```
Pro Inside global       Inside local        Outside local       Outside global
```

### show ip nat statistics
```
Total active translations: 0 (0 static, 0 dynamic; 0 extended)
Outside interfaces:
  GigabitEthernet0/1
Inside interfaces:
Hits: 0  Misses: 120
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** NAT inside interface not configured on Gi0/0 — no 'ip nat inside' command applied

---

## 4. Remediation Steps
1. R1(config)# interface gi0/0
2. R1(config-if)# ip nat inside
3. Verify: show ip nat statistics (inside interfaces should now show Gi0/0)
4. Test: ping 8.8.8.8 from internal host

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
