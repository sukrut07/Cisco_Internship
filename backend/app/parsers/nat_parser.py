"""
NetSage AI — NAT Parser.

Parses: show ip nat translations, show ip nat statistics
"""
from __future__ import annotations

import re


def parse_nat_translations(output: str) -> list[dict]:
    """
    Parse 'show ip nat translations' output.

    Returns list of NAT translation records:
    [{"proto": "tcp", "inside_local": "192.168.1.10:80", "inside_global": "203.0.113.5:80",
      "outside_local": "8.8.8.8:53", "outside_global": "8.8.8.8:53"}]
    """
    if not output or not output.strip():
        return []

    translations = []
    # Pro Inside global       Inside local        Outside local       Outside global
    # tcp 203.0.113.5:1025    192.168.1.10:1025   8.8.8.8:80          8.8.8.8:80
    #     203.0.113.5         192.168.1.100       ---                 ---
    pattern = re.compile(
        r"^\s*(\S+)\s+([\d.:]+)\s+([\d.:]+)\s+([\d.:]+|---)\s+([\d.:]+|---)\s*$",
        re.MULTILINE,
    )

    for match in pattern.finditer(output):
        proto, inside_global, inside_local, outside_local, outside_global = match.groups()
        translations.append(
            {
                "proto": proto,
                "inside_global": inside_global,
                "inside_local": inside_local,
                "outside_local": outside_local,
                "outside_global": outside_global,
            }
        )

    return translations


def parse_nat_statistics(output: str) -> dict:
    """
    Parse 'show ip nat statistics' output.

    Returns dict with key NAT statistics.
    """
    if not output or not output.strip():
        return {}

    stats: dict = {}

    total_pattern = re.compile(r"Total\s+translations:\s+(\d+)", re.IGNORECASE)
    outside_pattern = re.compile(r"(\d+)\s+outside\s+interfaces", re.IGNORECASE)
    inside_pattern = re.compile(r"(\d+)\s+inside\s+interfaces", re.IGNORECASE)
    hits_pattern = re.compile(r"Hits:\s+(\d+)", re.IGNORECASE)
    misses_pattern = re.compile(r"Misses:\s+(\d+)", re.IGNORECASE)

    for pattern, key in [
        (total_pattern, "total_translations"),
        (outside_pattern, "outside_interfaces"),
        (inside_pattern, "inside_interfaces"),
        (hits_pattern, "hits"),
        (misses_pattern, "misses"),
    ]:
        match = pattern.search(output)
        if match:
            stats[key] = int(match.group(1))

    return stats
