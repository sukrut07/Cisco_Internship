"""
NetSage AI — Route Rule.

Checks for missing routes in the routing table.
Uses IP containment logic to avoid false positives when a covering route exists.
Extracts target networks from symptoms when destination_network is not explicitly set.
"""
from __future__ import annotations

import re
from typing import Any

from app.parsers.route_parser import parse_ip_route, find_route_for_network, has_default_route
from app.rules.base import BaseRule, RuleCheckResult
from app.utils.ip_utils import extract_ips_from_text, is_valid_ip


class RouteRule(BaseRule):
    """Detect missing routes, unreachable next-hops, and routing table issues."""

    name = "missing_route"
    description = "Checks whether destination networks are reachable in the routing table."

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        show_outputs: dict = context.get("show_outputs", {})
        routes: list[dict] = context.get("routes", [])
        destination_network: str | None = context.get("destination_network")
        symptom: str = context.get("symptom", "")

        # Parse from raw output if not pre-parsed
        if not routes and show_outputs.get("show ip route"):
            routes = parse_ip_route(show_outputs["show ip route"])

        if not routes:
            return self._not_checked("No routing table available.")

        evidence = []

        # If no explicit destination network, try to extract target IP from symptom
        if not destination_network and symptom:
            symptom_ips = extract_ips_from_text(symptom)
            # Find IPs that are not standard localhost/gateway/mask
            candidate_ips = [
                ip for ip in symptom_ips
                if not ip.startswith("127.") and not ip.startswith("255.") and not ip.endswith(".0")
            ]
            if candidate_ips:
                destination_network = candidate_ips[-1]  # Most likely target IP

        # Check for default route
        if not has_default_route(routes):
            evidence.append("No default route (0.0.0.0/0) found in routing table.")

        # Check for specific destination
        if destination_network:
            best_route = find_route_for_network(destination_network, routes)
            if best_route is None:
                evidence.append(
                    f"No route to destination {destination_network} in routing table."
                )
                return self._fail(
                    message=f"No route to {destination_network} in routing table.",
                    severity="HIGH",
                    evidence=evidence,
                    details={
                        "destination": destination_network,
                        "routes_checked": len(routes),
                    },
                )
            else:
                route_info = f"Route to {destination_network} found via {best_route.get('network')} ({best_route.get('type')})"
                return self._pass(
                    message=f"Route to {destination_network} exists.",
                    evidence=[route_info],
                )

        # Check routing protocols if output present
        proto_output = (show_outputs.get("show ip protocols") or "").lower()
        if "routing protocol is" not in proto_output and proto_output:
            evidence.append("No active dynamic routing protocol identified in 'show ip protocols'.")

        if evidence:
            return self._warning(
                message="Routing table may have issues.",
                severity="MEDIUM",
                evidence=evidence,
            )

        return self._pass(
            f"Routing table has {len(routes)} route(s). No obvious missing routes detected.",
            evidence=[f"Total routes: {len(routes)}"],
        )
