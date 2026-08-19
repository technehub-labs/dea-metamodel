"""CR-10 Phase 2 — impact graph, dependency propagation and architecture delta.

Phase 2 scope (CR-10AW): impact graph, dependency propagation, change analysis
and architecture delta. The engine is deliberately structural (CR-10K Level 0)
and keeps **impact** separate from **impact valence** (CR-10H): affected does
not automatically mean harmed.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..graph import GraphStore
from .engine import ScenarioEngine, _store_from_snapshot, snapshot_store
from .model import Baseline, Change, ChangeOperation, Scenario


class ImpactValence(str, Enum):
    """CR-10H — impact valence is explicit, never assumed from impact itself."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class ImpactCategory(str, Enum):
    """CR-10G — impact categories."""

    STRATEGIC = "strategic"
    BUSINESS = "business"
    CAPABILITY = "capability"
    PROCESS = "process"
    CUSTOMER = "customer"
    DATA = "data"
    APPLICATION = "application"
    TECHNOLOGY = "technology"
    SECURITY = "security"
    RISK = "risk"
    AGENT = "agent"
    GOVERNANCE = "governance"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"


EdgeKey = Tuple[str, str, str]


@dataclass(frozen=True)
class Impact:
    """CR-10G — one affected entity in the impact graph."""

    entity: str
    entity_type: str
    category: ImpactCategory
    depth: int
    direct: bool
    valence: ImpactValence = ImpactValence.UNKNOWN
    path: List[EdgeKey] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "entity": self.entity,
            "type": self.entity_type,
            "category": self.category.value,
            "depth": self.depth,
            "direct": self.direct,
            "valence": self.valence.value,
            "path": [list(e) for e in self.path],
        }


@dataclass(frozen=True)
class ChangeAnalysis:
    """CR-10 Phase 2 — what one scenario delta touches and what it impacts."""

    operation: ChangeOperation
    target: str
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    modified: List[str] = field(default_factory=list)
    impacts: List[Impact] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation.value,
            "target": self.target,
            "added": self.added,
            "removed": self.removed,
            "modified": self.modified,
            "impacts": [i.as_dict() for i in self.impacts],
        }


@dataclass(frozen=True)
class ImpactReport:
    """CR-10G/L — impact graph + change analysis + architecture delta."""

    scenario_id: str
    baseline_id: str
    delta: "ArchitectureDelta"
    changes: List[ChangeAnalysis]
    impacts: List[Impact]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "scenario": self.scenario_id,
            "baseline": self.baseline_id,
            "delta": self.delta.as_dict(),
            "changes": [c.as_dict() for c in self.changes],
            "impacts": [i.as_dict() for i in self.impacts],
        }


