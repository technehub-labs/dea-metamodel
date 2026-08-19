"""CR-9.4 — snapshots and drift (CR-9BI, CR-9BD/BE)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..graph import GraphStore, Node
from ..graph.base import _parse_instant, utcnow
from ..scenario.engine import snapshot_store


@dataclass(frozen=True)
class Snapshot:
    """Frozen snapshot of a graph at a point in time."""

    id: str
    taken_at: str
    nodes: Dict[str, Dict[str, Any]]
    edges: Dict[tuple, Dict[str, Any]]
    label: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "takenAt": self.taken_at, "label": self.label,
            "nodes": list(self.nodes.values()),
            "edges": [dict(record, __key=list(key)) for key, record in self.edges.items()],
        }


@dataclass(frozen=True)
class SnapshotDelta:
    """CR-9BI: structural diff between two snapshots."""

    added_nodes: List[str] = field(default_factory=list)
    removed_nodes: List[str] = field(default_factory=list)
    modified_nodes: List[str] = field(default_factory=list)
    added_edges: List[tuple] = field(default_factory=list)
    removed_edges: List[tuple] = field(default_factory=list)
    modified_edges: List[tuple] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.added_nodes or self.removed_nodes or self.modified_nodes
                    or self.added_edges or self.removed_edges or self.modified_edges)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "addedNodes": self.added_nodes,
            "removedNodes": self.removed_nodes,
            "modifiedNodes": self.modified_nodes,
            "addedEdges": [list(e) for e in self.added_edges],
            "removedEdges": [list(e) for e in self.removed_edges],
            "modifiedEdges": [list(e) for e in self.modified_edges],
        }


def snapshot_graph(store: GraphStore, snapshot_id: str,
                   label: str = "") -> Snapshot:
    """CR-9BI: take a frozen snapshot of any GraphStore."""
    snap = snapshot_store(store)
    nodes = {n["id"]: n for n in snap["nodes"]}
    edges = {(e["source"], e["type"], e["target"]): e for e in snap["edges"]}
    return Snapshot(
        id=snapshot_id, taken_at=utcnow().isoformat(),
        nodes=nodes, edges=edges, label=label)


def diff_snapshots(before: Snapshot, after: Snapshot) -> SnapshotDelta:
    """Structural diff between two frozen snapshots."""
    added_nodes = sorted(set(after.nodes) - set(before.nodes))
    removed_nodes = sorted(set(before.nodes) - set(after.nodes))
    modified_nodes = sorted(
        node_id for node_id in set(after.nodes) & set(before.nodes)
        if before.nodes[node_id] != after.nodes[node_id])
    added_edges = sorted(set(after.edges) - set(before.edges))
    removed_edges = sorted(set(before.edges) - set(after.edges))
    modified_edges = sorted(
        key for key in set(after.edges) & set(before.edges)
        if before.edges[key] != after.edges[key])
    return SnapshotDelta(
        added_nodes=added_nodes, removed_nodes=removed_nodes,
        modified_nodes=modified_nodes, added_edges=added_edges,
        removed_edges=removed_edges, modified_edges=modified_edges)
