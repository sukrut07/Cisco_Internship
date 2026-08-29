"""
NetSage AI — Route Rule.

Checks for missing routes in the routing table.
Uses IP containment logic to avoid false positives when a covering route exists.
"""
from __future__ import annotations

from typing import Any

from app.rules.base import BaseRule, RuleCheckResult
from app.parsers.route_parser import parse_ip_route, find_route_for_network, has_default_route


class RouteRule(BaseRule):
    """Detect missing routes and routing table issues."""

    name = "missing_route"
    description = "Checks whether destination networks are reachable in the routing table."

    def check(self, context: dict[str, Any]) -> RuleCheckResult:
        show_outputs: dict = context.get("show_outputs", {})
        routes: list[dict] = context.get("routes", [])
        destination_network: str | None = context.get("destination_network")

        # Parse from raw output if not pre-parsed
        if not routes and show_outputs.get("show ip route"):
            routes = parse_ip_route(show_outputs["show ip route"])

        if not routes:
            return self._not_checked("No routing table available.")

        evidence = []

        # Check for default route
        if not has_default_route(routes):
            evidence.append("No default route (0.0.0.0/0) found in routing table.")

        # Check for specific destination
        if destination_network:
            best_route = find_route_for_network(destination_network, routes)
            if best_route is None:
                evidence.append(
                    f"No route to destination network {destination_network}. "
                    f"No covering route found."
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
