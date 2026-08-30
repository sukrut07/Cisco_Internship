# Topology Specification — CASE-001: Inter-VLAN Routing

## 1. Network Topology Diagram

```
                 ┌────────────────────────────────┐
                 │          Server-1              │
                 │ IP: 192.168.30.10/24 (VLAN 30) │
                 │ GW: 192.168.30.1               │
                 └───────────────┬────────────────┘
                                 │ Fa0
                                 │
                 ┌───────────────┴────────────────┐
                 │       Switch SW2 (2960)        │
                 │ Port Fa0/10: Access VLAN 30    │
                 │ Port Gi0/1: Access VLAN 30     │
                 └───────────────┬────────────────┘
                                 │ Gi0/1
                                 │
                 ┌───────────────┴────────────────┐
                 │        Router R1 (1941)        │
                 │ Gi0/0.10: 192.168.10.1/24 (V10)│
                 │ Gi0/0.20: 192.168.20.1/24 (V20)│
                 │ Gi0/1:    192.168.30.1/24 (V30)│
                 └───────────────┬────────────────┘
                                 │ Gi0/0 (802.1Q Trunk)
                                 │
                 ┌───────────────┴────────────────┐
                 │       Switch SW1 (2960)        │
                 │ Port Gi0/1: Trunk (VLAN 10,20) │
                 │ Port Fa0/1: Access VLAN 10     │
                 │ Port Fa0/2: Access VLAN 20     │
                 └───────┬───────────────┬────────┘
                         │ Fa0/1         │ Fa0/2
                         │               │
     ┌───────────────────┴──┐         ┌──┴───────────────────┐
     │         PC-1         │         │         PC-2         │
     │ IP: 192.168.10.10/24 │         │ IP: 192.168.20.10/24 │
     │ GW: 192.168.10.1     │         │ GW: 192.168.20.1     │
     │ VLAN 10 (Students)   │         │ VLAN 20 (Staff)      │
     └──────────────────────┘         └──────────────────────┘
```

---

## 2. IP Addressing Plan

| Device | Interface | IP Address | Subnet Mask | Default Gateway | VLAN / Description |
|---|---|---|---|---|---|
| **PC-1** | `Fa0` | `192.168.10.10` | `255.255.255.0` | `192.168.10.1` | VLAN 10 (Students) |
| **PC-2** | `Fa0` | `192.168.20.10` | `255.255.255.0` | `192.168.20.1` | VLAN 20 (Staff) |
| **Server-1** | `Fa0` | `192.168.30.10` | `255.255.255.0` | `192.168.30.1` | VLAN 30 (Servers) |
| **SW1** | `VLAN 1` (Mgmt) | `192.168.10.2` | `255.255.255.0` | `192.168.10.1` | Management |
| **SW2** | `VLAN 1` (Mgmt) | `192.168.30.2` | `255.255.255.0` | `192.168.30.1` | Management |
| **R1** | `Gi0/0.10` | `192.168.10.1` | `255.255.255.0` | N/A | Subinterface (VLAN 10) |
| **R1** | `Gi0/0.20` | `192.168.20.1` | `255.255.255.0` | N/A | Subinterface (VLAN 20) |
| **R1** | `Gi0/1` | `192.168.30.1` | `255.255.255.0` | N/A | Routed Port (VLAN 30) |

---

## 3. Port Connections & Cabling

| Local Device | Local Port | Remote Device | Remote Port | Cable Type | Mode |
|---|---|---|---|---|---|
| `PC-1` | `FastEthernet0` | `SW1` | `FastEthernet0/1` | Straight-through | Access VLAN 10 |
| `PC-2` | `FastEthernet0` | `SW1` | `FastEthernet0/2` | Straight-through | Access VLAN 20 |
| `SW1` | `GigabitEthernet0/1` | `R1` | `GigabitEthernet0/0` | Straight-through | 802.1Q Trunk |
| `R1` | `GigabitEthernet0/1` | `SW2` | `GigabitEthernet0/1` | Straight-through | Routed / Access |
| `SW2` | `FastEthernet0/10` | `Server-1` | `FastEthernet0` | Straight-through | Access VLAN 30 |
