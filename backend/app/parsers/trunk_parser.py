"""
NetSage AI — Trunk Parser.

Parses: show interfaces trunk
"""
from __future__ import annotations

import re


def parse_interfaces_trunk(output: str) -> list[dict]:
    """
    Parse 'show interfaces trunk' output.

    Returns list of trunk records:
    [
      {
        "interface": "GigabitEthernet0/1",
        "mode": "on",
        "encapsulation": "802.1q",
        "status": "trunking",
        "native_vlan": "1",
        "vlans_allowed": "1-4094",
        "vlans_active": "10,20,30",
        "vlans_forwarding": "10,20,30"
      }, ...
    ]
    """
    if not output or not output.strip():
        return []

    trunks: list[dict] = []

    # Section patterns
    port_section_pattern = re.compile(
        r"Port\s+Mode\s+Encapsulation\s+Status\s+Native\s+vlan",
        re.IGNORECASE,
    )
    vlans_allowed_pattern = re.compile(r"VLANs\s+allowed\s+on\s+trunk", re.IGNORECASE)
    vlans_active_pattern = re.compile(r"VLANs\s+allowed\s+and\s+active\s+in\s+management", re.IGNORECASE)
    vlans_forwarding_pattern = re.compile(r"VLANs\s+in\s+spanning\s+tree\s+forwarding", re.IGNORECASE)

    trunk_line = re.compile(
        r"^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)\s*$",
        re.MULTILINE,
    )
    vlan_line = re.compile(r"^(\S+)\s+([\d,\-none]+)\s*$", re.MULTILINE)

    lines = output.split("\n")
    section = "port"
    interface_map: dict[str, dict] = {}

    for line in lines:
        if port_section_pattern.search(line):
            section = "port"
            continue
        elif vlans_allowed_pattern.search(line):
            section = "vlans_allowed"
            continue
        elif vlans_active_pattern.search(line):
            section = "vlans_active"
            continue
        elif vlans_forwarding_pattern.search(line):
            section = "vlans_forwarding"
            continue

        if section == "port":
            m = trunk_line.match(line)
            if m:
                iface, mode, encap, status, native = m.groups()
                interface_map[iface] = {
                    "interface": iface,
                    "mode": mode,
                    "encapsulation": encap,
                    "status": status,
                    "native_vlan": native,
                    "vlans_allowed": "",
                    "vlans_active": "",
                    "vlans_forwarding": "",
                }
        elif section in ("vlans_allowed", "vlans_active", "vlans_forwarding"):
            m = vlan_line.match(line)
            if m:
                iface, vlans = m.groups()
                if iface in interface_map:
                    interface_map[iface][section] = vlans

    trunks = list(interface_map.values())
    return trunks


def vlan_on_trunk(vlan_id: str | int, trunk_records: list[dict]) -> bool:
    """Return True if a VLAN is present in the active VLANs of any trunk."""
    vlan_str = str(vlan_id)
    for trunk in trunk_records:
        active = trunk.get("vlans_active", "")
        if vlan_str in active.split(","):
            return True
    return False
