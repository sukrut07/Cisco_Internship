# CASE-009: DHCP Relay Agent Not Configured

**Category:** DHCP  
**OSI Layer:** Layer 3  
**Concept:** DHCP  
**Severity:** HIGH  
**Next Command:** `show ip helper-address`  

---

## 1. Symptom & Topology
- **Symptom:** PCs in VLAN 20 (192.168.20.0/24) cannot get IP addresses from the DHCP server in VLAN 10 (192.168.10.100). PCs receive APIPA addresses.
- **Topology:** `PC1 (VLAN 20) -> SW1 -> R1 (VLAN 10 SVI: 192.168.10.1, VLAN 20 SVI: 192.168.20.1) -> DHCP Server (192.168.10.100)`

---

## 2. Cisco Show Command Telemetry
### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
Vlan10                 192.168.10.1    YES manual up                    up
Vlan20                 192.168.20.1    YES manual up                    up
```

### show ip dhcp binding
```
IP address       Client-ID/         Lease expiration        Type
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** DHCP relay (ip helper-address) not configured on VLAN 20 SVI

---

## 4. Remediation Steps
1. R1(config)# interface vlan 20
2. R1(config-if)# ip helper-address 192.168.10.100
3. Verify: show ip helper-address
4. Test: ipconfig /renew on PC1

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
