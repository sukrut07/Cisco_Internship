# CASE-019: Wireless Authentication Failure

**Category:** WIRELESS  
**OSI Layer:** Layer 2  
**Concept:** Wireless  
**Severity:** MEDIUM  
**Next Command:** `show wireless client summary`  

---

## 1. Symptom & Topology
- **Symptom:** Laptop cannot connect to SSID 'Corporate-Wifi'. Authentication fails repeatedly. Other devices connect fine. The laptop was recently re-imaged.
- **Topology:** `Laptop -> AP (WPA2-Enterprise 802.1X) -> RADIUS Server (192.168.1.200)`

---

## 2. Cisco Show Command Telemetry
### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.1.1     YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** 802.1X wireless authentication failing — likely missing supplicant configuration or wrong credentials after re-image

---

## 4. Remediation Steps
1. Verify 802.1X supplicant is configured on laptop
2. Check credentials match Active Directory
3. Verify RADIUS server reachability: ping 192.168.1.200
4. Check RADIUS server logs for authentication failures
5. Re-enroll device if certificate-based auth

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
