"""CR-9.7 — decision & impact engine tests."""
from pathlib import Path

import pytest

from runtime.api import RuntimeService
from runtime.decision import (DecisionEvaluation, DecisionError,
                                DecisionImpactEngine)
from runtime.graph import InMemoryGraphStore
from runtime.model import load_model

from conftest import BASE


def _assembled_appraisal():
    """CR-9 §73/§74: DMM gap drives a Decision; the decision produces Outcomes
    that the proposal engine writes to as ChangeInitiatives."""
    store = InMemoryGraphStore()
    service = RuntimeService(store)
    load_model(BASE / "models" / "dmm" / "executable.yaml", store)
    from runtime.assessment import AssessmentService
    AssessmentService(store).execute_assessment("asm.2026-q3")
    svc = service
    svc.create_entity("dec.2026-q3", "Decision",
                      "2026-Q3 Maturity Decision",
                      properties={"description": "Address DMM gap"},
                      lifecycle_status="proposed")
    svc.create_entity("ci.training", "Outcome",
                      "Tooling Automation Training",
                      properties={"target_maturity": 4})
    svc.create_entity("ci.automation", "Outcome",
                      "Pipeline Automation Push",
                      properties={"target_maturity": 4})
    from runtime.graph import Edge
    svc.create_relationship("dec.2026-q3", "traces-to",
                            "asm.2026-q3.gap.2000", status="proposed")
    svc.create_relationship("dec.2026-q3", "results-in",
                            "ci.training", status="proposed")
    svc.create_relationship("dec.2026-q3", "results-in",
                            "ci.automation", status="proposed")
    return store, service


def test_engine_summarizes_decision_against_current_graph_state():
    """CR-9 §73: the decision engine summarizes a Decision against the live graph."""
    store, service = _assembled_appraisal()
    engine = DecisionImpactEngine(service)

    evaluation = engine.evaluate_decision("dec.2026-q3")

    assert isinstance(evaluation, DecisionEvaluation)
    assert evaluation.decision_id == "dec.2026-q3"
    assert evaluation.proposed_outcome_ids == ["ci.training", "ci.automation"]
    assert evaluation.proposed_outcome_ids == [
        "ci.training", "ci.automation"]


def test_engine_dependency_paths_returns_explicit_route():
    """CR-9 §73: dependency paths surface for impact analysis."""
    store, service = _assembled_appraisal()
    engine = DecisionImpactEngine(service)

    paths = engine.dependency_paths(start="dec.2026-q3", target="ci.training")

    assert paths, "engine should record at least one path"
    edge_keys = [edge for _, edges in paths for edge in edges]
    assert ("dec.2026-q3", "results-in", "ci.training") in edge_keys


def test_engine_propose_initiatives_creates_change_initiatives_on_graph():
    """CR-9 §74: proposing initiatives creates ChangeInitiative nodes on the graph."""
    store, service = _assembled_appraisal()
    service.delete_entity("ci.training", cascade=True)
    service.delete_entity("ci.automation", cascade=True)
    engine = DecisionImpactEngine(service)

    created = engine.propose_initiatives(
        "dec.2026-q3",
        proposals=[{"id": "ci.embedded", "name": "Embedded Tooling",
                     "target_maturity": 4, "type": "Outcome"}])

    assert created == ["ci.embedded"]
    assert store.has_entity("ci.embedded")
    edge = next(e for e in store.edges_of("dec.2026-q3", direction="out")
                 if e.target == "ci.embedded")
    assert edge.type == "results-in"


def test_engine_avoids_duplicate_initiative_ids():
    """CR-9 §74: re-running the proposal does not duplicate existing initiatives."""
    store, service = _assembled_appraisal()
    engine = DecisionImpactEngine(service)

    created = engine.propose_initiatives(
        "dec.2026-q3",
        proposals=[{"id": "ci.training", "name": "Training",
                     "target_maturity": 4}])

    assert created == []
    assert store.has_entity("ci.training")  # already present, not duplicated


def test_engine_unknown_decision_raises():
    store = InMemoryGraphStore()
    service = RuntimeService(store)
    with pytest.raises(DecisionError, match="unknown decision"):
        DecisionImpactEngine(service).evaluate_decision("dec.nonexistent")
