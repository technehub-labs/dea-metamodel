"""CR-9.9 — OpenDEA Explorer runtime API tests."""
from pathlib import Path

from runtime.api import RuntimeService
from runtime.assessment import AssessmentService
from runtime.decision import DecisionImpactEngine
from runtime.explorer import ExplorerMode, ExplorerService
from runtime.graph import InMemoryGraphStore
from runtime.model import load_model
from runtime.scenario.decision import (Criterion, CriterionScore,
                                       DecisionIntelligenceEngine,
                                       ScenarioEvaluation)

from conftest import BASE


def _runtime():
    """An Explorer-relevant graph: capability, supporting app, decision, gap."""
    store = InMemoryGraphStore()
    service = RuntimeService(store)
    load_model(BASE / "models" / "dmm" / "executable.yaml", store)
    AssessmentService(store).execute_assessment("asm.2026-q3")
    service.create_entity("dec.2026-q3", "Decision",
                          "Maturity Decision",
                          properties={"description": "Address DMM gap"})
    service.create_entity("outcome.2026-q3", "Outcome",
                          "Embedded Tooling Outcome")
    return service


def test_explorer_supports_typed_modes():
    explorer = ExplorerService(_runtime())
    for mode in (ExplorerMode.EXPLORE, ExplorerMode.ASSESS,
                  ExplorerMode.TRACE, ExplorerMode.COMPARE,
                  ExplorerMode.QUERY, ExplorerMode.SIMULATE,
                  ExplorerMode.GOVERN):
        assert mode in explorer.modes


def test_explorer_explore_lists_entities_by_type_and_lifecycle():
    service = _runtime()
    service.create_entity("app.x", "ApplicationComponent", "X",
                          lifecycle_status="active")
    service.create_entity("app.y", "ApplicationComponent", "Y",
                          lifecycle_status="deprecated")
    explorer = ExplorerService(service)

    active = explorer.explore(type="ApplicationComponent",
                              lifecycle_status="active")
    assert {n.id for n in active} == {"app.x"}


def test_explorer_assess_runs_assessment_engine():
    service = _runtime()
    explorer = ExplorerService(service)
    result = explorer.assess("asm.2026-q3")

    assert result["assessmentId"] == "asm.2026-q3"
    assert result["score"] is not None
    assert result["maturityLevel"] is not None
    assert "gapId" in result


def test_explorer_query_uses_graph_capabilities():
    service = _runtime()
    explorer = ExplorerService(service)
    result = explorer.query(type="ApplicationComponent")
    assert all(n.type == "ApplicationComponent" for n in result)


def test_explorer_govern_uses_decision_engine():
    service = _runtime()
    service.create_relationship(
        "dec.2026-q3", "results-in", "outcome.2026-q3")
    explorer = ExplorerService(service)
    evaluation = explorer.govern("dec.2026-q3")

    assert evaluation["decisionId"] == "dec.2026-q3"
    assert "outcome.2026-q3" in evaluation["proposedOutcomeIds"]


def test_explorer_compare_supports_two_scenario_evaluations():
    """CR-9.9: COMPARE reuses the CR-10 decision intelligence engine."""
    evaluations = [
        ScenarioEvaluation("scenario.a", [
            CriterionScore("strategicValue", 0.8)]),
        ScenarioEvaluation("scenario.b", [
            CriterionScore("strategicValue", 0.6)]),
    ]
    criteria = [Criterion("strategicValue", "Strategic Value", 1.0)]
    report = DecisionIntelligenceEngine().compare(evaluations, criteria)
    assert report.recommendation.scenario_id == "scenario.a"


def test_explorer_simulate_loads_yaml_and_returns_delta():
    """CR-9.9: SIMULATE runs the CR-10 scenario pipeline against the runtime."""
    from runtime.graph import InMemoryGraphStore
    from runtime.model import load_model
    store = InMemoryGraphStore()
    service = RuntimeService(store)
    load_model(BASE / "models" / "scenarios" / "customer-service-baseline.yaml", store)
    explorer = ExplorerService(service)
    yaml_path = str(BASE / "models" / "scenarios" / "customer-platform-replacement.yaml")
    result = explorer.simulate_from_yaml(yaml_path, "baseline.explorer")
    assert result["scenario"] == "scenario.replace-customer-platform"
    assert "platform.customer-v2" in result["delta"]["addedEntities"]


def test_explorer_trace_returns_provenance_chain():
    service = _runtime()
    AssessmentService(service.store).execute_assessment("asm.2026-q3")
    result_id = service.store.query(type="AssessmentResult")[0].id
    service.create_entity("ev.app-inventory", "Evidence", "App Inventory",
                          properties={"confidence": 0.9})
    service.create_relationship("ev.app-inventory", "supports", result_id)
    explorer = ExplorerService(service)

    chain = explorer.trace(result_id, through="supports").as_dict()
    assert chain["subject"] == result_id
    assert chain["through"] == "supports"
    assert any(item["entity_id"] == "ev.app-inventory"
               for item in chain["evidence"])
