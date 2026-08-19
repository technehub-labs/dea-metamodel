"""CR-10 Phase 2 — impact engine tests (CR-10G/H + Phase 2 scope)."""

from runtime.api import RuntimeService
from runtime.graph import InMemoryGraphStore
from runtime.model import load_model
from runtime.scenario import (ChangeOperation, ScenarioEngine, ScenarioStatus,
                              load_scenario)
from runtime.scenario.impact import (ImpactEngine, ImpactValence,
                                     architecture_delta)
from conftest import BASE


def test_impact_engine_is_exported_from_scenario_package():
    from runtime.scenario import ImpactEngine as ExportedImpactEngine
    assert ExportedImpactEngine is ImpactEngine


def test_architecture_delta_detects_entity_and_edge_changes():
    """CR-10 Phase 2: architecture delta compares before/after graph states."""
    before = {
        "nodes": [
            {"id": "app.old", "type": "ApplicationComponent", "name": "Old"},
            {"id": "cap.a", "type": "BusinessCapability", "name": "A"},
        ],
        "edges": [
            {"type": "supports", "source": "app.old", "target": "cap.a"},
        ],
    }
    after = {
        "nodes": [
            {"id": "app.new", "type": "ApplicationComponent", "name": "New"},
            {"id": "cap.a", "type": "BusinessCapability", "name": "A",
             "properties": {"criticality": "high"}},
        ],
        "edges": [
            {"type": "supports", "source": "app.new", "target": "cap.a"},
            {"type": "enables", "source": "cap.a", "target": "obj.a"},
        ],
    }

    delta = architecture_delta(before, after)

    assert delta.added_entities == ["app.new"]
    assert delta.removed_entities == ["app.old"]
    assert delta.modified_entities == ["cap.a"]
    assert delta.added_edges == [
        ("app.new", "supports", "cap.a"),
        ("cap.a", "enables", "obj.a"),
    ]
    assert delta.removed_edges == [("app.old", "supports", "cap.a")]


def _dependency_store():
    store = InMemoryGraphStore()
    svc = RuntimeService(store)
    svc.create_entity("app.a", "ApplicationComponent", "App")
    svc.create_entity("cap.a", "BusinessCapability", "Capability")
    svc.create_entity("obj.a", "StrategicObjective", "Objective")
    svc.create_relationship("app.a", "supports", "cap.a", status="active")
    svc.create_relationship("cap.a", "enables", "obj.a", status="active")
    return store


def test_dependency_propagation_marks_direct_and_indirect_impact():
    """CR-10G: impact graph records dependency paths and depth."""
    impacts = ImpactEngine().propagate(
        _dependency_store(), ["app.a"], operation=ChangeOperation.REMOVE)
    by_id = {i.entity: i for i in impacts}

    assert by_id["cap.a"].direct is True
    assert by_id["cap.a"].depth == 1
    assert by_id["cap.a"].category.value == "capability"
    assert by_id["cap.a"].path == [("app.a", "supports", "cap.a")]
    assert by_id["obj.a"].direct is False
    assert by_id["obj.a"].depth == 2
    assert by_id["obj.a"].category.value == "strategic"
    assert by_id["obj.a"].path == [
        ("app.a", "supports", "cap.a"),
        ("cap.a", "enables", "obj.a"),
    ]


def test_impact_valence_is_explicit_and_configurable():
    """CR-10H: affected does not automatically mean negative impact."""
    store = _dependency_store()
    default = ImpactEngine().propagate(
        store, ["app.a"], operation=ChangeOperation.REMOVE)
    assert {i.valence for i in default} == {ImpactValence.UNKNOWN}

    engine = ImpactEngine(valence_rules={
        (ChangeOperation.REMOVE, "BusinessCapability"): ImpactValence.NEGATIVE,
        (ChangeOperation.REMOVE, "StrategicObjective"): ImpactValence.MIXED,
    })
    impacts = engine.propagate(store, ["app.a"], operation=ChangeOperation.REMOVE)
    by_id = {i.entity: i for i in impacts}
    assert by_id["cap.a"].valence == ImpactValence.NEGATIVE
    assert by_id["obj.a"].valence == ImpactValence.MIXED


def test_golden_scenario_impact_report():
    """CR-10AS/Phase 2: impact graph + change analysis + architecture delta."""
    store = InMemoryGraphStore()
    load_model(BASE / "models" / "scenarios" / "customer-service-baseline.yaml", store)
    scenario_engine = ScenarioEngine()
    baseline = scenario_engine.create_baseline(
        store, "baseline.customer-service", "Customer-Service Current State")
    scenario = load_scenario(str(
        BASE / "models" / "scenarios" / "customer-platform-replacement.yaml"))
    scenario.transition(ScenarioStatus.DEFINED)

    report = ImpactEngine().evaluate(scenario, baseline)

    assert scenario.status == ScenarioStatus.EVALUATED
    assert report.delta.added_entities == ["platform.customer-v2"]
    assert report.delta.removed_entities == ["app.customer-platform"]
    assert report.changes[0].operation == ChangeOperation.REPLACE
    assert report.changes[0].added == ["platform.customer-v2"]
    assert report.changes[0].removed == ["app.customer-platform"]
    impacted = {i.entity: i for i in report.impacts}
    assert impacted["cap.customer-service"].direct is True
    assert impacted["cap.customer-service"].category.value == "capability"
    assert impacted["tech.hosting"].direct is True
    assert impacted["tech.hosting"].category.value == "technology"
    assert {i.valence for i in report.impacts} == {ImpactValence.UNKNOWN}
