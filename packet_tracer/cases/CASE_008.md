# CASE-008: DHCP Server Not Reachable — APIPA Address

**Category:** DHCP  
**OSI Layer:** Layer 3  
**Concept:** DHCP  
**Severity:** HIGH  
**Next Command:** `show ip dhcp binding`  

---

## 1. Symptom & Topology
- **Symptom:** PC1 received IP address 169.254.45.32 after connecting to the network. The PC cannot communicate with any other device. DHCP server is located at 192.168.10.254.
- **Topology:** `PC1 -> SW1 -> R1 -> DHCP Server (192.168.10.254)`

---

## 2. Cisco Show Command Telemetry
### show ip dhcp binding
```
IP address       Client-ID/         Lease expiration        Type
                 Hardware address
```

### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.10.1    YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** PC1 received APIPA address — DHCP server unreachable

---

## 4. Remediation Steps
1. Verify DHCP server is running
2. Check DHCP pool: show ip dhcp pool
3. If DHCP is on different subnet, configure DHCP relay: ip helper-address 192.168.10.254
4. Release/renew: ipconfig /renew

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
