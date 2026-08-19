"""CR-9.10b — interop and performance suite tests."""

import time

from runtime.api import RuntimeService
from runtime.conformance import (ConformanceClass, ConformanceSuite,
                                INTEROP_SCENARIOS, PerformanceSuite,
                                run_interop_scenario)
from runtime.graph import InMemoryGraphStore
from runtime.interoperability import (ExternalIdentifier, ExternalSystem,
                                      InteropRegistry, SemanticMapping)
from runtime.model import load_model
from runtime.provenance import AssertionStatus, ProvenanceService
from runtime.reasoning import (ReasoningEngine, ReasoningLevel, Rule, RuleMatch)
from runtime.scenario import (ScenarioEngine, ScenarioStatus, load_scenario)
from runtime.scenario.impact import ImpactEngine

from conftest import BASE


def test_interop_scenarios_are_catalogued_with_classes():
    classes = {tuple(s.classes) for s in INTEROP_SCENARIOS}
    assert classes  # non-empty
    for scenario in INTEROP_SCENARIOS:
        assert scenario.classes, (
            f"interop scenario {scenario.name!r} declares no classes")


def test_interop_scenarios_pass_on_reference_runtime():
    for scenario in INTEROP_SCENARIOS:
        report = run_interop_scenario(scenario)
        assert report["scenario"] == scenario.name
        assert report["passed"], report


def test_external_id_correlation_round_trip():
    registry = InteropRegistry()
    registry.register_system(ExternalSystem(
        id="system.servicenow", name="ServiceNow CMDB", type="CMDB"))
    registry.register_system(ExternalSystem(
        id="system.leanix", name="LeanIX", type="EA_REPOSITORY"))
    registry.register_mapping(SemanticMapping(
        source_concept="external:archimate.ApplicationComponent",
        target_concept="opendea:ApplicationComponent"))
    service = RuntimeService(InMemoryGraphStore())
    service.create_entity("app.customer-platform",
                          "ApplicationComponent", "CS Platform")
    registry.link_external_identifier(ExternalIdentifier(
        system="system.servicenow", identifier="CI-001",
        entity="app.customer-platform"))
    assert registry.resolve("system.servicenow", "CI-001") == "app.customer-platform"


def test_reasoning_materialization_lands_as_proposed_assertion():
    store = InMemoryGraphStore()
    service = RuntimeService(store)
    service.create_entity("cap.cs", "BusinessCapability", "Capability")
    service.create_entity("obj.cs", "StrategicObjective", "Objective")
    service.create_relationship("cap.cs", "enables", "obj.cs", status="active")
    provenance = ProvenanceService(store)

    rule = Rule(
        id="DEA-INF-007", name="StrategicCapability",
        level=ReasoningLevel.DETERMINISTIC,
        applies_to=["BusinessCapability"],
        condition=lambda store: [
            RuleMatch(subject="cap.cs", claim={"classification": "strategic"},
                      derived_from=["cap.cs", "obj.cs"], confidence=0.96)])
    inference = ReasoningEngine().infer(rule, store)[0]
    assertion_id = ReasoningEngine().materialize(inference, provenance)
    assertion = provenance.assertions_for("cap.cs")[0]
    assert assertion.id == assertion_id
    assert assertion.status == AssertionStatus.PROPOSED
    assert assertion.derivation_rule == "DEA-INF-007"


def test_performance_suite_meets_engineering_targets():
    for spec in PerformanceSuite.SPECS:
        result = PerformanceSuite(spec).run()
        assert result.passed, result.as_dict()
        assert result.nodes == spec.nodes
        assert result.edges_loaded >= spec.nodes


def test_conformance_classes_are_covered_by_full_suite_catalog():
    interop = ConformanceSuite(
        name="interop",
        classes=[ConformanceClass.API, ConformanceClass.VALIDATION,
                 ConformanceClass.PROVENANCE],
        description="Interoperability end-to-end scenarios (CR-9CM)")
    performance = ConformanceSuite(
        name="performance",
        classes=[ConformanceClass.QUERY],
        description="Performance engineering targets (CR-9CJ/CK)")
    covered = {c.value for s in (interop, performance) for c in s.classes}
    assert covered == {"API", "Query", "Validation", "Provenance"}
