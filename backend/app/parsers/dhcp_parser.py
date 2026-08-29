"""
NetSage AI — DHCP Parser.

Parses: show ip dhcp binding, show ip dhcp pool
"""
from __future__ import annotations

import re


def parse_dhcp_binding(output: str) -> list[dict]:
    """
    Parse 'show ip dhcp binding' output.

    Returns list of DHCP binding records:
    [{"ip": "192.168.1.100", "mac": "0100.1234.5678", "lease_expiry": "...", "type": "automatic"}]
    """
    if not output or not output.strip():
        return []

    bindings = []
    # Format: IP address      Client-ID/         Lease expiration        Type
    #         192.168.1.100   0100.1234.5678      Sep 01 2025 12:00 AM    Automatic
    pattern = re.compile(
        r"^([\d.]+)\s+(\S+)\s+([\w\s:]+?)\s+(Automatic|Manual|Automatic:)\s*$",
        re.MULTILINE | re.IGNORECASE,
    )

    for match in pattern.finditer(output):
        ip, mac, expiry, binding_type = match.groups()
        bindings.append(
            {
                "ip": ip,
                "mac": mac,
                "lease_expiry": expiry.strip(),
                "type": binding_type.lower().rstrip(":"),
            }
        )

    return bindings


def parse_dhcp_pool(output: str) -> list[dict]:
    """
    Parse 'show ip dhcp pool' output.

    Returns basic pool information.
    """
    if not output or not output.strip():
        return []

    pools = []
    pool_pattern = re.compile(r"Pool\s+(\S+)\s+:", re.IGNORECASE)
    network_pattern = re.compile(r"Network\s+:\s+([\d./]+)", re.IGNORECASE)

    current_pool: dict | None = None
    for line in output.split("\n"):
        pool_match = pool_pattern.search(line)
        if pool_match:
            current_pool = {"name": pool_match.group(1), "network": None}
            pools.append(current_pool)
            continue

        if current_pool:
            net_match = network_pattern.search(line)
            if net_match:
                current_pool["network"] = net_match.group(1)

    return pools
