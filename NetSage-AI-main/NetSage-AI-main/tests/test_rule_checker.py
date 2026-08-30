import pytest
from backend.rule_checker.checker import DeterministicRuleChecker

def test_interface_down_detection():
    checker = DeterministicRuleChecker()
    show_output = """
    GigabitEthernet0/0/0     192.168.15.1    YES manual administratively down   down
    """
    results = checker.analyze(show_outputs=show_output)
    failed = [r for r in results if r["status"] == "failed"]
    assert len(failed) >= 1
    assert any(r["rule"] == "interface_down" for r in failed)


def test_gateway_mismatch_detection():
    checker = DeterministicRuleChecker()
    show_output = "IP Address: 192.168.1.50\nSubnet Mask: 255.255.255.0\nDefault Gateway: 192.168.2.1"
    results = checker.analyze(
        show_outputs=show_output,
        source_ip="192.168.1.50",
        subnet_mask="255.255.255.0",
        gateway="192.168.2.1"
    )
    failed = [r for r in results if r["status"] == "failed"]
    assert any(r["rule"] == "gateway_mismatch" for r in failed)


def test_duplicate_ip_detection():
    checker = DeterministicRuleChecker()
    show_output = "%IP-4-DUPADDR: Duplicate address 192.168.5.10 on FastEthernet0/10"
    results = checker.analyze(show_outputs=show_output)
    failed = [r for r in results if r["status"] == "failed"]
    assert any(r["rule"] == "duplicate_ip" for r in failed)


def test_missing_vlan_detection():
    checker = DeterministicRuleChecker()
    show_output = "Access Mode VLAN: 30 (inactive)"
    results = checker.analyze(show_outputs=show_output)
    failed = [r for r in results if r["status"] == "failed"]
    assert any(r["rule"] == "missing_vlan" for r in failed)


def test_missing_route_detection():
    checker = DeterministicRuleChecker()
    show_output = "Gateway of last resort is not set"
    results = checker.analyze(show_outputs=show_output)
    failed = [r for r in results if r["status"] == "failed"]
    assert any(r["rule"] == "missing_route" for r in failed)


def test_authentication_failure_detection():
    checker = DeterministicRuleChecker()
    show_output = "Shared Secret (Mismatch detected on WLC log: Shared Secret Incorrect)"
    symptom = "Laptop fails authentication when joining SSID 'Corp-Secure'. Status stays on 'Authenticating...'"
    results = checker.analyze(show_outputs=show_output, symptom=symptom)
    failed = [r for r in results if r["status"] == "failed"]
    assert any(r["rule"] == "authentication_failure" for r in failed)

