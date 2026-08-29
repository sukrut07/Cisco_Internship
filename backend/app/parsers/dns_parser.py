"""
NetSage AI — DNS Output Parser.

Parses outputs of 'show hosts', 'show ip dns', 'nslookup', and DNS configs.
"""
from __future__ import annotations

import re
from typing import Any


def parse_show_hosts(output: str) -> dict[str, Any]:
    """
    Parse 'show hosts' or 'show ip hosts' command output.

    Returns:
        {
            "default_domain": str | None,
            "name_servers": list[str],
            "host_entries": list[dict[str, Any]]
        }
    """
    result: dict[str, Any] = {
        "default_domain": None,
        "name_servers": [],
        "host_entries": [],
    }

    if not output:
        return result

    for line in output.splitlines():
        line_clean = line.strip()

        # Domain name
        domain_match = re.search(r"Default domain is\s+([^\s]+)", line_clean, re.IGNORECASE)
        if domain_match:
            result["default_domain"] = domain_match.group(1)

        # Name servers
        ns_match = re.search(r"Name servers are\s+([^\s]+(?:\s*,\s*[^\s]+)*)", line_clean, re.IGNORECASE)
        if ns_match:
            servers = [s.strip() for s in ns_match.group(1).split(",") if s.strip()]
            result["name_servers"].extend(servers)

        # Host table entries (e.g., "server1 (temp, OK) 192.168.1.100")
        host_match = re.match(r"^([a-zA-Z0-9\-_.]+)\s+\([^)]+\)\s+((?:\d{1,3}\.){3}\d{1,3})", line_clean)
        if host_match:
            result["host_entries"].append({
                "hostname": host_match.group(1),
                "ip": host_match.group(2),
            })

    return result


def parse_nslookup(output: str) -> dict[str, Any]:
    """
    Parse 'nslookup' test output.

    Returns:
        {
            "server": str | None,
            "resolved_ip": str | None,
            "timed_out": bool,
            "server_failure": bool,
            "non_existent_domain": bool
        }
    """
    result = {
        "server": None,
        "resolved_ip": None,
        "timed_out": False,
        "server_failure": False,
        "non_existent_domain": False,
    }

    if not output:
        return result

    out_lower = output.lower()
    if "timed out" in out_lower or "timed-out" in out_lower or "timeout" in out_lower or "no response" in out_lower:
        result["timed_out"] = True
    if "server can't find" in out_lower or "can't find" in out_lower or "non-existent domain" in out_lower:
        result["non_existent_domain"] = True
    if "server failure" in out_lower or "servfail" in out_lower:
        result["server_failure"] = True

    # Find server
    server_match = re.search(r"Server:\s+((?:\d{1,3}\.){3}\d{1,3}|[^\s]+)", output, re.IGNORECASE)
    if server_match:
        result["server"] = server_match.group(1)

    # Find address
    addr_match = re.search(r"Address:\s+((?:\d{1,3}\.){3}\d{1,3})", output, re.IGNORECASE)
    if addr_match:
        result["resolved_ip"] = addr_match.group(1)

    return result
