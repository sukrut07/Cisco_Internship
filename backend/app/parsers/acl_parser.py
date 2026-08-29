"""
NetSage AI — ACL Parser.

Parses: show access-lists, show ip access-lists
"""
from __future__ import annotations

import re


def parse_access_lists(output: str) -> list[dict]:
    """
    Parse 'show access-lists' output.

    Returns list of ACL records grouped by ACL name/number.
    [
      {
        "acl_name": "100",
        "type": "extended",
        "entries": [
          {
            "sequence": "10",
            "action": "deny",
            "protocol": "ip",
            "source": "192.168.10.0",
            "source_wildcard": "0.0.0.255",
            "destination": "any",
            "destination_wildcard": None,
            "matches": 42
          }
        ]
      }
    ]
    """
    if not output or not output.strip():
        return []

    acls: list[dict] = []
    current_acl: dict | None = None

    # ACL header: Extended IP access list 100  OR  Standard IP access list MGMT
    acl_header = re.compile(
        r"^(Standard|Extended)\s+IP\s+access\s+list\s+(\S+)",
        re.IGNORECASE | re.MULTILINE,
    )

    # ACE entry: 10 deny ip 192.168.10.0 0.0.0.255 any (42 matches)
    ace_pattern = re.compile(
        r"^\s+(\d+)\s+(permit|deny)\s+(\S+)\s+([\d.]+|any|host\s+[\d.]+)\s*"
        r"([\d.]+)?\s*([\d.]+|any|host\s+[\d.]+)?\s*([\d.]+)?\s*"
        r"(?:\((\d+)\s+match(?:es)?\))?",
        re.IGNORECASE | re.MULTILINE,
    )

    lines = output.split("\n")
    for line in lines:
        header_match = acl_header.match(line)
        if header_match:
            acl_type, acl_name = header_match.groups()
            current_acl = {
                "acl_name": acl_name,
                "type": acl_type.lower(),
                "entries": [],
            }
            acls.append(current_acl)
            continue

        if current_acl:
            ace_match = ace_pattern.match(line)
            if ace_match:
                (seq, action, protocol, src, src_wild, dst, dst_wild, matches) = ace_match.groups()
                current_acl["entries"].append(
                    {
                        "sequence": seq,
                        "action": action.lower(),
                        "protocol": protocol.lower(),
                        "source": src,
                        "source_wildcard": src_wild,
                        "destination": dst,
                        "destination_wildcard": dst_wild,
                        "matches": int(matches) if matches else 0,
                    }
                )

    return acls


def has_deny_rules(acls: list[dict]) -> bool:
    """Return True if any ACL has deny entries with matches."""
    for acl in acls:
        for entry in acl.get("entries", []):
            if entry.get("action") == "deny" and entry.get("matches", 0) > 0:
                return True
    return False
