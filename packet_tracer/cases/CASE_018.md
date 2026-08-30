# CASE-018: Wireless Guest Network Not Isolated

**Category:** WIRELESS  
**OSI Layer:** Layer 3  
**Concept:** Wireless  
**Severity:** HIGH  
**Next Command:** `show access-lists`  

---

## 1. Symptom & Topology
- **Symptom:** Guest WiFi users can access internal corporate servers at 10.0.0.0/8. Guest network should be isolated to internet-only access. Guest VLAN is VLAN 30.
- **Topology:** `Wireless AP (SSID: Guest-WiFi VLAN 30) -> SW1 -> R1 -> internal (10.0.0.0/8)`

---

## 2. Cisco Show Command Telemetry
### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
Vlan30                 192.168.30.1    YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** No ACL applied to VLAN 30 SVI to restrict access to internal networks

---

## 4. Remediation Steps
1. Create ACL to deny internal access: access-list 130 deny ip 192.168.30.0 0.0.0.255 10.0.0.0 0.255.255.255
2. Permit internet: access-list 130 permit ip any any
3. Apply to VLAN 30 SVI inbound
4. Test guest isolation

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
