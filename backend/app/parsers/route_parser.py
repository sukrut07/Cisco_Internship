"""
NetSage AI — Route Parser.

Parses: show ip route
"""
from __future__ import annotations

import re
from typing import Optional


# Cisco route type codes
ROUTE_CODES = {
    "C": "connected",
    "S": "static",
    "R": "rip",
    "M": "mobile",
    "B": "bgp",
    "D": "eigrp",
    "EX": "eigrp_external",
    "O": "ospf",
    "IA": "ospf_inter_area",
    "N1": "ospf_nssa_external_type1",
    "N2": "ospf_nssa_external_type2",
    "E1": "ospf_external_type1",
    "E2": "ospf_external_type2",
    "i": "isis",
    "L1": "isis_level1",
    "L2": "isis_level2",
    "ia": "isis_inter_area",
    "*": "candidate_default",
    "U": "per_user_static",
    "o": "odr",
    "P": "periodic_downloaded_static",
    "H": "nhrp",
    "+": "replicated",
    "%": "next_hop_override",
    "L": "local",
}


def parse_ip_route(output: str) -> list[dict]:
    """
    Parse 'show ip route' output.

    Returns list of route records:
    [
      {
        "type": "static",
        "code": "S",
        "network": "192.168.30.0/24",
        "next_hop": "10.0.0.2",
        "interface": "GigabitEthernet0/0",
        "metric": None,
        "is_default": False
      }, ...
    ]
    """
    if not output or not output.strip():
        return []

    routes = []

    # Pattern for standard routes:
    # S    192.168.30.0/24 [1/0] via 10.0.0.2
    # O    10.10.10.0/24 [110/2] via 192.168.1.1, GigabitEthernet0/0
    # C    192.168.1.0/24 is directly connected, GigabitEthernet0/0
    # S*   0.0.0.0/0 [1/0] via 203.0.113.1

    route_pattern = re.compile(
        r"^\s*([A-Za-z*+%]+\*?)\s+([\d./]+)\s+"
        r"(?:\[(\d+)/(\d+)\]\s+via\s+([\d.]+)(?:,\s*(\d+)\s+\S+)?(?:,\s*(\S+))?|"
        r"is\s+directly\s+connected,\s*(\S+))",
        re.MULTILINE,
    )

    for match in route_pattern.finditer(output):
        code, network, admin_dist, metric, next_hop, age, via_iface, connected_iface = match.groups()
        code_clean = code.strip("*").strip()
        route_type = ROUTE_CODES.get(code_clean, "unknown")
        is_default = network == "0.0.0.0/0" or "*" in code

        routes.append(
            {
                "type": route_type,
                "code": code,
                "network": network,
                "next_hop": next_hop,
                "interface": connected_iface or via_iface,
                "admin_distance": int(admin_dist) if admin_dist else None,
                "metric": int(metric) if metric else None,
                "is_default": is_default,
            }
        )

    return routes


def find_route_for_network(
    destination: str, routes: list[dict]
) -> Optional[dict]:
    """
    Find the most specific route that covers a destination network/IP.

    Uses proper IP containment, not string matching.
    """
    import ipaddress

    try:
        dest_net = ipaddress.IPv4Network(destination, strict=False)
    except ValueError:
        return None

    best: Optional[dict] = None
    best_prefix = -1

    for route in routes:
        try:
            route_net = ipaddress.IPv4Network(route["network"], strict=False)
            # Check if destination is covered by this route
            if dest_net.subnet_of(route_net) or dest_net == route_net:
                if route_net.prefixlen > best_prefix:
                    best_prefix = route_net.prefixlen
                    best = route
        except (ValueError, TypeError):
            continue

    return best


def has_default_route(routes: list[dict]) -> bool:
    """Return True if a default route (0.0.0.0/0) exists."""
    return any(r.get("is_default") or r.get("network") == "0.0.0.0/0" for r in routes)
