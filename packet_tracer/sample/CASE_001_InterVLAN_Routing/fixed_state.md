# Fixed State Specification — CASE-001: Inter-VLAN Routing

## 1. Remediation Strategy

The engineer stages and applies the following Cisco IOS command on Router `R1`:
```cisco
R1# configure terminal
R1(config)# interface GigabitEthernet0/1
R1(config-if)# no shutdown
R1(config-if)# end
```

---

## 2. Post-Fix Verification

### A. Interface Verification (`show ip interface brief` on R1)
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    unassigned      YES unset  up                    up
GigabitEthernet0/0.10 192.168.10.1    YES manual up                    up
GigabitEthernet0/0.20 192.168.20.1    YES manual up                    up
GigabitEthernet0/1    192.168.30.1    YES manual up                    up
```

### B. Routing Table Verification (`show ip route` on R1)
```
Gateway of last resort is not set

C    192.168.10.0/24 is directly connected, GigabitEthernet0/0.10
L    192.168.10.1/32 is directly connected, GigabitEthernet0/0.10
C    192.168.20.0/24 is directly connected, GigabitEthernet0/0.20
L    192.168.20.1/32 is directly connected, GigabitEthernet0/0.20
C    192.168.30.0/24 is directly connected, GigabitEthernet0/1
L    192.168.30.1/32 is directly connected, GigabitEthernet0/1
```

### C. End-to-End ICMP Ping Verification
From `PC-1` command prompt:
```
C:\> ping 192.168.30.10

Pinging 192.168.30.10 with 32 bytes of data:
Reply from 192.168.30.10: bytes=32 time<1ms TTL=127
Reply from 192.168.30.10: bytes=32 time<1ms TTL=127
Reply from 192.168.30.10: bytes=32 time<1ms TTL=127
Reply from 192.168.30.10: bytes=32 time<1ms TTL=127

Ping statistics for 192.168.30.10:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```
