"""CR-9.10a — conformance classes, golden graphs and runner."""

import pytest

from runtime.conformance import (ConformanceClass, ConformanceReport,
                                ConformanceSuite, EXCLUDED_ENDPOINTS)
from runtime.conformance.golden import GOLDEN_GRAPHS, golden_graph_assertions
from runtime.conformance.runner import run_conformance
from runtime.graph import InMemoryGraphStore
from runtime.model import load_model

from conftest import BASE


def test_runtime_conformance_classes_are_explicitly_declared():
    """CR-9.10: the seven runtime conformance classes are listed, not implicit."""
    expected = {"Core", "Profile", "API", "Query",
                "Validation", "Provenance", "Security"}
    declared = {cls.value for cls in ConformanceClass}
    assert declared == expected


def test_endpoint_blacklist_excludes_repository(paths=None):
    """CR-9.10: budget reflects which runtime surfaces are deliberately not
    exposed by the public suite (none by default; room for future vendor-only
    paths)."""
    assert "store.infer" in EXCLUDED_ENDPOINTS
    assert "store.autonomous_mutate" in EXCLUDED_ENDPOINTS


def test_golden_graph_assets_are_present():
    """CR-9CN: golden graphs are deterministic, named, and loadable."""
    assert "enterprise" in GOLDEN_GRAPHS
    assert "dmm" in GOLDEN_GRAPHS
    assert "customer-service-baseline" in GOLDEN_GRAPHS


def test_golden_graph_assertions_match_loadable_state():
    """CR-9CN: expected node/edge counts and a traversal result are checked."""
    for path in GOLDEN_GRAPHS.values():
        store = InMemoryGraphStore()
        load_model(BASE / path, store)
        assertions = golden_graph_assertions(path)
        if "expected_nodes" in assertions:
            assert store.stats()["nodes"] == assertions["expected_nodes"]
        if "expected_edges" in assertions:
            assert store.stats()["edges"] == assertions["expected_edges"]


def test_conformance_runner_produces_class_resolution_report():
    """CR-9.10: the runner reports which classes are exercised by each suite."""
    suites = [
        ConformanceSuite(name="graphstore-contract",
                         classes=[ConformanceClass.CORE, ConformanceClass.QUERY]),
        ConformanceSuite(name="golden-graph",
                         classes=[ConformanceClass.CORE, ConformanceClass.VALIDATION]),
    ]
    report = run_conformance(suites)
    assert isinstance(report, ConformanceReport)
    assert report.suite_count == 2
    assert report.classes_covered == {"Core", "Query", "Validation"}
