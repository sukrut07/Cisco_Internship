# Packet Tracer Labs — NetSage AI

This directory contains the Cisco Packet Tracer topology designs, device configuration scripts, CLI telemetry outputs, and fault specifications for the **NetSage AI** project.

---

## 1. Submission Structure & Guidelines

> [!IMPORTANT]
> **Instructor Submission Rule:** The final submission ZIP contains a **maximum of 3 files**:
> 1. `NetSageAI_Project_Report.pdf`
> 2. `NetSageAI_Sample_Case_01_InterVLAN_Routing.pkt` (Representative sample case)
> 3. `NetSageAI_Source_Code.zip`
>
> All 35 troubleshooting scenarios are documented in `dataset/cases.csv` and the project report, while **CASE-001 (Inter-VLAN Routing)** serves as the primary representative `.pkt` file for live demonstration and evaluation.

---

## 2. Directory Layout

```
packet_tracer/
├── README.md                      # This setup guide
├── CASE_MAPPING.md                # Mapping of dataset cases to PT topologies
├── sample/
│   ├── CASE_001_InterVLAN_Routing/# Primary Sample Case for Demo & ZIP
│   │   ├── README.md              # Case overview & instructions
│   │   ├── topology.md            # Topology diagram & device interfaces
│   │   ├── configuration.md       # Cisco IOS configuration commands
│   │   ├── broken_state.md        # Intentional fault & failure symptoms
│   │   ├── fixed_state.md         # Remediation commands & verification
│   │   ├── show_commands.md       # Required Cisco show commands
│   │   ├── show_outputs_before.txt# Telemetry before fix (broken)
│   │   ├── show_outputs_after.txt # Telemetry after fix (healthy)
│   │   ├── expected_diagnosis.json# Contract-compliant AI output
│   │   └── NetSageAI_Sample_Case_01.pkt.md # Manual creation guide
│   ├── CASE_002_ACL/
│   └── CASE_003_DHCP/
└── cases/                         # Markdown specifications for lab cases (01-20+)
    ├── CASE_001.md
    ├── CASE_002.md
    └── ...
```

---

## 3. Step-by-Step Manual Guide: Creating the `.pkt` File in Cisco Packet Tracer

To ensure 100% compatibility and avoid corrupted binary files, follow these exact steps to build and save `NetSageAI_Sample_Case_01_InterVLAN_Routing.pkt` in Cisco Packet Tracer:

### Step 1: Open Cisco Packet Tracer
Launch Cisco Packet Tracer (v8.0+ recommended).

### Step 2: Add Hardware Devices
Place the following standard devices onto the logical workspace:
- **Router R1:** Cisco 1941 or 2911 Router
- **Switch SW1:** Cisco Catalyst 2960-24TT Switch
- **Switch SW2:** Cisco Catalyst 2960-24TT Switch
- **PC-1:** Generic End Device (PC) — Students VLAN
- **PC-2:** Generic End Device (PC) — Staff VLAN
- **Server-1:** Generic Server Device — Server VLAN

### Step 3: Connect Physical Interfaces
Connect the devices using standard straight-through and crossover copper cables:
- `PC-1` (FastEthernet0) ─── `SW1` (FastEthernet0/1)
- `PC-2` (FastEthernet0) ─── `SW1` (FastEthernet0/2)
- `SW1` (GigabitEthernet0/1) ─── `R1` (GigabitEthernet0/0) [802.1Q Trunk]
- `R1` (GigabitEthernet0/1) ─── `SW2` (GigabitEthernet0/1)
- `SW2` (FastEthernet0/10) ─── `Server-1` (FastEthernet0)

### Step 4: Configure VLANs and Trunking on Switch SW1
Access `SW1` CLI and paste the configuration from [`sample/CASE_001_InterVLAN_Routing/configuration.md`](./sample/CASE_001_InterVLAN_Routing/configuration.md).

### Step 5: Configure IP Addresses on End Devices
- **PC-1:** IP `192.168.10.10`, Subnet `255.255.255.0`, Gateway `192.168.10.1`
- **PC-2:** IP `192.168.20.10`, Subnet `255.255.255.0`, Gateway `192.168.20.1`
- **Server-1:** IP `192.168.30.10`, Subnet `255.255.255.0`, Gateway `192.168.30.1`

### Step 6: Configure Router R1 (Broken Baseline)
Configure subinterfaces `Gi0/0.10` and `Gi0/0.20` for VLAN 10 and VLAN 20 on `R1`.  
**Intentional Fault:** Do NOT configure subinterface `Gi0/0.30` or omit interface `Gi0/1` addressing for the Server network `192.168.30.0/24`.

### Step 7: Verify the Broken State
From PC-1 Command Prompt:
- `ping 192.168.10.1` ─── **SUCCESS (Reply received)**
- `ping 192.168.30.10` ─── **FAILURE (Destination host unreachable / Request timed out)**

### Step 8: Capture Diagnostic Show Commands
Execute diagnostic show commands on `R1` and `SW1`:
- `show ip route`
- `show ip interface brief`
- `show interfaces trunk`
- `show vlan brief`

### Step 9: Save the Broken `.pkt` File
Save the topology file as:
`packet_tracer/sample/CASE_001_InterVLAN_Routing/NetSageAI_Sample_Case_01_InterVLAN_Routing.pkt`

### Step 10: Live Fix and Post-Verification
During demonstration, configure the missing Layer 3 route/interface on `R1`, then verify:
- PC-1 to Server-1 ping ─── **SUCCESS (5/5 replies)**
