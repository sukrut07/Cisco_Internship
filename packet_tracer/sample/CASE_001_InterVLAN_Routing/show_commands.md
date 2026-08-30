# Diagnostic Show Commands — CASE-001: Inter-VLAN Routing

This document details the Cisco CLI show commands required to troubleshoot CASE-001, why each command is executed, and what evidence it provides.

---

## 1. Required Diagnostic Commands

### Command 1: `show ip route`
- **Device:** Router `R1`
- **Purpose:** Verifies whether the router has an active route in its Forwarding Information Base (FIB) for the destination subnet `192.168.30.0/24`.
- **Fault Indicator:** `192.168.30.0/24` is absent, and no default route (`0.0.0.0/0`) exists.
- **Healthy Indicator:** `C 192.168.30.0/24 is directly connected, GigabitEthernet0/1` is present.

### Command 2: `show ip interface brief`
- **Device:** Router `R1`
- **Purpose:** Inspects physical Layer 1 and data link Layer 2 status for all router interfaces and subinterfaces.
- **Fault Indicator:** Interface `GigabitEthernet0/1` shows `Status: administratively down` and `Protocol: down`.
- **Healthy Indicator:** All active interfaces show `Status: up` and `Protocol: up`.

### Command 3: `show interfaces trunk`
- **Device:** Switch `SW1`
- **Purpose:** Confirms that 802.1Q trunking encapsulation is active on `Gi0/1` and VLANs 10 and 20 are allowed across the trunk to `R1`.
- **Fault Indicator:** `Gi0/1` in access mode, incorrect native VLAN mismatch, or VLAN 10 pruned from trunk.
- **Healthy Indicator:** `Gi0/1` shows `Status: trunking`, `Encapsulation: 802.1q`, allowed VLANs `10,20`.

### Command 4: `show vlan brief`
- **Device:** Switch `SW1` and `SW2`
- **Purpose:** Validates that VLAN 10 (Students), VLAN 20 (Staff), and VLAN 30 (Servers) exist in the VLAN database and ports are assigned correctly.
- **Healthy Indicator:** `Fa0/1` assigned to VLAN 10, `Fa0/2` assigned to VLAN 20, `Fa0/10` on SW2 assigned to VLAN 30.
