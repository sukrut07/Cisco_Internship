# CASE-003: Duplicate IP Address Conflict

**Category:** IP_ADDRESSING  
**OSI Layer:** Layer 3  
**Concept:** IP Addressing  
**Severity:** HIGH  
**Next Command:** `show ip arp`  

---

## 1. Symptom & Topology
- **Symptom:** PC1 and PC2 intermittently lose connectivity. ARP conflicts appear. Users report random disconnections on the network.
- **Topology:** `PC1 (192.168.1.10/24) and PC2 (192.168.1.10/24) both connected to SW1`

---

## 2. Cisco Show Command Telemetry
### show ip interface brief
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.1.1     YES manual up                    up
```


---

## 3. Expected Fault & Root Cause
**Expected Fault:** Duplicate IP address 192.168.1.10 assigned to both PC1 and PC2

---

## 4. Remediation Steps
1. Identify both devices with 'arp -a'
2. Change PC2 IP to 192.168.1.11
3. Verify no duplicate exists
4. Test connectivity from both PCs

---

## 5. Packet Tracer Mapping
- **Lab Status:** Verified Lab Scenario
- **Dataset Link:** Listed in `dataset/cases.csv` and `backend/data/seed_cases.json`
