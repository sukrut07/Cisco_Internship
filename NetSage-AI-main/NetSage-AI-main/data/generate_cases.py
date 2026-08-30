import csv
import os

cases_data = [
    {
        "case_id": "CASE-101",
        "title": "PC cannot access server in VLAN 30",
        "symptom": "PC-1 in VLAN 10 cannot ping Server-1 in VLAN 30. Switch logs indicate VLAN 30 does not exist on Access Switch 2.",
        "topology": "PC-1 (192.168.10.10) -> Switch-1 -> Switch-2 -> Server-1 (192.168.30.50)",
        "show_outputs": "=== Switch-2 show vlan brief ===\nVLAN Name                             Status    Ports\n---- -------------------------------- --------- -------------------------------\n1    default                          active    Fa0/1, Fa0/2, Fa0/3, Fa0/4\n10   Engineering                      active    Fa0/5, Fa0/6\n20   Sales                            active    Fa0/7, Fa0/8\n\n=== Switch-2 show interfaces Fa0/10 switchport ===\nName: Fa0/10\nMode: access\nAccess Mode VLAN: 30 (inactive)",
        "expected_fault": "VLAN 30 is missing from Switch-2 VLAN database causing access port Fa0/10 to be inactive.",
        "osi_layer": "Layer 2 (Data Link)",
        "concept": "VLAN",
        "severity": "High"
    },
    {
        "case_id": "CASE-102",
        "title": "PC1 has wrong default gateway configured",
        "symptom": "Host PC1 (192.168.1.50) cannot reach external destination 8.8.8.8 or router subinterface.",
        "topology": "PC1 (192.168.1.50/24) -> Switch -> Router Fa0/0.1 (192.168.1.1/24)",
        "show_outputs": "=== PC1 IP Configuration ===\nIP Address: 192.168.1.50\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.2.1\n\n=== Router Fa0/0.1 show ip interface brief ===\nFa0/0.1            192.168.1.1     YES manual up                    up",
        "expected_fault": "Default Gateway 192.168.2.1 on PC1 is on a different IP subnet than its IP address 192.168.1.50/24.",
        "osi_layer": "Layer 3 (Network)",
        "concept": "Gateway",
        "severity": "High"
    },
    {
        "case_id": "CASE-103",
        "title": "DHCP clients fail to acquire IP address on remote VLAN",
        "symptom": "PC in VLAN 20 receives APIPA address (169.254.x.x). DHCP Server is located in VLAN 10 on Router-1.",
        "topology": "PC (VLAN 20) -> Switch -> Router-1 Fa0/0.20 (192.168.20.1) -> Router-1 Fa0/0.10 (DHCP Server)",
        "show_outputs": "=== Router-1 show running-config interface Fa0/0.20 ===\ninterface FastEthernet0/0.20\n encapsulation dot1Q 20\n ip address 192.168.20.1 255.255.255.0\n!\n=== Router-1 show ip dhcp binding ===\n(No bindings for 192.168.20.0 pool)",
        "expected_fault": "ip helper-address is missing on Router subinterface Fa0/0.20 to relay DHCP requests to DHCP server.",
        "osi_layer": "Layer 3 (Network)",
        "concept": "DHCP",
        "severity": "Critical"
    },
    {
        "case_id": "CASE-104",
        "title": "Host cannot resolve internal domain name web.corp.local",
        "symptom": "PC can ping server by IP address 10.0.0.50 but HTTP requests to web.corp.local fail with host unknown.",
        "topology": "PC1 -> Switch -> Router -> DNS Server (10.0.0.53)",
        "show_outputs": "=== PC1 IP Config ===\nIP Address: 10.0.10.15\nSubnet Mask: 255.255.255.0\nDefault Gateway: 10.0.10.1\nDNS Server: 10.0.0.55\n\n=== Router show ip route 10.0.0.55 ===\nRouting table entry for 10.0.0.55/32 not found.",
        "expected_fault": "DNS Server IP on PC1 is set to 10.0.0.55, which is invalid/unreachable. Actual DNS Server IP is 10.0.0.53.",
        "osi_layer": "Layer 7 (Application)",
        "concept": "DNS",
        "severity": "Medium"
    },
    {
        "case_id": "CASE-105",
        "title": "Branch Router cannot reach HQ Network via Static Route",
        "symptom": "Branch-R1 cannot forward traffic to HQ LAN 10.100.0.0/16. Traffic dropped at Branch-R1.",
        "topology": "Branch-R1 (Se0/0/0) <---> (Se0/0/0) HQ-R1 -> HQ LAN",
        "show_outputs": "=== Branch-R1 show ip route ===\nCodes: C - connected, S - static\nGateway of last resort is not set\n192.168.12.0/30 is subnetted, 1 subnets\nC    192.168.12.0 is directly connected, Serial0/0/0\n\n=== Branch-R1 show running-config | inc ip route ===\nip route 10.100.0.0 255.255.0.0 192.168.12.6",
        "expected_fault": "Static route next-hop IP 192.168.12.6 is wrong. Serial interface IP is 192.168.12.2.",
        "osi_layer": "Layer 3 (Network)",
        "concept": "Routing",
        "severity": "High"
    },
    {
        "case_id": "CASE-106",
        "title": "ACL blocking Web traffic to DMZ Web Server",
        "symptom": "Clients can ping DMZ Server 172.16.1.100 but TCP port 80 / 443 web connections timeout.",
        "topology": "Client -> Router Gi0/0/0 (Inbound ACL) -> DMZ Web Server (172.16.1.100)",
        "show_outputs": "=== Router show access-lists ===\nExtended IP access list 101_DMZ_FILTER\n    10 deny ip any host 172.16.1.100 (482 matches)\n    20 permit tcp any host 172.16.1.100 eq www\n    30 permit ip any any",
        "expected_fault": "ACL rule 10 explicitly denies all IP traffic to host 172.16.1.100 before rule 20 permits TCP port 80.",
        "osi_layer": "Layer 4 (Transport)",
        "concept": "ACL",
        "severity": "High"
    },
    {
        "case_id": "CASE-107",
        "title": "NAT overload fails for Internal LAN clients",
        "symptom": "Internal LAN hosts (192.168.1.0/24) cannot reach internet IP addresses. Pings timeout at Router WAN interface.",
        "topology": "LAN Hosts -> Router Gi0/0/0 (Inside) -> Router Gi0/0/1 (Outside) -> ISP Router",
        "show_outputs": "=== Router show ip nat statistics ===\nTotal active translations: 0\nOutside interfaces: GigabitEthernet0/0/1\nInside interfaces: (none)\n\n=== Router show ip interface brief ===\nGigabitEthernet0/0/0     192.168.1.1     YES manual up                    up\nGigabitEthernet0/0/1     203.0.113.2     YES manual up                    up",
        "expected_fault": "Interface GigabitEthernet0/0/0 is missing the command 'ip nat inside'.",
        "osi_layer": "Layer 3 (Network)",
        "concept": "NAT",
        "severity": "Critical"
    },
    {
        "case_id": "CASE-108",
        "title": "Wireless Laptop cannot connect to WPA2 Enterprise SSID",
        "symptom": "Laptop fails authentication when joining SSID 'Corp-Secure'. Status stays on 'Authenticating...'",
        "topology": "Wireless Laptop -> Lightweight AP -> WLC 3504 -> RADIUS Server (10.0.0.254)",
        "show_outputs": "=== WLC show radius summary ===\nServer Index..................................... 1\nServer Address................................... 10.0.0.254\nShared Secret.................................... ******** (Mismatch detected on WLC log: Shared Secret Incorrect)\nPort Number...................................... 1812",
        "expected_fault": "RADIUS shared secret mismatch between Wireless LAN Controller (WLC) and RADIUS server.",
        "osi_layer": "Layer 7 (Application)",
        "concept": "Wireless",
        "severity": "High"
    },
    {
        "case_id": "CASE-109",
        "title": "Trunk Link Native VLAN Mismatch causes CDP Error",
        "symptom": "Traffic between Switch-1 and Switch-2 suffers packet loss. Syslog logs '%CDP-4-NATIVE_VLAN_MISMATCH'.",
        "topology": "Switch-1 (Gi0/1) <---> (Gi0/1) Switch-2",
        "show_outputs": "=== Switch-1 show interfaces trunk ===\nPort        Mode         Encapsulation  Status        Native vlan\nGi0/1       on           802.1q         trunking      1\n\n=== Switch-2 show interfaces trunk ===\nPort        Mode         Encapsulation  Status        Native vlan\nGi0/1       on           802.1q         trunking      99",
        "expected_fault": "Native VLAN mismatch: Switch-1 uses VLAN 1 while Switch-2 uses VLAN 99 on trunk link Gi0/1.",
        "osi_layer": "Layer 2 (Data Link)",
        "concept": "VLAN",
        "severity": "Medium"
    },
    {
        "case_id": "CASE-110",
        "title": "Duplicate IP address configured on Server and Printer",
        "symptom": "Intermittent network connectivity to Finance Server at 192.168.5.10. ARP table flips between MAC addresses.",
        "topology": "Switch-1 -> Server-A (192.168.5.10) & Printer-B (192.168.5.10)",
        "show_outputs": "=== Switch-1 show mac address-table | inc 192.168.5.10 ===\nVlan    Mac Address       Type        Ports\n---    -----------       --------    -----\n 5     0050.56a1.b2c3    DYNAMIC     Fa0/10\n 5     0011.2233.4455    DYNAMIC     Fa0/18\n\n=== Syslog Log ===\n%IP-4-DUPADDR: Duplicate address 192.168.5.10 on FastEthernet0/10, sourced by 0011.2233.4455",
        "expected_fault": "Duplicate IP 192.168.5.10 assigned to both Finance Server (Fa0/10) and Printer (Fa0/18).",
        "osi_layer": "Layer 3 (Network)",
        "concept": "Gateway",
        "severity": "High"
    },
    {
        "case_id": "CASE-111",
        "title": "Router Subinterface Shut Down",
        "symptom": "All hosts in VLAN 15 cannot reach their default gateway or any external subnets.",
        "topology": "VLAN 15 Hosts -> Switch Trunk -> Router Gi0/0/0.15",
        "show_outputs": "=== Router show ip interface brief ===\nInterface                  IP-Address      OK? Method Status                  Protocol\nGi0/0/0                    unassigned      YES unset  up                      up\nGi0/0/0.15                 192.168.15.1    YES manual administratively down   down",
        "expected_fault": "Router subinterface GigabitEthernet0/0/0.15 is administratively down.",
        "osi_layer": "Layer 1 (Physical)",
        "concept": "Routing",
        "severity": "Critical"
    },
    {
        "case_id": "CASE-112",
        "title": "OSPF Adjacency fails due to Hello Interval mismatch",
        "symptom": "R1 and R2 fail to establish OSPF neighbor state. Neighbor status stuck in Down or Init.",
        "topology": "R1 Gi0/0/0 (10.0.0.1/30) <---> Gi0/0/0 R2 (10.0.0.2/30)",
        "show_outputs": "=== R1 show ip ospf interface Gi0/0/0 ===\nGi0/0/0 is up, line protocol is up\n  Process ID 1, Router ID 1.1.1.1, Network Type BROADCAST, Cost: 1\n  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5\n\n=== R2 show ip ospf interface Gi0/0/0 ===\nGi0/0/0 is up, line protocol is up\n  Process ID 1, Router ID 2.2.2.2, Network Type BROADCAST, Cost: 1\n  Timer intervals configured, Hello 30, Dead 120, Wait 120, Retransmit 5",
        "expected_fault": "OSPF Hello timer mismatch: R1 has Hello timer 10s while R2 has Hello timer 30s.",
        "osi_layer": "Layer 3 (Network)",
        "concept": "Routing",
        "severity": "High"
    },
    {
        "case_id": "CASE-113",
        "title": "Access Switchport configured in wrong VLAN",
        "symptom": "PC in HR department (intended VLAN 20) is getting IP address from Accounting VLAN 30 DHCP pool.",
        "topology": "HR PC -> Switch Fa0/12 -> Router (Router-on-a-stick)",
        "show_outputs": "=== Switch show interfaces Fa0/12 switchport ===\nName: Fa0/12\nOperational Mode: static access\nAccess Mode VLAN: 30 (Accounting)\nTrunking Native Mode VLAN: 1 (default)",
        "expected_fault": "Switchport Fa0/12 is assigned to VLAN 30 instead of intended HR VLAN 20.",
        "osi_layer": "Layer 2 (Data Link)",
        "concept": "VLAN",
        "severity": "Medium"
    },
    {
        "case_id": "CASE-114",
        "title": "DHCP Scope IP Pool Exhausted",
        "symptom": "New wireless clients connecting to guest Wi-Fi fail to receive IP configuration.",
        "topology": "Guest Laptops -> WLC -> DHCP Server Router",
        "show_outputs": "=== Router show ip dhcp pool Guest_Pool ===\nPool Guest_Pool :\n Utilization mark (red/blue)    : 100 / 0\n Subnet size (total/usable)    : 254 / 254\n Total addresses                : 254\n Leased addresses               : 254\n Pending addresses              : 0",
        "expected_fault": "DHCP address pool 'Guest_Pool' has reached 100% utilization with 0 available leases remaining.",
        "osi_layer": "Layer 3 (Network)",
        "concept": "DHCP",
        "severity": "High"
    },
    {
        "case_id": "CASE-115",
        "title": "Static NAT Mismatch for External Web Access",
        "symptom": "External internet users cannot open hosted website at public IP 203.0.113.50.",
        "topology": "Internet User -> Edge Router -> DMZ Web Server (192.168.100.50)",
        "show_outputs": "=== Edge Router show ip nat translations ===\nPro Inside global      Inside local       Outside local      Outside global\ntcp 203.0.113.50:80    192.168.100.55:80  ---                ---\n\n=== Server Config ===\nIP Address: 192.168.100.50",
        "expected_fault": "Static NAT translation rule points to wrong inside local IP address 192.168.100.55 instead of 192.168.100.50.",
        "osi_layer": "Layer 3 (Network)",
        "concept": "NAT",
        "severity": "High"
    },
    {
        "case_id": "CASE-116",
        "title": "Missing Encapsulation dot1Q on Router Subinterface",
        "symptom": "Router subinterface GigabitEthernet0/0/0.10 fails to process tagged VLAN 10 frames.",
        "topology": "Switch (Trunk) <---> Router Gi0/0/0.10",
        "show_outputs": "=== Router show running-config interface Gi0/0/0.10 ===\ninterface GigabitEthernet0/0/0.10\n ip address 10.10.10.1 255.255.255.0\n (Missing encapsulation dot1Q line)",
        "expected_fault": "Router subinterface Gi0/0/0.10 lacks the 'encapsulation dot1Q 10' command.",
        "osi_layer": "Layer 2 (Data Link)",
        "concept": "VLAN",
        "severity": "Critical"
    },
    {
        "case_id": "CASE-117",
        "title": "Inconsistent Subnet Mask on Router Interface",
        "symptom": "Hosts in subnet 10.20.0.0/24 can reach gateway 10.20.0.1, but hosts past 10.20.0.128 lose connection.",
        "topology": "Hosts (10.20.0.0/24 prefix) -> Router Gi0/1 (10.20.0.1)",
        "show_outputs": "=== Router show ip interface Gi0/1 ===\nGigabitEthernet0/1 is up, line protocol is up\n  Internet address is 10.20.0.1/25 (255.255.255.128)\n\n=== Host-130 Config ===\nIP: 10.20.0.130 Subnet: 255.255.255.0 Gateway: 10.20.0.1",
        "expected_fault": "Subnet mask mismatch: Router Gi0/1 is configured with /25 (255.255.255.128), treating 10.20.0.130 as out-of-subnet.",
        "osi_layer": "Layer 3 (Network)",
        "concept": "Gateway",
        "severity": "High"
    },
    {
        "case_id": "CASE-118",
        "title": "OSPF Passive Interface blocking adjacency",
        "symptom": "Router-A and Router-B connect over Gi0/0/1 but fail to form OSPF neighbor relationship.",
        "topology": "Router-A (Gi0/0/1) <---> Router-B (Gi0/0/1)",
        "show_outputs": "=== Router-A show running-config | section ospf ===\nrouter ospf 1\n router-id 1.1.1.1\n passive-interface default\n no passive-interface GigabitEthernet0/0/0\n network 10.0.0.0 0.255.255.255 area 0",
        "expected_fault": "Interface GigabitEthernet0/0/1 is suppressed by 'passive-interface default' and missing 'no passive-interface GigabitEthernet0/0/1'.",
        "osi_layer": "Layer 3 (Network)",
        "concept": "Routing",
        "severity": "High"
    },
    {
        "case_id": "CASE-119",
        "title": "ACL Inbound vs Outbound Direction Misconfiguration",
        "symptom": "ACL 110 intended to filter traffic from Remote Subnet fails to block packets.",
        "topology": "Remote Subnet -> Router Gi0/0/0 (Inbound) -> Router Gi0/0/1 (Outbound) -> Internal LAN",
        "show_outputs": "=== Router show ip interface Gi0/0/0 ===\nGigabitEthernet0/0/0 is up, line protocol is up\n  Inbound access list is not set\n  Outbound access list is 110\n\n=== Router show access-lists 110 ===\nExtended IP access list 110\n    10 deny ip 192.168.50.0 0.0.0.255 any",
        "expected_fault": "Access list 110 is applied outbound on Gi0/0/0 instead of inbound, causing traffic entering Gi0/0/0 to bypass filtering.",
        "osi_layer": "Layer 3 (Network)",
        "concept": "ACL",
        "severity": "High"
    },
    {
        "case_id": "CASE-120",
        "title": "Port Security Violation shutting down switchport",
        "symptom": "User plugged personal laptop into desk jack and port immediately went dark (err-disabled).",
        "topology": "Laptop -> Switch Fa0/5",
        "show_outputs": "=== Switch show interfaces Fa0/5 status ===\nPort      Name               Status       Vlan       Duplex  Speed Type\nFa0/5                        err-disabled 10         auto    auto  10/100BaseTX\n\n=== Switch show port-security interface Fa0/5 ===\nPort Security              : Enabled\nPort Status                : Secure-shutdown\nViolation Mode             : Shutdown\nSecure MAC Address Quant   : 1\nLast Source Address:Vlan   : a44e.31b2.99dd:10",
        "expected_fault": "Port security violation triggered on Fa0/5 due to unauthorized MAC address a44e.31b2.99dd.",
        "osi_layer": "Layer 2 (Data Link)",
        "concept": "VLAN",
        "severity": "Medium"
    },
    {
        "case_id": "CASE-121",
        "title": "Lightweight Access Point unable to join WLC",
        "symptom": "Access Point AP-1 LED blinks amber/red and status on WLC shows AP count 0.",
        "topology": "AP-1 -> PoE Switch -> Router -> WLC (10.10.10.100)",
        "show_outputs": "=== AP-1 Console Log ===\n%CAPWAP-3-ERRORLOG: Did not receive CAPWAP discovery response from WLC.\n%DHCP-6-ADDRESS_ASSIGNED: IP 192.168.99.15/24, Option 43: Not configured.",
        "expected_fault": "DHCP Option 43 is missing in the AP subnet DHCP pool, preventing the AP from discovering WLC IP 10.10.10.100.",
        "osi_layer": "Layer 7 (Application)",
        "concept": "Wireless",
        "severity": "High"
    },
    {
        "case_id": "CASE-122",
        "title": "Missing Default Route on ISP Gateway Router",
        "symptom": "Internal workstations can reach edge router WAN interface, but pings to public 8.8.8.8 fail with unreachable.",
        "topology": "LAN -> Edge Router (203.0.113.1) <---> ISP Router",
        "show_outputs": "=== Edge Router show ip route ===\nCodes: C - connected, S - static\nGateway of last resort is not set\n192.168.1.0/24 is sub-netted, 1 subnets\nC    192.168.1.0 is directly connected, GigabitEthernet0/0/0\n203.0.113.0/30 is sub-netted, 1 subnets\nC    203.0.113.0 is directly connected, GigabitEthernet0/0/1",
        "expected_fault": "Edge Router has no Gateway of Last Resort (default route 'ip route 0.0.0.0 0.0.0.0 GigabitEthernet0/0/1').",
        "osi_layer": "Layer 3 (Network)",
        "concept": "Routing",
        "severity": "Critical"
    },
    {
        "case_id": "CASE-123",
        "title": "Trunk Allowed VLAN list excluding Management VLAN 99",
        "symptom": "Network administrators cannot SSH to Switch-2 (10.99.0.2) from Core Switch.",
        "topology": "Core Switch (Gi0/1) <---> (Gi0/1) Switch-2",
        "show_outputs": "=== Core Switch show interfaces trunk ===\nPort        Mode         Encapsulation  Status        Native vlan\nGi0/1       on           802.1q         trunking      1\nPort        Vlans allowed on trunk\nGi0/1       10,20,30\n(VLAN 99 is missing from allowed list)",
        "expected_fault": "Management VLAN 99 is omitted from the 'switchport trunk allowed vlan' list on link Gi0/1.",
        "osi_layer": "Layer 2 (Data Link)",
        "concept": "VLAN",
        "severity": "Medium"
    },
    {
        "case_id": "CASE-124",
        "title": "ACL Wildcard Mask inverted error",
        "symptom": "ACL intended to permit subnet 172.16.10.0/24 permits only IP 172.16.10.0 and denies all hosts.",
        "topology": "Branch LAN -> Router Gi0/0/0 (Inbound ACL 10)",
        "show_outputs": "=== Router show access-lists 10 ===\nStandard IP access list 10\n    10 permit 172.16.10.0 255.255.255.0 (0 matches)\n(Note: Cisco IOS standard ACL expects wildcard mask 0.0.0.255, not subnet mask 255.255.255.0)",
        "expected_fault": "ACL rule 10 uses subnet mask 255.255.255.0 instead of wildcard mask 0.0.0.255.",
        "osi_layer": "Layer 3 (Network)",
        "concept": "ACL",
        "severity": "High"
    },
    {
        "case_id": "CASE-125",
        "title": "DNS Service Disabled on Packet Tracer Server",
        "symptom": "All host DNS queries to DNS Server 192.168.1.250 fail with ICMP Port Unreachable.",
        "topology": "Hosts -> Switch -> Server (192.168.1.250)",
        "show_outputs": "=== Server Services Status ===\nHTTP Service: ON\nDHCP Service: OFF\nDNS Service: OFF (Service state turned off in Packet Tracer Services tab)",
        "expected_fault": "DNS Service is disabled in server configuration settings.",
        "osi_layer": "Layer 7 (Application)",
        "concept": "DNS",
        "severity": "Medium"
    },
    {
        "case_id": "CASE-126",
        "title": "Duplex Mismatch causing heavy collisions and slow throughput",
        "symptom": "File transfers between Switch-A and Switch-B are extremely slow with high collision counts.",
        "topology": "Switch-A Fa0/24 <---> Fa0/24 Switch-B",
        "show_outputs": "=== Switch-A show interfaces Fa0/24 ===\nFa0/24 is up, line protocol is up\n  Full-duplex, 100Mb/s, media type is 100BaseTX\n\n=== Switch-B show interfaces Fa0/24 ===\nFa0/24 is up, line protocol is up\n  Half-duplex, 100Mb/s, media type is 100BaseTX\n  5429 late collisions, 12044 deferred",
        "expected_fault": "Duplex mismatch: Switch-A is set to Full-duplex while Switch-B is set to Half-duplex.",
        "osi_layer": "Layer 1 (Physical)",
        "concept": "VLAN",
        "severity": "Medium"
    },
    {
        "case_id": "CASE-127",
        "title": "NAT Pool address range outside WAN interface subnet",
        "symptom": "Overload NAT translates traffic to public pool 198.51.100.100-110, but ISP drops return packets.",
        "topology": "Router Gi0/0/1 (203.0.113.2/30) <---> ISP Router (203.0.113.1/30)",
        "show_outputs": "=== Router show ip nat pool MY_POOL ===\npool MY_POOL: netmask 255.255.255.0\n start 198.51.100.100 end 198.51.100.110\n\n=== ISP Router show ip route 198.51.100.0 ===\nRouting table entry for 198.51.100.0/24 not found.",
        "expected_fault": "NAT pool addresses (198.51.100.x) are not routed by the ISP to Edge Router WAN interface 203.0.113.2.",
        "osi_layer": "Layer 3 (Network)",
        "concept": "NAT",
        "severity": "High"
    },
    {
        "case_id": "CASE-128",
        "title": "Wireless Security Pre-Shared Key (PSK) Mismatch",
        "symptom": "Smartphone fails to connect to Wi-Fi SSID 'Home-WiFi'. Stays stuck on 'Connecting...'",
        "topology": "Smartphone -> Wireless Router (SSID: Home-WiFi)",
        "show_outputs": "=== Wireless Router Config ===\nSSID: Home-WiFi\nSecurity: WPA2-Personal\nPSK Passphrase: SecurePassword2026!\n\n=== Smartphone Wi-Fi Profile ===\nSSID: Home-WiFi\nSecurity: WPA2-Personal\nConfigured Passphrase: SecurePassword2026 (Missing exclamation mark)",
        "expected_fault": "WPA2 Pre-Shared Key mismatch on smartphone profile.",
        "osi_layer": "Layer 2 (Data Link)",
        "concept": "Wireless",
        "severity": "Low"
    },
    {
        "case_id": "CASE-129",
        "title": "DHCP Excluded Addresses Blocking Valid Host Range",
        "symptom": "DHCP Server assigns IPs starting from 192.168.1.200, leaving hosts unable to get early pool IPs.",
        "topology": "DHCP Server Router -> Switch -> Clients",
        "show_outputs": "=== Router show running-config | inc dhcp ===\nip dhcp excluded-address 192.168.1.1 192.168.1.199\nip dhcp pool LAN_POOL\n network 192.168.1.0 255.255.255.0\n default-router 192.168.1.1",
        "expected_fault": "DHCP excluded address range is overly broad (excluding .1 through .199), limiting pool to only 55 usable host addresses.",
        "osi_layer": "Layer 3 (Network)",
        "concept": "DHCP",
        "severity": "Low"
    },
    {
        "case_id": "CASE-130",
        "title": "Static Route Pointing to Wrong Exit Interface",
        "symptom": "Router-1 traffic destined for 10.50.0.0/16 is forwarded out Gi0/0/0 instead of Gi0/0/1.",
        "topology": "Router-1 (Gi0/0/0 to LAN, Gi0/0/1 to WAN) -> Router-2",
        "show_outputs": "=== Router-1 show ip route ===\nCodes: C - connected, S - static\nS    10.50.0.0/16 is directly connected, GigabitEthernet0/0/0\n\n=== Router-1 show interfaces brief ===\nGi0/0/0 is connected to LAN 192.168.1.0/24\nGi0/0/1 is connected to WAN 10.255.0.1/30",
        "expected_fault": "Static route for 10.50.0.0/16 configured with wrong exit interface GigabitEthernet0/0/0 instead of WAN interface GigabitEthernet0/0/1.",
        "osi_layer": "Layer 3 (Network)",
        "concept": "Routing",
        "severity": "High"
    }
]

def main():
    os.makedirs("data", exist_ok=True)
    csv_path = os.path.join("data", "cases.csv")
    fieldnames = [
        "case_id", "title", "symptom", "topology", "show_outputs",
        "expected_fault", "osi_layer", "concept", "severity"
    ]
    
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for case in cases_data:
            writer.writerow(case)
            
    print(f"Successfully generated {len(cases_data)} realistic Cisco troubleshooting cases in {csv_path}")

if __name__ == "__main__":
    main()
