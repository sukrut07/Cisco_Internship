# Broken State Specification — CASE-001: Inter-VLAN Routing

## 1. Fault Summary

| Property | Value |
|---|---|
| **Case ID** | `CASE-001` |
| **Title** | Inter-VLAN Routing & Server Connectivity Failure |
| **Primary Fault** | Router R1 interface `GigabitEthernet0/1` towards Server VLAN 30 is `administratively down`, causing the destination route `192.168.30.0/24` to be absent from the FIB. |
| **OSI Layer** | Layer 3 (Network) |
| **Concept Tag** | Inter-VLAN Routing / Interface State |
| **Severity** | HIGH |

---

## 2. Observed Symptoms

- **PC-1 (`192.168.10.10`)**:
  - Local Gateway Ping (`ping 192.168.10.1`): **SUCCESS (100% reply)**
  - Inter-VLAN Staff Ping (`ping 192.168.20.10`): **SUCCESS (100% reply)**
  - Server Ping (`ping 192.168.30.10`): **FAILURE (Destination host unreachable / Request timed out)**
- **Packet Drop Point**: Router R1 drops packets destined for `192.168.30.10` due to missing active route / link down state on `Gi0/1`.

---

## 3. Broken CLI Telemetry (`show` Commands)

### A. `show ip route` on R1
```
Gateway of last resort is not set

C    192.168.10.0/24 is directly connected, GigabitEthernet0/0.10
L    192.168.10.1/32 is directly connected, GigabitEthernet0/0.10
C    192.168.20.0/24 is directly connected, GigabitEthernet0/0.20
L    192.168.20.1/32 is directly connected, GigabitEthernet0/0.20
```
*(Notice: Destination subnet `192.168.30.0/24` is absent from routing table).*

### B. `show ip interface brief` on R1
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    unassigned      YES unset  up                    up
GigabitEthernet0/0.10 192.168.10.1    YES manual up                    up
GigabitEthernet0/0.20 192.168.20.1    YES manual up                    up
GigabitEthernet0/1    192.168.30.1    YES manual administratively down down
```
*(Evidence: Interface Gi0/1 is administratively down).*

### C. `show interfaces trunk` on SW1
```
Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/1       10,20
```
*(Evidence: Trunk encapsulation and allowed VLANs 10,20 are correctly functioning between SW1 and R1).*
