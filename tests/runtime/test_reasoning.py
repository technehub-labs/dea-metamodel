"""CR-9.3 — semantic reasoning tests (CR-9Q/R/S/T)."""

import pytest

from runtime.api import RuntimeService
from runtime.graph import InMemoryGraphStore
from runtime.provenance import AssertionStatus, ProvenanceService
from runtime.reasoning import (ReasoningEngine, ReasoningError, ReasoningLevel,
                               Rule, RuleMatch, RuleRegistry, RuleSeverity)


def test_rule_registry_stores_governed_rule_metadata():
    """CR-9S: rules are versioned, enabled, profile-scoped and traceable."""
    rule = Rule(
        id="DEA-INF-007",
        name="StrategicCapabilityFromStrategicObjective",
        level=ReasoningLevel.DETERMINISTIC,
        applies_to=["BusinessCapability"],
        condition=lambda store: [],
        version="1.0.0",
        profile="dea:core",
        severity=RuleSeverity.ERROR,
        description="Capability enabling a strategic objective is strategic",
    )
    registry = RuleRegistry()
    registry.register(rule)

    loaded = registry.get("DEA-INF-007")
    assert loaded.version == "1.0.0"
    assert loaded.enabled is True
    assert loaded.profile == "dea:core"
    assert loaded.severity == RuleSeverity.ERROR
    assert registry.rules_for(profile="dea:core") == [rule]
    assert registry.rules_for(profile="dea:assessment") == []


def test_disabled_rules_are_not_returned_for_evaluation():
    registry = RuleRegistry()
    rule = Rule(
        id="DEA-INF-008", name="Disabled", level=ReasoningLevel.GRAPH,
        applies_to=["BusinessCapability"], condition=lambda store: [],
        enabled=False)
    registry.register(rule)

    assert registry.enabled_rules() == []


def _strategic_rule():
    def condition(store):
        for capability in store.query(type="BusinessCapability"):
            for edge in store.edges_of(capability.id, direction="out",
                                       rel_type="enables"):
                objective = store.get_entity(edge.target)
                if objective.type == "StrategicObjective":
                    yield RuleMatch(
                        subject=capability.id,
                        claim={"classification": "strategic"},
                        derived_from=[capability.id, objective.id],
                        confidence=0.96,
                        explanation=[
                            f"{capability.id} enables {objective.id}",
                            f"{objective.id} is a StrategicObjective",
                        ])
    return Rule(
        id="DEA-INF-007",
        name="StrategicCapabilityFromStrategicObjective",
        level=ReasoningLevel.DETERMINISTIC,
        applies_to=["BusinessCapability"],
        condition=condition,
        version="1.0.0",
        profile="dea:core")


def _strategic_store():
    store = InMemoryGraphStore()
    svc = RuntimeService(store)
    svc.create_entity("cap.customer-service", "BusinessCapability", "Customer Service")
    svc.create_entity("obj.customer-experience", "StrategicObjective", "Customer Experience")
    svc.create_relationship("cap.customer-service", "enables",
                            "obj.customer-experience", status="active")
    return store


def test_deterministic_rule_evaluates_without_mutating_graph():
    """CR-9Q/CQ: evaluation derives candidates; it does not silently assert."""
    store = _strategic_store()
    before = store.stats()
    inferences = ReasoningEngine().infer(_strategic_rule(), store)

    assert len(inferences) == 1
    inference = inferences[0]
    assert inference.subject == "cap.customer-service"
    assert inference.claim == {"classification": "strategic"}
    assert inference.rule_id == "DEA-INF-007"
    assert inference.level == ReasoningLevel.DETERMINISTIC
    assert inference.confidence == 0.96
    assert store.stats() == before  # no silent materialization


def test_inference_explainability_answers_why():
    """CR-9T: every derived result exposes conclusion → rule → support → confidence."""
    inference = ReasoningEngine().infer(_strategic_rule(), _strategic_store())[0]
    explanation = ReasoningEngine().explain(inference)

    assert explanation["conclusion"]["subject"] == "cap.customer-service"
    assert explanation["rule"]["id"] == "DEA-INF-007"
    assert explanation["level"] == 1
    assert explanation["confidence"] == 0.96
    assert explanation["because"] == [
        "cap.customer-service enables obj.customer-experience",
        "obj.customer-experience is a StrategicObjective",
    ]


def test_materialized_inference_becomes_proposed_assertion_with_provenance():
    """CR-9T/CQ: materialization is explicit and lands as PROPOSED, never approved."""
    store = _strategic_store()
    inference = ReasoningEngine().infer(_strategic_rule(), store)[0]
    provenance = ProvenanceService(store)

    assertion_id = ReasoningEngine().materialize(inference, provenance)
    assertion = provenance.assertions_for("cap.customer-service")[0]

    assert assertion.id == assertion_id
    assert assertion.status == AssertionStatus.PROPOSED
    assert assertion.claim == {"classification": "strategic"}
    assert assertion.derived_from == [
        "cap.customer-service", "obj.customer-experience"]
    assert assertion.derivation_rule == "DEA-INF-007"
    node = store.get_entity(assertion_id)
    assert node.properties["reasoning_level"] == 1
    chain = provenance.why("cap.customer-service")
    assert [a.id for a in chain.assertions] == [assertion_id]


def test_reasoning_level_is_recorded_never_blended():
    """CR-9R: deterministic and graph inference keep their own levels."""
    graph_rule = Rule(
        id="DEA-INF-009", name="GraphPathImpact", level=ReasoningLevel.GRAPH,
        applies_to=["BusinessCapability"],
        condition=lambda store: [RuleMatch(
            subject="cap.customer-service", claim={"impact_path": True},
            derived_from=["cap.customer-service"], confidence=0.8)])
    inference = ReasoningEngine().infer(graph_rule, _strategic_store())[0]

    assert inference.level == ReasoningLevel.GRAPH
    assert inference.as_dict()["level"] == 3


def test_rule_applies_to_is_enforced():
    """CR-9S: a rule cannot derive facts outside its declared scope."""
    rule = Rule(
        id="DEA-INF-010", name="WrongScope", level=ReasoningLevel.DETERMINISTIC,
        applies_to=["ApplicationComponent"],
        condition=lambda store: [RuleMatch(
            subject="cap.customer-service", claim={"x": 1})])

    with pytest.raises(ReasoningError, match="applies to"):
        ReasoningEngine().infer(rule, _strategic_store())
