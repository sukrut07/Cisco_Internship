# CASE-035: IP Routing Not Enabled on Multilayer Switch

**Category:** INTER_VLAN_ROUTING  
**OSI Layer:** Layer 3  
**Concept:** Inter-VLAN Routing  
**Severity:** HIGH  
**Next Command:** `show ip routing`  

---

## 1. Symptom & Topology
- **Symptom:** MLS1 is a Layer 3 capable switch with SVIs configured for VLAN 10 and VLAN 20. Hosts in different VLANs cannot communicate even though SVIs are up/up.
- **Topology:** `PC1 (VLAN 10) -> MLS1 (SVIs configured but ip routing disabled) -> PC2 (VLAN 20)`

---

## 2. Cisco Show Command Telemetry
### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
Vlan10                 192.168.10.1    YES manual up                    up
Vlan20                 192.168.20.1    YES manual up                    up
```

### show ip route
```
Default gateway is 192.168.10.254

    Network         Next Hop
*   0.0.0.0         192.168.10.254
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** 'ip routing' not enabled on multilayer switch — operating as Layer 2 switch only

---

## 4. Remediation Steps
1. MLS1(config)# ip routing
2. Verify: show ip route (should show connected routes for SVIs)
3. Test: ping 192.168.20.1 from VLAN 10 PC

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
