# Broken State Specification — NetSage-AI (CASE-001)

## 1. Fault Summary

| Property | Value |
|---|---|
| **Case ID** | `CASE-001` |
| **Title** | Gateway Interface Administratively Down to Server Subnet |
| **Primary Fault** | `Netsage-Gateway` router interface `GigabitEthernet0/0` towards `NetSage_AI_Server` (`192.168.1.10`) is `administratively down`, causing the destination route `192.168.1.0/24` to be absent from the FIB. |
| **OSI Layer** | Layer 3 (Network) |
| **Concept Tag** | Inter-Subnet Routing / Gateway Interface State |
| **Severity** | HIGH |

---

## 2. Observed Symptoms

- **Admin-PC (`192.168.2.10`)**:
  - Local Gateway Ping (`ping 192.168.2.1`): **SUCCESS (100% reply)**
  - Local Client Ping (`ping 192.168.2.20`): **SUCCESS (100% reply)**
  - Server Ping (`ping 192.168.1.10`): **FAILURE (Destination host unreachable / Request timed out)**
  - DNS Resolution / Web Access (`http://netsage.ai`): **FAILURE (Server uncontactable)**

---

## 3. Broken CLI Telemetry (`show` Commands)

### A. `show ip route` on Netsage-Gateway
```
Gateway of last resort is not set

C    192.168.2.0/24 is directly connected, GigabitEthernet0/1
L    192.168.2.1/32 is directly connected, GigabitEthernet0/1
```
*(Notice: Destination subnet `192.168.1.0/24` is absent from routing table).*

### B. `show ip interface brief` on Netsage-Gateway
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.1.1     YES manual administratively down down
GigabitEthernet0/1    192.168.2.1     YES manual up                    up
```
*(Evidence: Interface GigabitEthernet0/0 is administratively down).*
