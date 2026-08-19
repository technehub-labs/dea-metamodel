"""CR-9.7 — decision & impact engine (CR-9 §73/§74).

Wraps the scenario impact engine and decision intelligence service as a
runtime Decision & Impact Engine that operates on the live graph (not just
scenarios). Decisions are summarised against the graph, dependency paths are
exposed for impact analysis, and proposed ChangeInitiatives land on the graph
with explicit authorship.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from ..api import RuntimeService
from ..graph import GraphStore


@dataclass(frozen=True)
class DecisionEvaluation:
    """Summary of one Decision against the current graph state."""

    decision_id: str
    node: Mapping[str, Any]
    addressed_gap_id: Optional[str]
    proposed_outcome_ids: List[str]
    dependency_paths: List[Tuple[List[str], List[Tuple[str, str, str]]]] = field(
        default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "decisionId": self.decision_id,
            "node": dict(self.node),
            "addressedGapId": self.addressed_gap_id,
            "proposedOutcomeIds": list(self.proposed_outcome_ids),
            "dependencyPaths": [
                {"nodes": nodes, "edges": [list(e) for e in edges]}
                for nodes, edges in self.dependency_paths
            ],
        }


class DecisionError(Exception):
    """Decision engine invariant violated."""


class DecisionImpactEngine:
    """CR-9 §73/§74 — runtime decision evaluation and change linkage."""

    def __init__(self, service: RuntimeService):
        self.service = service

    def evaluate_decision(self, decision_id: str) -> DecisionEvaluation:
        store = self.service.store
        if not store.has_entity(decision_id):
            raise DecisionError(f"unknown decision {decision_id!r}")
        node = store.get_entity(decision_id)
        if node.type != "Decision":
            raise DecisionError(
                f"node {decision_id!r} is a {node.type}, not a Decision")

        gap_id = self._find_addressed_gap(decision_id)
        outcome_ids = [
            edge.target for edge in store.edges_of(
                decision_id, direction="out", rel_type="results-in")
        ]
        paths = self.dependency_paths(decision_id, gap_id) if gap_id else []
        return DecisionEvaluation(
            decision_id=decision_id,
            node={
                "id": node.id, "name": node.name,
                "lifecycle_status": node.lifecycle_status,
                "properties": dict(node.properties),
            },
            addressed_gap_id=gap_id,
            proposed_outcome_ids=outcome_ids,
            dependency_paths=paths,
        )

    def dependency_paths(self, start: str, target: Optional[str],
                         max_depth: int = 6
                         ) -> List[Tuple[List[str], List[Tuple[str, str, str]]]]:
        """Return shortest dependency paths from start to target (or any target).

        Each path is (nodes, edges) where ``edges`` is the sequence of
        relationship keys traversed.
        """
        if not self.service.store.has_entity(start):
            raise DecisionError(f"unknown start entity {start!r}")
        if target is not None and not self.service.store.has_entity(target):
            raise DecisionError(f"unknown target entity {target!r}")
        paths: List[Tuple[List[str], List[Tuple[str, str, str]]]] = []
        seen_targets: set = set()
        from collections import deque
        queue: deque = deque([(start, [start], [])])
        while queue:
            current, nodes, edges = queue.popleft()
            if target is not None and current == target and len(nodes) > 1:
                paths.append((list(nodes), list(edges)))
                seen_targets.add(current)
                continue
            if target is None and current != start and current not in seen_targets:
                paths.append((list(nodes), list(edges)))
                seen_targets.add(current)
            if len(nodes) >= max_depth + 1:
                continue
            for edge in self.service.store.edges_of(current, direction="out"):
                if edge.status in ("deprecated", "retired"):
                    continue
                if edge.target not in nodes:
                    queue.append((edge.target, nodes + [edge.target],
                                   edges + [edge.key]))
        return paths

    def propose_initiatives(self, decision_id: str,
                              proposals: Iterable[Mapping[str, Any]]
                              ) -> List[str]:
        """Materialise proposed ChangeInitiatives on the graph.

        A proposal is a mapping with `id`, `name`, and arbitrary metadata. The
        engine creates a `ChangeInitiative` node for each proposal that does
        not already exist, and connects it to ``decision_id`` via
        ``results-in``. Existing initiative ids are returned as-is.
        """
        store = self.service.store
        if not store.has_entity(decision_id):
            raise DecisionError(f"unknown decision {decision_id!r}")
        if self.service.get_entity(decision_id).type != "Decision":
            raise DecisionError(
                f"node {decision_id!r} is not a Decision")
        created: List[str] = []
        for proposal in proposals:
            pid = proposal.get("id")
            if not pid:
                raise DecisionError("proposals require an id")
            if store.has_entity(pid):
                continue
            props = {k: v for k, v in proposal.items() if k != "id" and k != "name"}
            self.service.create_entity(
                pid, "Outcome",
                proposal.get("name", pid),
                properties=props)
            self.service.create_relationship(
                decision_id, "results-in", pid, status="proposed")
            created.append(pid)
        return created

    def _find_addressed_gap(self, decision_id: str) -> Optional[str]:
        """Best-effort: a Decision may address an AssessmentGap via any
        outgoing relationship to an AssessmentGap node."""
        for edge in self.service.store.edges_of(decision_id, direction="out"):
            node = self.service.store.get_entity(edge.target)
            if node.type == "AssessmentGap":
                return node.id
        return None
