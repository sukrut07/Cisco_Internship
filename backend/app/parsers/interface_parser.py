"""
NetSage AI — Interface Parser.

Parses: show ip interface brief, show interfaces
"""
from __future__ import annotations

import re
from typing import Optional


def parse_ip_interface_brief(output: str) -> list[dict]:
    """
    Parse 'show ip interface brief' output.

    Returns a list of interface records:
    [
      {
        "name": "GigabitEthernet0/0",
        "ip_address": "192.168.1.1",
        "method": "manual",
        "status": "up",
        "protocol": "up"
      }, ...
    ]
    """
    if not output or not output.strip():
        return []

    interfaces = []
    # Skip header line(s)
    # Format: Interface  IP-Address  OK?  Method  Status  Protocol
    pattern = re.compile(
        r"^(\S+)\s+([\d.]+|unassigned)\s+(\S+)\s+(\S+)\s+([\w\s]+?)\s+([\w\s]+?)\s*$",
        re.MULTILINE,
    )

    for match in pattern.finditer(output):
        name, ip, ok, method, status, protocol = match.groups()
        interfaces.append(
            {
                "name": name,
                "ip_address": ip if ip != "unassigned" else None,
                "ok": ok,
                "method": method,
                "status": status.strip().lower(),
                "protocol": protocol.strip().lower(),
            }
        )

    return interfaces


def parse_show_interfaces(output: str) -> list[dict]:
    """
    Parse 'show interfaces' output (simplified).

    Returns basic status info per interface.
    """
    if not output or not output.strip():
        return []

    interfaces = []
    # Match lines like: GigabitEthernet0/0 is up, line protocol is up
    header_pattern = re.compile(
        r"^(\S+)\s+is\s+(administratively\s+down|up|down)[,\s]*"
        r"line\s+protocol\s+is\s+(up|down)",
        re.MULTILINE | re.IGNORECASE,
    )

    for match in header_pattern.finditer(output):
        name, status, protocol = match.groups()
        interfaces.append(
            {
                "name": name,
                "status": status.strip().lower(),
                "protocol": protocol.strip().lower(),
                "administratively_down": "administratively" in status.lower(),
            }
        )

    return interfaces


def classify_interface_issue(status: str, protocol: str) -> Optional[str]:
    """
    Classify the interface condition.

    Returns:
        None — interface is healthy
        'admin_down' — administratively shut down
        'physical_down' — physical link failure
        'up_down' — Layer 1 ok, Layer 2 issue
    """
    s = status.lower()
    p = protocol.lower()

    if "administratively" in s:
        return "admin_down"
    if s == "down" and p == "down":
        return "physical_down"
    if s == "up" and p == "down":
        return "up_down"
    return None
