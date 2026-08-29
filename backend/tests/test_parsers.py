"""Tests for Cisco show command parsers."""
import pytest

from app.parsers.interface_parser import parse_ip_interface_brief, classify_interface_issue
from app.parsers.vlan_parser import parse_vlan_brief, vlan_exists
from app.parsers.route_parser import parse_ip_route, find_route_for_network, has_default_route
from app.parsers.trunk_parser import parse_interfaces_trunk, vlan_on_trunk
from app.parsers.acl_parser import parse_access_lists, has_deny_rules
from app.parsers.nat_parser import parse_nat_translations, parse_nat_statistics
from app.parsers.dhcp_parser import parse_dhcp_binding


# ---------------------------------------------------------------------------
# Interface Parser
# ---------------------------------------------------------------------------

INTERFACE_BRIEF = """\
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.1.1     YES manual up                    up
GigabitEthernet0/1    10.0.0.1        YES manual administratively down down
GigabitEthernet0/2    unassigned      YES unset  down                  down
"""


def test_interface_parser_counts():
    ifaces = parse_ip_interface_brief(INTERFACE_BRIEF)
    assert len(ifaces) >= 2  # at least GE0/0 and GE0/1 parsed


def test_interface_parser_fields():
    ifaces = parse_ip_interface_brief(INTERFACE_BRIEF)
    gi0 = next(i for i in ifaces if "GigabitEthernet0/0" in i["name"])
    assert gi0["ip_address"] == "192.168.1.1"
    assert gi0["status"] == "up"
    assert gi0["protocol"] == "up"


def test_interface_classify_admin_down():
    assert classify_interface_issue("administratively down", "down") == "admin_down"


def test_interface_classify_physical_down():
    assert classify_interface_issue("down", "down") == "physical_down"


def test_interface_classify_up_down():
    assert classify_interface_issue("up", "down") == "up_down"


def test_interface_classify_up_up():
    # Healthy interface returns None (no issue)
    assert classify_interface_issue("up", "up") is None


# ---------------------------------------------------------------------------
# VLAN Parser
# ---------------------------------------------------------------------------

VLAN_BRIEF = """\
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/5
10   Engineering                      active    Fa0/1, Fa0/2
20   Sales                            active    
1002 fddi-default                     act/unsup
"""


def test_vlan_parser_counts():
    vlans = parse_vlan_brief(VLAN_BRIEF)
    assert len(vlans) >= 2  # At least VLAN 1, 10, 20


def test_vlan_parser_fields():
    vlans = parse_vlan_brief(VLAN_BRIEF)
    vlan10 = next((v for v in vlans if v["vlan_id"] == "10"), None)
    assert vlan10 is not None
    assert vlan10["name"] == "Engineering"
    assert vlan10["status"] == "active"


def test_vlan_exists_true():
    vlans = parse_vlan_brief(VLAN_BRIEF)
    assert vlan_exists("10", vlans) is True


def test_vlan_exists_false():
    vlans = parse_vlan_brief(VLAN_BRIEF)
    assert vlan_exists("30", vlans) is False


# ---------------------------------------------------------------------------
# Route Parser
# ---------------------------------------------------------------------------

ROUTING_TABLE = """\
Codes: C - connected, S - static
Gateway of last resort is 203.0.113.1 to network 0.0.0.0
S*   0.0.0.0/0 [1/0] via 203.0.113.1
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
C    10.0.0.0/30 is directly connected, GigabitEthernet0/1
S    192.168.30.0/24 [1/0] via 10.0.0.2
"""


def test_route_parser_counts():
    routes = parse_ip_route(ROUTING_TABLE)
    assert len(routes) >= 3


def test_has_default_route():
    routes = parse_ip_route(ROUTING_TABLE)
    assert has_default_route(routes) is True


def test_no_default_route():
    partial = "C    192.168.1.0/24 is directly connected, GigabitEthernet0/0"
    routes = parse_ip_route(partial)
    assert has_default_route(routes) is False


def test_find_route_exact():
    routes = parse_ip_route(ROUTING_TABLE)
    result = find_route_for_network("192.168.30.0/24", routes)
    assert result is not None


