# CASE-010: DNS Resolution Failure — IP Works

**Category:** DNS  
**OSI Layer:** Layer 7  
**Concept:** DNS  
**Severity:** MEDIUM  
**Next Command:** `nslookup server1.company.local`  

---

## 1. Symptom & Topology
- **Symptom:** Users can ping server by IP (192.168.30.10) but cannot reach it by name (server1.company.local). Web browser cannot connect to internal websites by name.
- **Topology:** `PC1 -> R1 -> DNS Server (192.168.1.100) -> Server1 (192.168.30.10)`

---

## 2. Cisco Show Command Telemetry
### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.1.1     YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** DNS server not configured or unreachable — name resolution fails

---

## 4. Remediation Steps
1. Verify DNS server IP on PC1
2. Test: nslookup server1.company.local
3. Ping DNS server: ping 192.168.1.100
4. Verify DNS service is running on server
5. Configure correct DNS server on PC1 if needed

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
