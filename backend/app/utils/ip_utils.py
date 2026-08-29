"""
NetSage AI — IP Address Utilities.

Uses the Python standard library ipaddress module.
No shell execution; no external dependencies.
"""
from __future__ import annotations

import ipaddress
from typing import Optional


def is_valid_ip(ip: str) -> bool:
    """Return True if ip is a valid IPv4 address."""
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ValueError:
        return False


def is_valid_network(network: str) -> bool:
    """Return True if network is a valid IPv4 network (e.g., '192.168.1.0/24')."""
    try:
        ipaddress.IPv4Network(network, strict=False)
        return True
    except ValueError:
        return False


def ip_in_network(ip: str, network: str) -> bool:
    """Return True if ip belongs to the given network."""
    try:
        return ipaddress.IPv4Address(ip) in ipaddress.IPv4Network(network, strict=False)
    except ValueError:
        return False


def get_network_for_host(ip: str, mask: str) -> Optional[str]:
    """
    Return the network address for a host given its IP and subnet mask.

    Accepts both CIDR (/24) and dotted (255.255.255.0) masks.
    Returns None if inputs are invalid.
    """
    try:
        interface = ipaddress.IPv4Interface(f"{ip}/{mask}")
        return str(interface.network)
    except ValueError:
        return None


def same_subnet(ip1: str, ip2: str, mask: str) -> bool:
    """Return True if ip1 and ip2 are in the same subnet defined by mask."""
    try:
        iface1 = ipaddress.IPv4Interface(f"{ip1}/{mask}")
        iface2 = ipaddress.IPv4Interface(f"{ip2}/{mask}")
        return iface1.network == iface2.network
    except ValueError:
        return False


def mask_to_cidr(mask: str) -> Optional[int]:
    """Convert a dotted subnet mask to CIDR prefix length."""
    try:
        return ipaddress.IPv4Network(f"0.0.0.0/{mask}").prefixlen
    except ValueError:
        return None


def cidr_to_mask(prefix: int) -> str:
    """Convert a CIDR prefix length to dotted subnet mask."""
    return str(ipaddress.IPv4Network(f"0.0.0.0/{prefix}").netmask)


def is_apipa_address(ip: str) -> bool:
    """Return True if ip is an APIPA (link-local) address (169.254.x.x)."""
    try:
        addr = ipaddress.IPv4Address(ip)
        return addr in ipaddress.IPv4Network("169.254.0.0/16")
    except ValueError:
        return False


def find_covering_route(destination_ip: str, routes: list[str]) -> Optional[str]:
    """
    Find the most specific route from routes that covers destination_ip.

    routes: list of network strings like ['192.168.1.0/24', '0.0.0.0/0']
    Returns the best matching route or None.
    """
    try:
        dest = ipaddress.IPv4Address(destination_ip)
        best: Optional[ipaddress.IPv4Network] = None
        for route_str in routes:
            try:
                net = ipaddress.IPv4Network(route_str, strict=False)
                if dest in net:
                    if best is None or net.prefixlen > best.prefixlen:
                        best = net
            except ValueError:
                continue
        return str(best) if best else None
    except ValueError:
        return None


def extract_ips_from_text(text: str) -> list[str]:
    """Extract all valid IPv4 addresses from a text string."""
    import re
    pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    candidates = re.findall(pattern, text)
    return [ip for ip in candidates if is_valid_ip(ip)]