class ImpactEngine:
    """Dependency propagation and scenario impact evaluation."""

    _CATEGORY_BY_TYPE = {
        "StrategicObjective": ImpactCategory.STRATEGIC,
        "BusinessCapability": ImpactCategory.CAPABILITY,
        "BusinessProcess": ImpactCategory.PROCESS,
        "BusinessService": ImpactCategory.BUSINESS,
        "ApplicationComponent": ImpactCategory.APPLICATION,
        "Technology": ImpactCategory.TECHNOLOGY,
        "DataEntity": ImpactCategory.DATA,
        "InformationAsset": ImpactCategory.DATA,
        "Agent": ImpactCategory.AGENT,
        "Policy": ImpactCategory.GOVERNANCE,
        "Decision": ImpactCategory.GOVERNANCE,
        "Risk": ImpactCategory.RISK,
        "Customer": ImpactCategory.CUSTOMER,
    }

    def __init__(self,
                 valence_rules: Optional[Dict[Tuple[ChangeOperation, str],
                                              ImpactValence]] = None):
        self.valence_rules = valence_rules or {}

    def propagate(self, store: GraphStore,
                  sources: Iterable[str],
                  operation: ChangeOperation,
                  max_depth: int = 10,
                  direction: str = "out") -> List[Impact]:
        """Propagate impact along active dependency edges.

        Depth 1 is direct impact; depth > 1 is indirect. The first shortest
        path wins so results remain deterministic. Valence comes only from the
        explicit rule set — never from the operation itself (CR-10H).
        """
        impacted: Dict[str, Impact] = {}
        seen = set(sources)
        frontier = deque()
        for source in sources:
            if not store.has_entity(source):
                continue
            frontier.append((source, 0, []))

        while frontier:
            current, depth, path = frontier.popleft()
            if depth >= max_depth:
                continue
            for edge in store.edges_of(current, direction=direction):
                if not edge.is_active_at():
                    continue
                next_id = (edge.target if edge.source == current and direction != "in"
                           else edge.source)
                if next_id in seen:
                    continue
                node = store.get_entity(next_id)
                next_path = path + [edge.key]
                category = self._CATEGORY_BY_TYPE.get(
                    node.type, ImpactCategory.OPERATIONAL)
                valence = self.valence_rules.get(
                    (operation, node.type), ImpactValence.UNKNOWN)
                impacted[node.id] = Impact(
                    entity=node.id,
                    entity_type=node.type,
                    category=category,
                    depth=depth + 1,
                    direct=(depth + 1) == 1,
                    valence=valence,
                    path=next_path,
                )
                seen.add(node.id)
                frontier.append((node.id, depth + 1, next_path))
        return list(impacted.values())

    def evaluate(self, scenario: Scenario, baseline: Baseline,
                 scenario_engine: Optional[ScenarioEngine] = None) -> ImpactReport:
        """Evaluate a scenario's impact without mutating the baseline.

        The scenario engine produces a fresh simulated state (CR-10B); the
        impact engine then computes the architecture delta and propagates each
        explicit change through the baseline dependency graph (CR-10G/H).
        """
        engine = scenario_engine or ScenarioEngine()
        simulated = engine.simulate(scenario, baseline)
        delta = architecture_delta(baseline.snapshot, snapshot_store(simulated))
        baseline_store = _store_from_snapshot(baseline.snapshot)
        changes = [self._analyze_change(baseline_store, change)
                   for change in scenario.changes]

        merged: Dict[str, Impact] = {}
        for change in changes:
            for impact in change.impacts:
                prior = merged.get(impact.entity)
                if prior is None or impact.depth < prior.depth:
                    merged[impact.entity] = impact
        return ImpactReport(
            scenario_id=scenario.id,
            baseline_id=baseline.id,
            delta=delta,
            changes=changes,
            impacts=list(merged.values()),
        )

    def _analyze_change(self, store: GraphStore, change: Change) -> ChangeAnalysis:
        op = change.operation
        edge = change.edge or {}
        node = change.node or {}
        added: List[str] = []
        removed: List[str] = []
        modified: List[str] = []

        if op == ChangeOperation.ADD:
            added = [node.get("id", change.target)]
        elif op == ChangeOperation.REMOVE:
            removed = [change.target]
        elif op == ChangeOperation.REPLACE:
            removed = [change.target]
            if node.get("id"):
                added = [node["id"]]
        elif op in (ChangeOperation.MODIFY, ChangeOperation.RECLASSIFY,
                    ChangeOperation.ENABLE, ChangeOperation.DISABLE,
                    ChangeOperation.SCALE):
            modified = [change.target]
        elif op in (ChangeOperation.CONNECT, ChangeOperation.DISCONNECT):
            modified = [change.target]
            if edge.get("to"):
                modified.append(edge["to"])
        elif op == ChangeOperation.MOVE:
            modified = [change.target]
            if edge.get("from"):
                modified.append(edge["from"])
            if edge.get("to"):
                modified.append(edge["to"])

        # Both directions matter for structural replacement/removal: outgoing
        # edges identify dependents; incoming edges identify dependencies that
        # must be rewired or reviewed. Valence remains rules-driven.
        impacts = self.propagate(store, [change.target], op, direction="both")
        return ChangeAnalysis(operation=op, target=change.target,
                              added=added, removed=removed,
                              modified=modified, impacts=impacts)


@dataclass(frozen=True)
class ArchitectureDelta:
    """Difference between two graph snapshots (CR-10 Phase 2)."""

    added_entities: List[str] = field(default_factory=list)
    removed_entities: List[str] = field(default_factory=list)
    modified_entities: List[str] = field(default_factory=list)
    added_edges: List[EdgeKey] = field(default_factory=list)
    removed_edges: List[EdgeKey] = field(default_factory=list)
    modified_edges: List[EdgeKey] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "addedEntities": self.added_entities,
            "removedEntities": self.removed_entities,
            "modifiedEntities": self.modified_entities,
            "addedEdges": [list(e) for e in self.added_edges],
            "removedEdges": [list(e) for e in self.removed_edges],
            "modifiedEdges": [list(e) for e in self.modified_edges],
        }


def _edge_key(edge: Dict[str, Any]) -> EdgeKey:
    return (edge["source"], edge["type"], edge["target"])


def architecture_delta(before: Dict[str, Any],
                       after: Dict[str, Any]) -> ArchitectureDelta:
    """Compute the structural delta between two graph snapshots.

    Entity identity is the canonical id; relationship identity is
    ``(source, type, target)``. Metadata changes on the same identity are
    reported as modifications, not as remove/add pairs.
    """
    before_nodes = {n["id"]: n for n in before.get("nodes", [])}
    after_nodes = {n["id"]: n for n in after.get("nodes", [])}
    before_edges = {_edge_key(e): e for e in before.get("edges", [])}
    after_edges = {_edge_key(e): e for e in after.get("edges", [])}

    return ArchitectureDelta(
        added_entities=[n["id"] for n in after.get("nodes", [])
                        if n["id"] not in before_nodes],
        removed_entities=[n["id"] for n in before.get("nodes", [])
                          if n["id"] not in after_nodes],
        modified_entities=[n["id"] for n in after.get("nodes", [])
                           if n["id"] in before_nodes and before_nodes[n["id"]] != n],
        added_edges=[_edge_key(e) for e in after.get("edges", [])
                     if _edge_key(e) not in before_edges],
        removed_edges=[_edge_key(e) for e in before.get("edges", [])
                       if _edge_key(e) not in after_edges],
        modified_edges=[key for key, edge in after_edges.items()
                        if key in before_edges and before_edges[key] != edge],
    )
