"""Tests for the Rule Engine and individual rules."""
import pytest

from app.rules.base import RuleCheckResult
from app.rules.duplicate_ip import DuplicateIPRule
from app.rules.gateway import GatewayRule
from app.rules.subnet_mask import SubnetMaskRule
from app.rules.interface_status import InterfaceStatusRule
from app.rules.vlan import VLANRule
from app.rules.routes import RouteRule
from app.rules.dhcp import DHCPRule
from app.rules.dns import DNSRule
from app.rules.nat import NATRule
from app.rules.engine import RuleEngine


# ---------------------------------------------------------------------------
# Duplicate IP Rule
# ---------------------------------------------------------------------------

def test_duplicate_ip_detected():
    rule = DuplicateIPRule()
    ctx = {"devices": [
        {"name": "PC1", "ip": "192.168.1.10"},
        {"name": "PC2", "ip": "192.168.1.10"},
    ]}
    result = rule.check(ctx)
    assert result.status == "FAIL"
    assert "192.168.1.10" in result.message or any("192.168.1.10" in e for e in result.evidence)


def test_duplicate_ip_no_duplicates():
    rule = DuplicateIPRule()
    ctx = {"devices": [
        {"name": "PC1", "ip": "192.168.1.10"},
        {"name": "PC2", "ip": "192.168.1.20"},
    ]}
    result = rule.check(ctx)
    assert result.status == "PASS"


def test_duplicate_ip_no_devices():
    rule = DuplicateIPRule()
    result = rule.check({})
    assert result.status == "NOT_CHECKED"


# ---------------------------------------------------------------------------
# Subnet Mask Rule
# ---------------------------------------------------------------------------

def test_subnet_mask_valid():
    rule = SubnetMaskRule()
    ctx = {"devices": [
        {"name": "PC1", "ip": "192.168.1.10", "mask": "255.255.255.0", "expected_network": "192.168.1.0/24"},
    ]}
    result = rule.check(ctx)
    assert result.status == "PASS"


def test_subnet_mask_mismatch():
    rule = SubnetMaskRule()
    ctx = {"devices": [
        {"name": "PC1", "ip": "192.168.1.10", "mask": "255.255.255.128", "expected_network": "192.168.1.0/24"},
    ]}
    result = rule.check(ctx)
    assert result.status == "FAIL"


# ---------------------------------------------------------------------------
# Gateway Rule
# ---------------------------------------------------------------------------

def test_gateway_mismatch():
    rule = GatewayRule()
    ctx = {"devices": [
        {"name": "PC1", "ip": "192.168.10.20", "mask": "255.255.255.0", "gateway": "192.168.20.1"},
    ]}
    result = rule.check(ctx)
    assert result.status == "FAIL"
    assert "192.168.20.1" in " ".join(result.evidence)


def test_gateway_valid():
    rule = GatewayRule()
    ctx = {"devices": [
        {"name": "PC1", "ip": "192.168.1.10", "mask": "255.255.255.0", "gateway": "192.168.1.1"},
    ]}
    result = rule.check(ctx)
    assert result.status == "PASS"


def test_gateway_no_devices():
    rule = GatewayRule()
    result = rule.check({})
    assert result.status == "NOT_CHECKED"


# ---------------------------------------------------------------------------
# Interface Status Rule
# ---------------------------------------------------------------------------

SHOW_INTERFACES_BRIEF = """\
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.1.1     YES manual up                    up
GigabitEthernet0/1    10.0.0.1        YES manual administratively down down
GigabitEthernet0/2    unassigned      YES unset  down                  down
"""


def test_interface_admin_down():
    rule = InterfaceStatusRule()
    ctx = {"show_outputs": {"show ip interface brief": SHOW_INTERFACES_BRIEF}}
    result = rule.check(ctx)
    assert result.status == "FAIL"
    assert any("admin" in e.lower() or "administratively" in e.lower() for e in result.evidence)


def test_interface_all_up():
    rule = InterfaceStatusRule()
    ctx = {"show_outputs": {"show ip interface brief": (
        "Interface              IP-Address      OK? Method Status    Protocol\n"
        "GigabitEthernet0/0    192.168.1.1     YES manual up        up\n"
    )}}
    result = rule.check(ctx)
    assert result.status == "PASS"


def test_interface_no_data():
    rule = InterfaceStatusRule()
    result = rule.check({})
    assert result.status == "NOT_CHECKED"


# ---------------------------------------------------------------------------
# Route Rule
# ---------------------------------------------------------------------------

ROUTING_TABLE = """\
Codes: C - connected, S - static
Gateway of last resort is not set
C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
C    10.0.0.0/30 is directly connected, GigabitEthernet0/1
"""


def test_route_missing():
    rule = RouteRule()
    ctx = {
        "show_outputs": {"show ip route": ROUTING_TABLE},
        "destination_network": "192.168.30.0/24",
    }
    result = rule.check(ctx)
    assert result.status == "FAIL"
    assert "192.168.30.0" in result.message or any("192.168.30" in e for e in result.evidence)


