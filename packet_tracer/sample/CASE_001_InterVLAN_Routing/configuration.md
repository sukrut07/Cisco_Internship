# Cisco IOS Configuration Scripts — CASE-001: Inter-VLAN Routing

This document provides copy-paste ready Cisco IOS configuration commands for Cisco Packet Tracer.

---

## 1. Switch 1 (SW1) Configuration (Catalyst 2960)

```cisco
enable
configure terminal
hostname SW1

! Create VLANs
vlan 10
 name Students
vlan 20
 name Staff
exit

! Configure Access Ports
interface FastEthernet0/1
 description PC-1 Connection (Students)
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown
exit

interface FastEthernet0/2
 description PC-2 Connection (Staff)
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 no shutdown
exit

! Configure 802.1Q Trunk Uplink to Router R1
interface GigabitEthernet0/1
 description Trunk to Router R1 Gi0/0
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 no shutdown
exit

end
write memory
```

---

## 2. Switch 2 (SW2) Configuration (Catalyst 2960)

```cisco
enable
configure terminal
hostname SW2

! Create Server VLAN
vlan 30
 name Servers
exit

! Configure Server Access Port
interface FastEthernet0/10
 description Server-1 Connection
 switchport mode access
 switchport access vlan 30
 spanning-tree portfast
 no shutdown
exit

! Configure Link to Router R1
interface GigabitEthernet0/1
 description Link from Router R1 Gi0/1
 switchport mode access
 switchport access vlan 30
 no shutdown
exit

end
write memory
```

---

## 3. Router R1 Configuration — Baseline (BROKEN STATE)

In this broken baseline state, router `R1` has subinterfaces for VLAN 10 and 20 configured, but the interface or route towards the Server network (`192.168.30.0/24`) is administratively shutdown or missing the IP configuration on `Gi0/1`.

```cisco
enable
configure terminal
hostname R1

! Enable Physical Interface connected to SW1 trunk
interface GigabitEthernet0/0
 no ip address
 no shutdown
exit

! Configure Subinterface for VLAN 10 (Students Gateway)
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
 no shutdown
exit

! Configure Subinterface for VLAN 20 (Staff Gateway)
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
 no shutdown
exit

! FAULT INJECTION: Interface Gi0/1 connected to Server switch is shutdown
interface GigabitEthernet0/1
 description Link to SW2 (Server Subnet)
 ip address 192.168.30.1 255.255.255.0
 shutdown
exit

end
write memory
```

---

## 4. Router R1 Remediation Commands (FIXED STATE)

```cisco
enable
configure terminal

interface GigabitEthernet0/1
 description Link to SW2 (Server Subnet)
 ip address 192.168.30.1 255.255.255.0
 no shutdown
exit

end
write memory
```
