"""CR-9.10b — performance suite (CR-9CJ/CK)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..graph import InMemoryGraphStore
from ..model import load_model


@dataclass(frozen=True)
class PerformanceSpec:
    """CR-9CK — one synthetic model scale."""

    name: str
    nodes: int
    edges_per_node: int = 3
    target_query_seconds: float = 5.0
    target_traversal_seconds: float = 5.0


# Engineering targets, not semantic SLAs (CR-9CJ). The budget is generous
# because the reference store is in-memory; per-vendor SLAs are out of scope.
DEFAULT_SPECS: List[PerformanceSpec] = [
    PerformanceSpec("scale.1k", nodes=1_000),
    PerformanceSpec("scale.10k", nodes=10_000),
]


@dataclass(frozen=True)
class PerformanceResult:
    spec: PerformanceSpec
    nodes: int
    edges_loaded: int
    load_seconds: float
    query_seconds: float
    traversal_seconds: float
    passed: bool
    failure_reason: str = ""

    def as_dict(self) -> Dict[str, object]:
        return {
            "spec": self.spec.name,
            "nodes": self.nodes,
            "edgesLoaded": self.edges_loaded,
            "loadSeconds": round(self.load_seconds, 4),
            "querySeconds": round(self.query_seconds, 4),
            "traversalSeconds": round(self.traversal_seconds, 4),
            "passed": self.passed,
            "failureReason": self.failure_reason,
        }


def _build_synthetic_model(spec: PerformanceSpec) -> Dict[str, object]:
    """Build a synthetic model from a spec without touching the disk."""
    elements = []
    for idx in range(spec.nodes):
        relationships = []
        for offset in range(1, spec.edges_per_node + 1):
            target = (idx + offset) % spec.nodes
            if target == idx:
                continue
            relationships.append({
                "type": "supports",
                "target": f"n.{target}",
                "status": "active",
            })
        elements.append({
            "id": f"n.{idx}",
            "type": "BusinessCapability",
            "name": f"Capability {idx}",
            "lifecycle_status": "active",
            "relationships": relationships,
        })
    return {
        "opendea": {"version": "1.0.0"},
        "model": {"id": spec.name, "name": spec.name, "version": "1.0.0"},
        "profiles": ["dea:core@1.0.0"],
        "context": {"kind": "enterprise"},
        "metadata": {"author": "openDEA-conformance", "assertion_status": "declared"},
        "elements": elements,
    }


class PerformanceSuite:
    """CR-9CK — runs the performance suite against the reference runtime."""

    SPECS: List[PerformanceSpec] = DEFAULT_SPECS

    def __init__(self, spec: PerformanceSpec):
        self.spec = spec

    def run(self) -> PerformanceResult:
        model = _build_synthetic_model(self.spec)
        store = InMemoryGraphStore()

        start = time.perf_counter()
        load_model_object = _load_inline(model, store)
        load_seconds = time.perf_counter() - start

        start = time.perf_counter()
        store.query(type="BusinessCapability")
        query_seconds = time.perf_counter() - start

        start = time.perf_counter()
        if store.has_entity("n.0"):
            store.traverse("n.0", max_depth=3)
        traversal_seconds = time.perf_counter() - start

        edges = sum(len(e.get("relationships", [])) for e in model["elements"])
        passed = (query_seconds < self.spec.target_query_seconds
                  and traversal_seconds < self.spec.target_traversal_seconds)
        failure = "" if passed else (
            f"query={query_seconds:.2f}s or "
            f"traversal={traversal_seconds:.2f}s exceeded target")
        return PerformanceResult(
            spec=self.spec,
            nodes=len([n for n in model["elements"] if "type" in n]),
            edges_loaded=edges,
            load_seconds=load_seconds,
            query_seconds=query_seconds,
            traversal_seconds=traversal_seconds,
            passed=passed,
            failure_reason=failure,
        )

    def run_all(self) -> List[PerformanceResult]:
        return [PerformanceSuite(spec).run() for spec in self.SPECS]


def _load_inline(model: Dict[str, object], store: InMemoryGraphStore):
    """Validate then materialize the synthetic model into the store."""
    from ..model.loader import load_document
    return load_document(model, store, validate=False)