def test_find_route_with_default():
    routes = parse_ip_route(ROUTING_TABLE)
    result = find_route_for_network("8.8.8.8", routes)
    assert result is not None  # Should match default route


def test_find_route_missing():
    partial = "C    192.168.1.0/24 is directly connected, GigabitEthernet0/0"
    routes = parse_ip_route(partial)
    result = find_route_for_network("10.99.99.0/24", routes)
    assert result is None


# ---------------------------------------------------------------------------
# Trunk Parser
# ---------------------------------------------------------------------------

TRUNK_OUTPUT = """\
Port        Mode         Encapsulation  Status        Native vlan
Gi0/1       on           802.1q         trunking      1

Port        Vlans allowed on trunk
Gi0/1       1-4094

Port        Vlans allowed and active in management domain
Gi0/1       1,10,20,30

Port        Vlans in spanning tree forwarding state and not pruned
Gi0/1       1,10,20,30
"""


def test_trunk_parser():
    trunks = parse_interfaces_trunk(TRUNK_OUTPUT)
    assert len(trunks) == 1
    assert trunks[0]["interface"] == "Gi0/1"
    assert trunks[0]["status"] == "trunking"


def test_vlan_on_trunk_true():
    trunks = parse_interfaces_trunk(TRUNK_OUTPUT)
    assert vlan_on_trunk("10", trunks) is True


def test_vlan_on_trunk_false():
    trunks = parse_interfaces_trunk(TRUNK_OUTPUT)
    assert vlan_on_trunk("99", trunks) is False


# ---------------------------------------------------------------------------
# ACL Parser
# ---------------------------------------------------------------------------

ACL_OUTPUT = """\
Extended IP access list 101
    10 deny ip 192.168.10.0 0.0.0.255 192.168.30.0 0.0.0.255 (127 matches)
    20 permit ip any any (45 matches)
"""


def test_acl_parser():
    acls = parse_access_lists(ACL_OUTPUT)
    assert len(acls) == 1
    assert acls[0]["acl_name"] == "101"


def test_acl_has_deny_with_matches():
    acls = parse_access_lists(ACL_OUTPUT)
    deny_entries = [
        e for acl in acls for e in acl["entries"]
        if e["action"] == "deny" and e["matches"] > 0
    ]
    assert len(deny_entries) == 1


def test_acl_has_deny_rules():
    acls = parse_access_lists(ACL_OUTPUT)
    assert has_deny_rules(acls) is True


# ---------------------------------------------------------------------------
# NAT Parser
# ---------------------------------------------------------------------------

NAT_TRANS = """\
Pro Inside global       Inside local        Outside local       Outside global
tcp 203.0.113.2:1025    192.168.1.10:1025   8.8.8.8:80          8.8.8.8:80
--- 203.0.113.2         192.168.1.20        ---                 ---
"""

NAT_STATS = """\
Total active translations: 2 (0 static, 2 dynamic; 2 extended)
Outside interfaces:
  GigabitEthernet0/1
Inside interfaces:
  GigabitEthernet0/0
Hits: 150  Misses: 3
"""


def test_nat_translations_parsed():
    trans = parse_nat_translations(NAT_TRANS)
    assert len(trans) >= 1


def test_nat_statistics_parsed():
    stats = parse_nat_statistics(NAT_STATS)
    assert stats["hits"] == 150
    assert stats["misses"] == 3


# ---------------------------------------------------------------------------
# DHCP Parser
# ---------------------------------------------------------------------------

DHCP_BINDING = """\
IP address       Client-ID/         Lease expiration        Type
                 Hardware address
192.168.1.10     0100.AABB.CC01     Sep 01 2025 08:00 AM    Automatic
192.168.1.11     0100.AABB.CC02     Sep 01 2025 08:00 AM    Automatic
"""


def test_dhcp_bindings_parsed():
    bindings = parse_dhcp_binding(DHCP_BINDING)
    assert len(bindings) == 2


def test_dhcp_binding_fields():
    bindings = parse_dhcp_binding(DHCP_BINDING)
    assert bindings[0]["ip"] == "192.168.1.10"