def test_route_present_with_covering():
    """Default route should cover any destination."""
    rule = RouteRule()
    ctx = {
        "show_outputs": {"show ip route": (
            "S*   0.0.0.0/0 [1/0] via 203.0.113.1\n"
            "C    192.168.1.0/24 is directly connected, GigabitEthernet0/0\n"
        )},
        "destination_network": "8.8.8.8",
    }
    result = rule.check(ctx)
    assert result.status == "PASS"


# ---------------------------------------------------------------------------
# DHCP Rule
# ---------------------------------------------------------------------------

def test_dhcp_apipa_detected():
    rule = DHCPRule()
    ctx = {"devices": [{"name": "PC1", "ip": "169.254.45.32"}]}
    result = rule.check(ctx)
    assert result.status == "FAIL"
    assert "169.254" in " ".join(result.evidence)


def test_dhcp_no_apipa():
    rule = DHCPRule()
    ctx = {"devices": [{"name": "PC1", "ip": "192.168.1.10"}]}
    result = rule.check(ctx)
    assert result.status in ("PASS", "NOT_CHECKED")


# ---------------------------------------------------------------------------
# Rule Engine
# ---------------------------------------------------------------------------

def test_rule_engine_runs_all():
    engine = RuleEngine()
    ctx = {}
    results = engine.run_all(ctx)
    assert len(results) > 0
    assert all(isinstance(r, RuleCheckResult) for r in results)


def test_rule_engine_no_crash_on_bad_context():
    """Rule engine should never crash — errors become NOT_CHECKED."""
    engine = RuleEngine()
    results = engine.run_all({"show_outputs": None, "devices": None})
    assert all(r.status in ("PASS", "FAIL", "WARNING", "NOT_CHECKED") for r in results)


def test_rule_engine_summary():
    engine = RuleEngine()
    results = engine.run_all({})
    summary = engine.summary(results)
    assert "total" in summary
    assert "fail" in summary


# ---------------------------------------------------------------------------
# Enhanced Rule Edge Cases
# ---------------------------------------------------------------------------

def test_dns_nslookup_timeout_detected():
    rule = DNSRule()
    ctx = {
        "show_outputs": {
            "nslookup": "Server: 192.168.1.50\n*** Request to 192.168.1.50 timed-out"
        }
    }
    result = rule.check(ctx)
    assert result.status == "FAIL"
    assert "timed out" in result.message.lower()


def test_dhcp_pool_exhaustion_detected():
    rule = DHCPRule()
    ctx = {
        "show_outputs": {
            "show ip dhcp pool": "Pool LAN-POOL : \n Utilization mark (high/low)    : 100 / 0 \n Total addresses                : 254\n Leased addresses               : 254\n Free addresses                 : 0"
        }
    }
    result = rule.check(ctx)
    assert result.status == "FAIL"
    assert "exhausted" in result.message.lower()


def test_dhcp_relay_missing_detected():
    rule = DHCPRule()
    ctx = {
        "symptom": "PC in remote branch cannot obtain IP from central DHCP server across router relay",
        "show_outputs": {
            "show running-config": "interface GigabitEthernet0/0\n ip address 192.168.10.1 255.255.255.0\n no shutdown"
        }
    }
    result = rule.check(ctx)
    assert result.status == "FAIL"
    assert "helper-address" in " ".join(result.evidence)


def test_nat_missing_inside_outside_detected():
    rule = NATRule()
    ctx = {
        "symptom": "Internal hosts cannot access the public internet via NAT overload",
        "show_outputs": {
            "show running-config": "interface Gi0/0\n ip address 192.168.1.1 255.255.255.0\ninterface Gi0/1\n ip address 203.0.113.1 255.255.255.0"
        }
    }
    result = rule.check(ctx)
    assert result.status == "FAIL"
    assert "nat inside" in " ".join(result.evidence).lower() or "nat outside" in " ".join(result.evidence).lower()


def test_vlan_native_mismatch_detected():
    rule = VLANRule()
    ctx = {
        "show_outputs": {
            "show interfaces trunk": "%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on GigabitEthernet0/1 (1), with Switch GigabitEthernet0/1 (99)."
        }
    }
    result = rule.check(ctx)
    assert result.status == "FAIL"
    assert "native vlan mismatch" in result.message.lower()


def test_route_auto_extraction_from_symptom():
    rule = RouteRule()
    ctx = {
        "symptom": "Workstation cannot reach destination server at 10.200.5.10. Default gateway is reachable.",
        "show_outputs": {
            "show ip route": "Codes: C - connected\nC 192.168.1.0/24 is directly connected, Gi0/0"
        }
    }
    result = rule.check(ctx)
    assert result.status == "FAIL"
    assert "10.200.5.10" in result.message
