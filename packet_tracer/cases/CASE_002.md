# CASE-002: Wrong Default Gateway on PC

**Category:** GATEWAY  
**OSI Layer:** Layer 3  
**Concept:** Default Gateway  
**Severity:** HIGH  
**Next Command:** `ipconfig /all`  

---

## 1. Symptom & Topology
- **Symptom:** PC1 can ping other hosts on the same subnet but cannot reach any other network. PC1 shows default gateway 192.168.20.1 but is in the 192.168.10.0/24 subnet.
- **Topology:** `PC1 (192.168.10.20/24, GW: 192.168.20.1) -> SW1 -> R1 (192.168.10.1/24)`

---

## 2. Cisco Show Command Telemetry
### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.10.1    YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** Default gateway 192.168.20.1 is outside host subnet 192.168.10.0/24

---

## 4. Remediation Steps
1. Change PC1 default gateway to 192.168.10.1
2. Verify: ipconfig on PC1
3. Test: ping 192.168.10.1 (gateway)
4. Test: ping remote host

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
