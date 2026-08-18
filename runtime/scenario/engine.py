"""CR-10 Phase 1 — Scenario engine: baselines, validation, simulated state.

The engine enforces the scenario architecture's central separation
(CR-10 §3):

    Current State
          │
       Baseline          ← frozen, never mutated
          │
      Scenario (delta)   ← first-class object, only changes
          │
     Simulated State     ← a NEW graph; production untouched

Phase 1 scope (CR-10AW): Scenario, Baseline, Change, Assumption, Constraint,
Outcome — with structural (Level 0, CR-10K) application of the delta. Impact
propagation (CR-10H), constraint evaluation, scoring and ranking land in
Phases 2–3; the simulated state produced here is their input.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import yaml

from ..graph import Edge, GraphStore, InMemoryGraphStore, Node
from .model import (Assumption, Baseline, Change, ChangeOperation, Constraint,
                    Outcome, Scenario, ScenarioError, ScenarioStatus,
                    Uncertainty)


class ScenarioValidationError(ScenarioError):
    """The scenario delta is structurally or semantically invalid."""


def snapshot_store(store: GraphStore) -> Dict[str, Any]:
    """Extract a frozen node/edge snapshot from any GraphStore."""
    nodes = [
        {"id": n.id, "type": n.type, "name": n.name, "version": n.version,
         "lifecycle_status": n.lifecycle_status, "assertion": n.assertion,
         "source": n.source, "properties": n.properties}
        for n in store.query()
    ]
    edges = []
    seen = set()
    for n in store.query():
        for e in store.edges_of(n.id, direction="out"):
            if e.key in seen:
                continue
            seen.add(e.key)
            edges.append({"type": e.type, "source": e.source, "target": e.target,
                          "valid_from": e.valid_from, "valid_to": e.valid_to,
                          "status": e.status, "provenance": e.provenance,
                          "properties": e.properties})
    return {"nodes": nodes, "edges": edges}


def _store_from_snapshot(snapshot: Dict[str, Any]) -> InMemoryGraphStore:
    store = InMemoryGraphStore()
    with store.transaction():
        for nd in snapshot["nodes"]:
            store.create_entity(Node(**nd))
        for ed in snapshot["edges"]:
            store.create_relationship(Edge(**ed))
    return store


class ScenarioEngine:
    """Creates baselines, validates scenarios, produces simulated states.

    The engine never mutates the store a baseline was taken from — simulation
    runs on a fresh graph rehydrated from the frozen snapshot (CR-10B).
    """

    def __init__(self, registry=None):
        # registry: runtime.api.Registry-compatible object for semantic checks.
        # Late import to keep the engine usable without the service layer.
        if registry is None:
            from ..api.service import Registry
            registry = Registry
        self.registry = registry

    # ---- baselines ----
    def create_baseline(self, store: GraphStore, baseline_id: str, name: str,
                        source: str = "runtime") -> Baseline:
        """Freeze the current graph as an immutable baseline (CR-10B)."""
        return Baseline(id=baseline_id, name=name,
                        snapshot=snapshot_store(store), source=source)

    # ---- validation ----
    def validate(self, scenario: Scenario, baseline: Baseline) -> List[str]:
        """Structural + registry validation of the delta against the baseline.
        Returns a list of problems (empty = valid)."""
        problems: List[str] = []
        if scenario.baseline != baseline.id:
            problems.append(f"scenario references baseline {scenario.baseline!r} "
                            f"but was validated against {baseline.id!r}")
        ids = {nd["id"] for nd in baseline.snapshot["nodes"]}
        edge_keys = {(ed["source"], ed["type"], ed["target"])
                     for ed in baseline.snapshot["edges"]}
        added: set = set()
        removed: set = set()
        entities = self.registry.entities()
        rels = self.registry.relationships()

        def live(eid: str) -> bool:
            return (eid in ids or eid in added) and eid not in removed

        for i, c in enumerate(scenario.changes):
            where = f"change[{i}] {c.operation.value} {c.target!r}"
            if c.operation == ChangeOperation.ADD:
                spec = c.node or {}
                nid = spec.get("id", c.target)
                if live(nid):
                    problems.append(f"{where}: entity {nid!r} already exists")
                ntype = spec.get("type")
                if not ntype:
                    problems.append(f"{where}: ADD requires node.type")
                elif ntype not in entities:
                    problems.append(f"{where}: unknown type {ntype!r} (DEA-E001)")
                elif entities[ntype].get("abstract"):
                    problems.append(f"{where}: type {ntype} is abstract (CR-8 §9)")
                if not spec.get("name"):
                    problems.append(f"{where}: ADD requires node.name")
                added.add(nid)
            elif c.operation == ChangeOperation.REMOVE:
                if not live(c.target):
                    problems.append(f"{where}: target not present in baseline")
                removed.add(c.target)
            elif c.operation in (ChangeOperation.MODIFY, ChangeOperation.ENABLE,
                                 ChangeOperation.DISABLE, ChangeOperation.SCALE,
                                 ChangeOperation.RECLASSIFY):
                if not live(c.target):
                    problems.append(f"{where}: target not present")
                if c.operation == ChangeOperation.RECLASSIFY:
                    ntype = c.set.get("type")
                    if not ntype or ntype not in entities:
                        problems.append(f"{where}: unknown reclassify type {ntype!r}")
                    elif entities[ntype].get("abstract"):
                        problems.append(f"{where}: type {ntype} is abstract (CR-8 §9)")
            elif c.operation == ChangeOperation.REPLACE:
                if not live(c.target):
                    problems.append(f"{where}: target not present")
                spec = c.node or {}
                nid = spec.get("id")
                if not nid:
                    problems.append(f"{where}: REPLACE requires node.id (the replacement)")
                elif live(nid):
                    problems.append(f"{where}: replacement {nid!r} already exists")
                ntype = spec.get("type")
                if not ntype or ntype not in entities:
                    problems.append(f"{where}: unknown replacement type {ntype!r}")
                if not spec.get("name"):
                    problems.append(f"{where}: REPLACE requires node.name")
                removed.add(c.target)
                if nid:
                    added.add(nid)
            elif c.operation == ChangeOperation.CONNECT:
                e = c.edge or {}
                if not live(c.target):
                    problems.append(f"{where}: source not present")
                if not e.get("to") or not live(e.get("to", "")):
                    problems.append(f"{where}: edge.to not present")
                rtype = e.get("type")
                if not rtype or rtype not in rels:
                    problems.append(f"{where}: undeclared relationship type {rtype!r} (DEA-E002)")
                key = (c.target, rtype, e.get("to"))
                if key in edge_keys:
                    problems.append(f"{where}: relationship already exists")
                edge_keys.add(key)
            elif c.operation == ChangeOperation.DISCONNECT:
                e = c.edge or {}
                key = (c.target, e.get("type"), e.get("to"))
                if key not in edge_keys:
                    problems.append(f"{where}: relationship not present")
                edge_keys.discard(key)
            elif c.operation == ChangeOperation.MOVE:
                e = c.edge or {}
                old = (c.target, e.get("type"), e.get("from"))
                if old not in edge_keys:
                    problems.append(f"{where}: relationship to move not present")
                if not e.get("to") or not live(e.get("to", "")):
                    problems.append(f"{where}: move destination not present")
                edge_keys.discard(old)
                edge_keys.add((c.target, e.get("type"), e.get("to")))
        return problems

    # ---- simulation ----
    def simulate(self, scenario: Scenario, baseline: Baseline) -> InMemoryGraphStore:
        """Apply the delta to a FRESH graph — the baseline is never touched.

        Returns the simulated state (CR-10 Level 0: structural). Raises
        ScenarioValidationError if the delta is invalid.
        """
        if scenario.status != ScenarioStatus.DEFINED:
            raise ScenarioError(
                f"scenario {scenario.id!r} must be DEFINED to simulate "
                f"(status: {scenario.status.value}). CR-10A lifecycle: "
                "Draft → Defined → Evaluating → Evaluated.")
        problems = self.validate(scenario, baseline)
        if problems:
            raise ScenarioValidationError(
                "scenario is invalid:\n  - " + "\n  - ".join(problems))
        scenario.transition(ScenarioStatus.EVALUATING)
        sim = _store_from_snapshot(baseline.snapshot)
        with sim.transaction():
            for c in scenario.changes:
                self._apply(sim, c)
        scenario.transition(ScenarioStatus.EVALUATED)  # freezes (CR-10AG)
        return sim

    def _apply(self, sim: GraphStore, c: Change) -> None:
        op = c.operation
        if op == ChangeOperation.ADD:
            spec = dict(c.node or {})
            sim.create_entity(Node(
                id=spec.get("id", c.target), type=spec["type"], name=spec["name"],
                version=spec.get("version", "1.0.0"),
                lifecycle_status=spec.get("lifecycle_status"),
                assertion=spec.get("assertion") or {},
                source=spec.get("source") or {},
                properties=spec.get("properties") or {}))
        elif op == ChangeOperation.REMOVE:
            sim.delete_entity(c.target, cascade=True)
        elif op == ChangeOperation.REPLACE:
            spec = dict(c.node or {})
            new_id = spec["id"]
            old_edges = sim.edges_of(c.target, direction="both")
            sim.delete_entity(c.target, cascade=True)
            sim.create_entity(Node(
                id=new_id, type=spec["type"], name=spec["name"],
                version=spec.get("version", "1.0.0"),
                lifecycle_status=spec.get("lifecycle_status"),
                assertion=spec.get("assertion") or {},
                source=spec.get("source") or {},
                properties=spec.get("properties") or {}))
            for e in old_edges:  # rewire
                sim.create_relationship(Edge(
                    type=e.type,
                    source=new_id if e.source == c.target else e.source,
                    target=new_id if e.target == c.target else e.target,
                    valid_from=e.valid_from, valid_to=e.valid_to,
                    status=e.status, provenance=e.provenance,
                    properties=e.properties))
        elif op == ChangeOperation.MODIFY:
            changes = {}
            for k, v in c.set.items():
                if k == "properties":
                    node = sim.get_entity(c.target)
                    changes["properties"] = {**node.properties, **v}
                elif k in ("name", "lifecycle_status", "assertion", "source", "version"):
                    changes[k] = v
                else:
                    raise ScenarioValidationError(f"MODIFY cannot set field {k!r}")
            sim.update_entity(c.target, **changes)
        elif op == ChangeOperation.RECLASSIFY:
            node = sim.get_entity(c.target)
            edges = sim.edges_of(c.target, direction="both")
            sim.delete_entity(c.target, cascade=True)
            sim.create_entity(Node(
                id=node.id, type=c.set["type"], name=node.name,
                version=node.version, lifecycle_status=node.lifecycle_status,
                assertion=node.assertion, source=node.source,
                properties=node.properties))
            for e in edges:
                sim.create_relationship(e)
        elif op == ChangeOperation.CONNECT:
            e = c.edge or {}
            sim.create_relationship(Edge(
                type=e["type"], source=c.target, target=e["to"],
                valid_from=e.get("valid_from"), valid_to=e.get("valid_to"),
                status=e.get("status"), provenance=e.get("provenance") or {},
                properties=e.get("properties") or {}))
        elif op == ChangeOperation.DISCONNECT:
            e = c.edge or {}
            sim.delete_relationship(c.target, e["type"], e["to"])
        elif op == ChangeOperation.ENABLE:
            sim.update_entity(c.target, lifecycle_status="active")
        elif op == ChangeOperation.DISABLE:
            sim.update_entity(c.target, lifecycle_status="deprecated")
        elif op == ChangeOperation.MOVE:
            e = c.edge or {}
            old = [x for x in sim.edges_of(c.target, direction="out")
                   if x.type == e["type"] and x.target == e["from"]][0]
            sim.delete_relationship(c.target, e["type"], e["from"])
            sim.create_relationship(Edge(
                type=old.type, source=old.source, target=e["to"],
                valid_from=old.valid_from, valid_to=old.valid_to,
                status=old.status, provenance=old.provenance,
                properties=old.properties))
        elif op == ChangeOperation.SCALE:
            node = sim.get_entity(c.target)
            sim.update_entity(c.target,
                              properties={**node.properties, "scale": c.set["scale"]})
        else:  # pragma: no cover — enum is closed
            raise ScenarioValidationError(f"unsupported operation {op}")


# ---- scenario file loading (CR-10AS golden scenario format) ----

def scenario_from_dict(doc: Dict[str, Any]) -> Scenario:
    """Parse a scenario document (YAML/JSON) into a Scenario object."""
    sc = doc["scenario"]
    return Scenario(
        id=sc["id"], name=sc["name"], baseline=sc["baseline"],
        description=sc.get("description", ""), owner=sc.get("owner", ""),
        purpose=sc.get("purpose", ""),
        changes=[Change(target=c["target"],
                        operation=ChangeOperation(c["operation"]),
                        node=c.get("node"), edge=c.get("edge"),
                        set=c.get("set") or {}, rationale=c.get("rationale", ""))
                 for c in sc.get("changes", [])],
        assumptions=[Assumption(**a) for a in sc.get("assumptions", [])],
        constraints=[Constraint(**c) for c in sc.get("constraints", [])],
        expected_outcomes=[Outcome(**{**o, "uncertainty": Uncertainty(o.get("uncertainty", "estimated"))})
                           for o in sc.get("expectedOutcomes", [])],
        provenance=sc.get("provenance") or {},
    )


def load_scenario(path: str) -> Scenario:
    return scenario_from_dict(yaml.safe_load(open(path).read()))
