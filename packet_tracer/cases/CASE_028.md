# CASE-028: DHCP Pool Exhausted

**Category:** DHCP  
**OSI Layer:** Layer 3  
**Concept:** DHCP  
**Severity:** MEDIUM  
**Next Command:** `show ip dhcp binding`  

---

## 1. Symptom & Topology
- **Symptom:** Some new PCs in VLAN 10 cannot get IP addresses. Existing PCs work fine. The DHCP pool was created with 20 addresses for 30 users.
- **Topology:** `30 PCs -> SW1 -> R1 (DHCP Server, pool: 192.168.10.10-192.168.10.29)`

---

## 2. Cisco Show Command Telemetry
### show ip dhcp binding
```
IP address       Client-ID/         Lease expiration        Type
192.168.10.10    0100.AABB.CC01     Sep 01 2025 08:00 AM    Automatic
192.168.10.11    0100.AABB.CC02     Sep 01 2025 08:00 AM    Automatic
192.168.10.29    0100.AABB.CC20     Sep 01 2025 08:00 AM    Automatic
```

### show ip dhcp pool
```
Pool LAN-POOL :
 Network: 192.168.10.0/24
 Domain Name: company.local
 DNS server: 192.168.10.254
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** DHCP pool has 20 addresses for 30 users — pool exhausted

---

## 4. Remediation Steps
1. Expand DHCP pool range
2. R1(config)# ip dhcp pool LAN-POOL
3. network 192.168.10.0 255.255.255.0
4. Or exclude fewer addresses to free more
5. Consider reducing lease time

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
