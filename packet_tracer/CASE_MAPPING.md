# Packet Tracer Case Mapping Matrix — NetSage AI

This matrix maps all 35 troubleshooting cases to their Packet Tracer topology, fault category, required CLI telemetry commands, and submission relevance.

---

## 1. Submission Relevance Legend
- **PRIMARY DEMO / SUBMISSION `.PKT`**: Representative case packaged in the 3-file ZIP submission and featured in the live demonstration video.
- **LAB SCENARIO / DATASET CASE**: Verified troubleshooting scenario included in `dataset/cases.csv` and report documentation.

---

## 2. Comprehensive 35-Case Mapping

| Case ID | Category | Title / Fault Type | Required Show Commands | Expected AI Diagnosis | Submission Relevance |
|---|---|---|---|---|---|
| **CASE-001** | `INTER_VLAN_ROUTING` | Interface Gi0/1 administratively down to Server VLAN 30 | `show ip route`, `show ip interface brief`, `show interfaces trunk` | Missing route / Admin down interface on R1 Gi0/1 | **PRIMARY DEMO & SUBMISSION `.PKT`** (`NetSageAI_Sample_Case_01_InterVLAN_Routing.pkt`) |
| **CASE-002** | `GATEWAY` | Wrong default gateway IP on PC (outside local subnet) | `ipconfig /all`, `show ip interface brief` | Default gateway mismatch outside host subnet | Lab Scenario / Dataset Case |
| **CASE-003** | `IP_ADDRESSING` | Duplicate static IP address conflict on subnet | `show ip arp`, `arp -a`, `show ip interface brief` | Duplicate IP address conflict on local segment | Lab Scenario / Responsible AI Case 1 |
| **CASE-004** | `INTERFACE` | Uplink interface administratively down | `show ip interface brief`, `show interfaces status` | Interface administratively shut down | Lab Scenario / Hero Verified Case |
| **CASE-005** | `VLAN` | Access port assigned to non-existent VLAN | `show vlan brief`, `show interfaces switchport` | VLAN not created in VLAN database | Lab Scenario / Dataset Case |
| **CASE-006** | `VLAN_TRUNK` | Native VLAN mismatch on 802.1Q trunk link | `show interfaces trunk`, `show cdp neighbors detail` | Native VLAN mismatch between switches | Lab Scenario / Dataset Case |
| **CASE-007** | `DHCP` | DHCP client receiving APIPA address (169.254.x.x) | `ipconfig /all`, `show ip dhcp binding` | DHCP server unresponsive / missing relay agent | Lab Scenario / Dataset Case |
| **CASE-008** | `DNS` | Primary DNS server IP incorrect on client | `ipconfig /all`, `nslookup server.lab.local` | DNS server IP unreachable or incorrect | Lab Scenario / Dataset Case |
| **CASE-009** | `ACL` | Extended ACL blocking HTTP/TCP port 80 traffic | `show access-lists`, `show ip route` | Inbound/Outbound ACL deny filter match | Lab Scenario / Responsible AI Case 2 |
| **CASE-010** | `NAT` | Missing `ip nat outside` on WAN uplink interface | `show ip nat translations`, `show ip interface brief` | NAT inside/outside interface designation missing | Lab Scenario / Dataset Case |
| **CASE-011** | `STATIC_ROUTING` | Next-hop IP address unreachable / incorrect | `show ip route`, `show ip arp` | Invalid next-hop static route entry | Lab Scenario / Dataset Case |
| **CASE-012** | `OSPF` | OSPF MTU mismatch preventing adjacency full state | `show ip ospf neighbor`, `show interfaces` | MTU mismatch causing OSPF stuck in EXSTART | Lab Scenario / Responsible AI Case 3 |
| **CASE-013** | `VLAN_TRUNK` | VLAN missing from allowed trunk list | `show interfaces trunk`, `show vlan brief` | Trunk pruning / missing allowed VLAN | Lab Scenario / Dataset Case |
| **CASE-014** | `DHCP` | DHCP scope pool IP exhaustion | `show ip dhcp pool`, `show ip dhcp binding` | DHCP pool exhaustion / all addresses leased | Lab Scenario / Dataset Case |
| **CASE-015** | `ACL` | Standard ACL applied in wrong direction | `show access-lists`, `show ip interface` | Outbound ACL filtering legitimate client traffic | Lab Scenario / Dataset Case |
| **CASE-016** | `SUBNET_MASK` | Incorrect subnet mask on server (`/28` vs `/24`) | `show ip interface brief`, `ipconfig /all` | Subnet mask mismatch isolating host | Lab Scenario / Dataset Case |
| **CASE-017** | `WIRELESS` | WPA2 Pre-Shared Key mismatch on AP / Client | `show running-config`, `show dot11 associations` | Wireless authentication PSK mismatch | Lab Scenario / Dataset Case |
| **CASE-018** | `VLAN` | Access switchport placed in dead/isolated VLAN | `show vlan brief`, `show interfaces FastEthernet0/5` | Access port misconfigured in dead VLAN | Lab Scenario / Responsible AI Case 4 |
| **CASE-019** | `NAT` | NAT overload pool ACL missing permit statement | `show access-lists`, `show ip nat statistics` | Dynamic NAT ACL denying client IP range | Lab Scenario / Dataset Case |
| **CASE-020** | `STP` | Spanning Tree PortFast disabled on edge port | `show spanning-tree`, `show spanning-tree interface` | STP listening/learning forward delay timeout | Lab Scenario / Dataset Case |
| **CASE-021** | `DHCP` | DHCP `ip helper-address` missing on router subinterface | `show running-config interface`, `show ip dhcp binding` | Missing DHCP relay agent on default gateway | Lab Scenario / Dataset Case |
| **CASE-022** | `ROUTING` | Default route (`0.0.0.0/0`) missing on core router | `show ip route`, `show ip interface brief` | Gateway of last resort not configured | Lab Scenario / Responsible AI Case 5 |
| **CASE-023** | `WIRELESS` | SSID broadcast disabled & client missing manual profile | `show dot11 associations`, `show running-config` | Hidden SSID mismatch on wireless client | Lab Scenario / Dataset Case |
| **CASE-024** | `DNS` | DNS A record missing on internal DNS server | `nslookup server.internal.lab`, `show hosts` | Internal DNS zone record resolution failure | Lab Scenario / Dataset Case |
| **CASE-025** | `ACL` | ACL denying ICMP echo-request packets | `show access-lists`, `show ip interface` | ACL blocking ping while TCP traffic succeeds | Lab Scenario / Dataset Case |
| **CASE-026** | `STATIC_ROUTING` | Asymmetric return route missing on remote router | `show ip route`, `traceroute` | Return routing missing for client subnet | Lab Scenario / Dataset Case |
| **CASE-027** | `VLAN` | Voice VLAN and Data VLAN configured on same PVID | `show interfaces switchport`, `show vlan brief` | Auxiliary voice VLAN misconfiguration | Lab Scenario / Dataset Case |
| **CASE-028** | `NAT` | Static NAT 1:1 translation mapped to wrong internal IP | `show ip nat translations`, `show ip interface brief` | Static NAT inside local address mismatch | Lab Scenario / Dataset Case |
| **CASE-029** | `OSPF` | OSPF hello / dead timer interval mismatch | `show ip ospf interface`, `show ip ospf neighbor` | Timer mismatch preventing OSPF adjacency | Lab Scenario / Dataset Case |
| **CASE-030** | `WIRELESS` | Wireless channel interference / duplicate BSSID | `show dot11 frequency`, `show controllers` | Channel overlap / 2.4GHz RF interference | Lab Scenario / Dataset Case |
| **CASE-031** | `GATEWAY` | VRRP / HSRP virtual IP mismatch on backup router | `show standby brief`, `show vrrp` | HSRP/VRRP virtual gateway address misconfigured | Lab Scenario / Dataset Case |
| **CASE-032** | `SECURITY` | Port security violation err-disabled switchport | `show port-security interface`, `show interfaces status` | Port security MAC violation shut down port | Lab Scenario / Dataset Case |
| **CASE-033** | `DHCP` | DHCP Snooping untrusted port blocking DHCP replies | `show ip dhcp snooping`, `show ip dhcp snooping binding` | DHCP snooping blocking server offer packets | Lab Scenario / Dataset Case |
| **CASE-034** | `DNS` | Forward lookup zone forwarder unreachable | `show ip dns view`, `nslookup` | Upstream recursive DNS forwarder timeout | Lab Scenario / Dataset Case |
| **CASE-035** | `VLAN_TRUNK` | DTP negotiation mode mismatch (Dynamic Auto / Auto) | `show interfaces trunk`, `show interfaces switchport` | DTP auto-negotiation failure leaving port in access | Lab Scenario / Dataset Case |
