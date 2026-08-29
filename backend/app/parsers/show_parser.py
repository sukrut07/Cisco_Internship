"""
NetSage AI — Central Show Command Parser Dispatcher.

Dispatches Cisco show-command text to the appropriate parser and returns
normalized structured output.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from app.core.security import normalize_command_name
from app.parsers.interface_parser import parse_ip_interface_brief, parse_show_interfaces
from app.parsers.vlan_parser import parse_vlan_brief
from app.parsers.route_parser import parse_ip_route
from app.parsers.acl_parser import parse_access_lists
from app.parsers.dhcp_parser import parse_dhcp_binding, parse_dhcp_pool
from app.parsers.nat_parser import parse_nat_translations, parse_nat_statistics
from app.parsers.trunk_parser import parse_interfaces_trunk
from app.parsers.dns_parser import parse_show_hosts, parse_nslookup


# ---------------------------------------------------------------------------
# Parser registry
# ---------------------------------------------------------------------------

_PARSER_REGISTRY: dict[str, Any] = {
    "show ip interface brief": parse_ip_interface_brief,
    "show interfaces": parse_show_interfaces,
    "show vlan brief": parse_vlan_brief,
    "show ip route": parse_ip_route,
    "show access-lists": parse_access_lists,
    "show ip access-lists": parse_access_lists,
    "show ip dhcp binding": parse_dhcp_binding,
    "show ip dhcp pool": parse_dhcp_pool,
    "show ip nat translations": parse_nat_translations,
    "show ip nat statistics": parse_nat_statistics,
    "show interfaces trunk": parse_interfaces_trunk,
    "show hosts": parse_show_hosts,
    "show ip hosts": parse_show_hosts,
    "nslookup": parse_nslookup,
}


class CiscoShowParser:
    """
    Central dispatcher for Cisco show-command parsers.

    Usage:
        parser = CiscoShowParser()
        result = parser.parse("show ip route", route_output)
    """

    def parse(self, command: str, output: str) -> dict[str, Any]:
        """
        Parse a Cisco show-command output.

        Returns:
            {
              "command": normalized command name,
              "parsed": structured data (list or dict),
              "status": "ok" | "unknown_format" | "empty" | "error"
            }
        """
        normalized = normalize_command_name(command)

        if not output or not output.strip():
            return {"command": normalized, "parsed": None, "status": "empty"}

        parser_fn = self._find_parser(normalized)
        if parser_fn is None:
            return {"command": normalized, "parsed": None, "status": "unknown_format"}

        try:
            parsed = parser_fn(output)
            return {"command": normalized, "parsed": parsed, "status": "ok"}
        except Exception as exc:
            return {
                "command": normalized,
                "parsed": None,
                "status": "error",
                "error": str(exc),
            }

    def _find_parser(self, normalized_cmd: str):
        """Find the appropriate parser function for a normalized command."""
        # Exact match first
        if normalized_cmd in _PARSER_REGISTRY:
            return _PARSER_REGISTRY[normalized_cmd]

        # Prefix match (e.g., "show interfaces gi0/0" → parse_show_interfaces)
        for key, fn in _PARSER_REGISTRY.items():
            if normalized_cmd.startswith(key):
                return fn

        return None

    def parse_all(self, show_outputs: dict[str, str]) -> dict[str, dict[str, Any]]:
        """
        Parse all show outputs in a dict.

        Returns a dict keyed by normalized command name.
        """
        results: dict[str, dict[str, Any]] = {}
        for cmd, output in show_outputs.items():
            normalized = normalize_command_name(cmd)
            results[normalized] = self.parse(cmd, output)
        return results

    def get_interfaces(self, show_outputs: dict[str, str]) -> list[dict]:
        """Convenience: extract interface list from show outputs."""
        output = show_outputs.get("show ip interface brief", "")
        if output:
            return parse_ip_interface_brief(output)
        return []

    def get_routes(self, show_outputs: dict[str, str]) -> list[dict]:
        """Convenience: extract routing table from show outputs."""
        output = show_outputs.get("show ip route", "")
        if output:
            return parse_ip_route(output)
        return []

    def get_vlans(self, show_outputs: dict[str, str]) -> list[dict]:
        """Convenience: extract VLAN table from show outputs."""
        output = show_outputs.get("show vlan brief", "")
        if output:
            return parse_vlan_brief(output)
        return []

    def get_trunks(self, show_outputs: dict[str, str]) -> list[dict]:
        """Convenience: extract trunk list from show outputs."""
        output = show_outputs.get("show interfaces trunk", "")
        if output:
            return parse_interfaces_trunk(output)
        return []

    def get_acls(self, show_outputs: dict[str, str]) -> list[dict]:
        """Convenience: extract ACL list from show outputs."""
        output = show_outputs.get("show access-lists", "") or show_outputs.get(
            "show ip access-lists", ""
        )
        if output:
            return parse_access_lists(output)
        return []

    def get_nat_translations(self, show_outputs: dict[str, str]) -> list[dict]:
        """Convenience: extract NAT translations from show outputs."""
        output = show_outputs.get("show ip nat translations", "")
        if output:
            return parse_nat_translations(output)
        return []

    def get_dhcp_bindings(self, show_outputs: dict[str, str]) -> list[dict]:
        """Convenience: extract DHCP bindings from show outputs."""
        output = show_outputs.get("show ip dhcp binding", "")
        if output:
            return parse_dhcp_binding(output)
        return []


# Module-level singleton
cisco_parser = CiscoShowParser()
