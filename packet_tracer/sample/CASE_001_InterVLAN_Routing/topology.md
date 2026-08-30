# Topology Specification — NetSage-AI Enterprise Architecture (CASE-001)

## 1. Network Topology Diagram

```
                ┌────────────────────────────────────────────────────────┐
                │                  NetSage_AI_Server                     │
                │        IP: 192.168.1.10/24 | GW: 192.168.1.1           │
                │     Services: DNS (netsage.ai) + HTTP Web Console      │
                └───────────────────────────┬────────────────────────────┘
                                            │ Fa0
                                            │
                ┌───────────────────────────┴────────────────────────────┐
                │                   Switch SW1 (2960)                    │
                │             Port Fa0/1 & Gi0/1 (VLAN 1)                │
                └───────────────────────────┬────────────────────────────┘
                                            │ Gi0/1
                                            │
                ┌───────────────────────────┴────────────────────────────┐
                │                    Netsage-Gateway                     │
                │                 Cisco 1941/2911 Router                 │
                │   Gig0/0: 192.168.1.1/24  |  Gig0/1: 192.168.2.1/24    │
                └───────────────────────────┬────────────────────────────┘
                                            │ Gi0/1
                                            │
                ┌───────────────────────────┴────────────────────────────┐
                │                   Switch SW2 (2960)                    │
                │            Port Gi0/1, Fa0/1, Fa0/2 (VLAN 1)           │
                └───────────────┬─────────────────────────┬──────────────┘
                                │ Fa0/1                   │ Fa0/2
                                │                         │
        ┌───────────────────────┴──────┐   ┌──────────────┴───────────────┐
        │           Admin-PC           │   │          Client-PC1          │
        │    IP: 192.168.2.10/24       │   │    IP: 192.168.2.20/24       │
        │    GW: 192.168.2.1           │   │    GW: 192.168.2.1           │
        │    DNS: 192.168.1.10         │   │    DNS: 192.168.1.10         │
        └──────────────────────────────┘   └──────────────────────────────┘
```

---

## 2. IP Addressing & Configuration Plan

| Device Name | Interface | IP Address | Subnet Mask | Default Gateway | Device Role / Function |
|---|---|---|---|---|---|
| **Netsage-Gateway** | `Gig0/0` | `192.168.1.1` | `255.255.255.0` | N/A | Default Gateway for Server Subnet (Subnet A) |
| **Netsage-Gateway** | `Gig0/1` | `192.168.2.1` | `255.255.255.0` | N/A | Default Gateway for Client LAN (Subnet B) |
| **NetSage_AI_Server** | `Fa0` | `192.168.1.10` | `255.255.255.0` | `192.168.1.1` | AI Core, HTTP Dashboard & DNS Server |
| **Admin-PC** | `Fa0` | `192.168.2.10` | `255.255.255.0` | `192.168.2.1` | Administrator Workstation (DNS: 192.168.1.10) |
| **Client-PC1** | `Fa0` | `192.168.2.20` | `255.255.255.0` | `192.168.2.1` | End-User Client Simulation Node |
| **SW1** | `Vlan1` | `192.168.1.2` | `255.255.255.0` | `192.168.1.1` | Server Switch Management |
| **SW2** | `Vlan1` | `192.168.2.2` | `255.255.255.0` | `192.168.2.1` | Client Switch Management |

---

## 3. Port Connections & Cabling

| Local Device | Local Port | Remote Device | Remote Port | Cable Type | Mode |
|---|---|---|---|---|---|
| `NetSage_AI_Server` | `FastEthernet0` | `SW1` | `FastEthernet0/1` | Straight-through | Access VLAN 1 |
| `SW1` | `GigabitEthernet0/1` | `Netsage-Gateway` | `GigabitEthernet0/0` | Straight-through | Routed Subnet A |
| `Netsage-Gateway` | `GigabitEthernet0/1` | `SW2` | `GigabitEthernet0/1` | Straight-through | Routed Subnet B |
| `Admin-PC` | `FastEthernet0` | `SW2` | `FastEthernet0/1` | Straight-through | Access VLAN 1 |
| `Client-PC1` | `FastEthernet0` | `SW2` | `FastEthernet0/2` | Straight-through | Access VLAN 1 |
