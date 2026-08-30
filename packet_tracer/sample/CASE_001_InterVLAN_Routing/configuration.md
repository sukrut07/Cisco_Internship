# Cisco IOS Configuration Scripts — NetSage-AI (CASE-001)

This document provides copy-paste ready Cisco IOS configuration commands for the NetSage-AI Packet Tracer topology.

---

## 1. Gateway Router Configuration (`Netsage-Gateway` - Cisco 1941/2911)

### Complete Healthy Configuration
```cisco
enable
configure terminal
hostname Netsage-Gateway

! --- Interface 0/0: Server Subnet Gateway ---
interface GigabitEthernet0/0
 description Server-Subnet-Uplink
 ip address 192.168.1.1 255.255.255.0
 no shutdown
 exit

! --- Interface 0/1: Client LAN Gateway ---
interface GigabitEthernet0/1
 description Client-LAN-Uplink
 ip address 192.168.2.1 255.255.255.0
 no shutdown
 exit

end
write memory
```

---

## 2. Intentional Fault Injection (Broken Baseline for Demo / CASE-001)

To create the **broken state** for the NetSage-AI troubleshooting demonstration:
```cisco
enable
configure terminal
hostname Netsage-Gateway

interface GigabitEthernet0/0
 description Server-Subnet-Uplink
 ip address 192.168.1.1 255.255.255.0
 shutdown
 exit

end
write memory
```

*Symptom:* `Admin-PC` (192.168.2.10) can ping default gateway `192.168.2.1` (SUCCESS) but cannot reach `NetSage_AI_Server` at `192.168.1.10` (FAILURE).

---

## 3. Router Remediation Command (Fixed State)

```cisco
enable
configure terminal
interface GigabitEthernet0/0
 no shutdown
 exit
end
write memory
```

---

## 4. End Device Configuration

### NetSage_AI_Server (Server)
- **IP Address:** `192.168.1.10`
- **Subnet Mask:** `255.255.255.0`
- **Default Gateway:** `192.168.1.1`
- **DNS Server:** `192.168.1.10`
- **DNS Service:** Enabled, A-Record `netsage.ai` $\rightarrow$ `192.168.1.10`
- **HTTP Service:** Enabled, Port 80

### Admin-PC (PC)
- **IP Address:** `192.168.2.10`
- **Subnet Mask:** `255.255.255.0`
- **Default Gateway:** `192.168.2.1`
- **DNS Server:** `192.168.1.10`

### Client-PC1 (PC)
- **IP Address:** `192.168.2.20`
- **Subnet Mask:** `255.255.255.0`
- **Default Gateway:** `192.168.2.1`
- **DNS Server:** `192.168.1.10`
