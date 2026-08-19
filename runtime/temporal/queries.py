"""Temporal queries on the CR-9.1 graph.

CR-9F / CR-9G: respect valid_from/valid_to, lifecycle status, and (when
present) transaction-time metadata. The bitemporal helper `as_of` answers
"what was true at valid_at, as we knew it at recorded_at".
"""
from __future__ import annotations

from typing import Any, List, Optional

from ..graph import GraphStore, Node
from ..graph.base import _parse_instant, utcnow


def what_is_true_now(store: GraphStore, entity_id: str,
                     at: Optional[Any] = None) -> List[Node]:
    """CR-9F: filter neighbours by both valid time and lifecycle status."""
    return store.neighbors(entity_id, direction="in", at=at)


def as_of(store: GraphStore, entity_id: str,
          valid_at: Any, recorded_at: Optional[Any] = None,
          direction: str = "in") -> List[Node]:
    """CR-9G: bitemporal query — return nodes whose edges were valid at
    ``valid_at`` *and* were recorded at-or-before ``recorded_at`` (default: now).
    """
    recorded = _parse_instant(recorded_at) or utcnow()
    valid = _parse_instant(valid_at)
    if valid is None:
        raise ValueError("valid_at is required for bitemporal queries")
    result: List[Node] = []
    for edge in store.edges_of(entity_id, direction=direction):
        if not edge.is_active_at(valid):
            continue
        recorded_at_str = edge.properties.get("recorded_at") if edge.properties else None
        if recorded_at_str is None:
            result.append(store.get_entity(
                edge.target if edge.source == entity_id and direction != "in"
                else edge.source))
            continue
        edge_recorded = _parse_instant(recorded_at_str)
        if edge_recorded is None or edge_recorded > recorded:
            continue
        result.append(store.get_entity(
            edge.target if edge.source == entity_id and direction != "in"
            else edge.source))
    return result


def snapshots(store: GraphStore, entity_id: str,
              instants: List[Any]) -> List[List[Node]]:
    """Return a snapshot of inbound neighbours at each instant."""
    return [store.neighbors(entity_id, direction="in", at=at) for at in instants]
