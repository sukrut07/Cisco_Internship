"""
NetSage AI — VLAN Parser.

Parses: show vlan brief
"""
from __future__ import annotations

import re


def parse_vlan_brief(output: str) -> list[dict]:
    """
    Parse 'show vlan brief' output.

    Returns list of VLAN records:
    [{"vlan_id": "10", "name": "Sales", "status": "active", "ports": ["Fa0/1", "Fa0/2"]}]
    """
    if not output or not output.strip():
        return []

    vlans = []
    # Pattern: 10   Sales  active   Fa0/1, Fa0/2
    pattern = re.compile(
        r"^(\d+)\s+(\S+)\s+(active|act\/unsup|suspended|act\/lshut)\s*(.*?)$",
        re.MULTILINE | re.IGNORECASE,
    )

    for match in pattern.finditer(output):
        vlan_id, name, status, ports_str = match.groups()
        ports = [p.strip() for p in ports_str.split(",") if p.strip()]
        vlans.append(
            {
                "vlan_id": vlan_id,
                "name": name,
                "status": status.lower(),
                "ports": ports,
            }
        )

    return vlans


def vlan_exists(vlan_id: str | int, vlans: list[dict]) -> bool:
    """Return True if the given VLAN ID exists in the parsed VLAN list."""
    vlan_id_str = str(vlan_id)
    return any(v["vlan_id"] == vlan_id_str for v in vlans)


def get_vlan_ports(vlan_id: str | int, vlans: list[dict]) -> list[str]:
    """Return the ports assigned to a given VLAN."""
    vlan_id_str = str(vlan_id)
    for vlan in vlans:
        if vlan["vlan_id"] == vlan_id_str:
            return vlan["ports"]
    return []
