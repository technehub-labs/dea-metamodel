"""CR-10 Phase 1 — scenario foundation tests.

Covers the Phase-1 slice of the CR-10 Definition of Done:
- Scenario is a first-class OpenDEA concept ✓
- Scenarios use immutable baselines ✓
- Changes are represented as explicit deltas ✓
- Assumptions / constraints are explicit ✓
- Scenario versions are reproducible ✓ (hash stability)
- Scenario immutability after evaluation ✓ (CR-10AG)
"""
import pytest

from runtime.graph import Edge, InMemoryGraphStore, Node
from runtime.scenario import (Assumption, Baseline, Change, ChangeOperation,
                              Constraint, Outcome, Scenario, ScenarioEngine,
                              ScenarioError, ScenarioStatus,
                              ScenarioValidationError, Uncertainty)


@pytest.fixture()
def baseline_store():
    """Current state: capability ← service ← application (CR-10AS pattern)."""
    store = InMemoryGraphStore()
    store.create_entity(Node(id="cap.customer-service", type="BusinessCapability",
                             name="Customer Service"))
    store.create_entity(Node(id="app.customer-platform", type="ApplicationComponent",
                             name="Customer Platform A"))
    store.create_entity(Node(id="tech.hosting", type="Technology",
                             name="Hosting"))
    store.create_relationship(Edge(type="supports", source="app.customer-platform",
                                   target="cap.customer-service", status="active"))
    store.create_relationship(Edge(type="supports", source="tech.hosting",
                                   target="app.customer-platform", status="active"))
    return store


@pytest.fixture()
def engine():
    return ScenarioEngine()


@pytest.fixture()
def baseline(engine, baseline_store):
    return engine.create_baseline(baseline_store, "baseline.2026-q3",
                                  "2026-Q3 Current State", source="example.minimal@1.0.0")


def defined_scenario(**over):
    sc = Scenario(id="scenario.replace-customer-platform",
                  name="Replace Customer Platform",
                  baseline="baseline.2026-q3",
                  owner="architect-42", purpose="CR-10AS canonical example",
                  **over)
    sc.transition(ScenarioStatus.DEFINED)
    return sc


# ---- CR-10A: first-class object + lifecycle ----

def test_scenario_is_first_class():
    sc = defined_scenario()
    d = sc.as_dict()
    assert d["id"] == "scenario.replace-customer-platform"
    assert d["status"] == "defined"
    assert d["baseline"] == "baseline.2026-q3"


def test_lifecycle_transitions_enforced():
    sc = Scenario(id="scenario.x", name="X", baseline="baseline.2026-q3")
    with pytest.raises(ScenarioError, match="illegal lifecycle"):
        sc.transition(ScenarioStatus.EVALUATED)  # skipping states
    sc.transition(ScenarioStatus.DEFINED)
    sc.transition(ScenarioStatus.EVALUATING)
    sc.transition(ScenarioStatus.EVALUATED)
    with pytest.raises(ScenarioError, match="illegal lifecycle"):
        sc.transition(ScenarioStatus.DRAFT)
    sc.transition(ScenarioStatus.REJECTED)


def test_noncanonical_scenario_id_rejected():
    with pytest.raises(ScenarioError, match="canonical"):
        Scenario(id="Replace Platform!", name="X", baseline="b")


# ---- CR-10D/E: assumptions and constraints are explicit objects ----

def test_assumptions_and_constraints_explicit():
    sc = defined_scenario()
    sc.add_assumption(Assumption(id="ASM-001",
                                 statement="Customer migration completes within 12 months",
                                 value=12, unit="months", confidence=0.75,
                                 source="program office", owner="ea-team"))
    sc.add_constraint(Constraint(subject="budget", operator="<=",
                                 value=20_000_000, unit="USD", priority="mandatory"))
    d = sc.as_dict()
    assert d["assumptions"][0]["id"] == "ASM-001"
    assert d["assumptions"][0]["confidence"] == 0.75
    assert d["constraints"][0]["operator"] == "<="


# ---- CR-10B: baseline immutability + simulated-state separation ----

def test_simulation_never_mutates_baseline(engine, baseline_store, baseline):
    sc = defined_scenario()
    sc.add_change(Change(target="app.customer-platform",
                         operation=ChangeOperation.REPLACE,
                         node={"id": "platform.customer-v2",
                               "type": "ApplicationComponent",
                               "name": "Customer Platform B"}))
    before = baseline_store.stats()
    sim = engine.simulate(sc, baseline)
    # baseline store untouched
    assert baseline_store.stats() == before
    assert baseline_store.has_entity("app.customer-platform")
    assert not baseline_store.has_entity("platform.customer-v2")
    # simulated state carries the delta
    assert not sim.has_entity("app.customer-platform")
    assert sim.has_entity("platform.customer-v2")
    # edges rewired to the replacement
    assert [n.id for n in sim.neighbors("platform.customer-v2")] == ["cap.customer-service"]
    assert [n.id for n in sim.neighbors("tech.hosting")] == ["platform.customer-v2"]


def test_scenario_status_after_simulation(engine, baseline):
    sc = defined_scenario()
    sc.add_change(Change(target="app.customer-platform",
                         operation=ChangeOperation.DISABLE))
    engine.simulate(sc, baseline)
    assert sc.status == ScenarioStatus.EVALUATED
    assert sc.frozen


def test_simulate_requires_defined_status(engine, baseline):
    sc = Scenario(id="scenario.draft", name="D", baseline="baseline.2026-q3")
    with pytest.raises(ScenarioError, match="must be DEFINED"):
        engine.simulate(sc, baseline)


# ---- CR-10C: delta operations ----

def test_add_and_connect(engine, baseline):
    sc = defined_scenario()
    sc.add_change(Change(target="agent.service-assistant",
                         operation=ChangeOperation.ADD,
                         node={"type": "Agent", "name": "Service Assistant",
                               "properties": {"authority_ref": "auth.1",
                                              "owner_ref": "person.1"}}))
    sc.add_change(Change(target="agent.service-assistant",
                         operation=ChangeOperation.CONNECT,
                         edge={"type": "uses", "to": "app.customer-platform"}))
    sim = engine.simulate(sc, baseline)
    assert sim.has_entity("agent.service-assistant")
    assert [n.id for n in sim.neighbors("agent.service-assistant")] == ["app.customer-platform"]


def test_modify_reclassify_move_scale(engine, baseline):
    sc = defined_scenario()
    sc.add_change(Change(target="app.customer-platform",
                         operation=ChangeOperation.MODIFY,
                         set={"properties": {"criticality": "high"}}))
    sc.add_change(Change(target="app.customer-platform",
                         operation=ChangeOperation.SCALE, set={"scale": 3}))
    sc.add_change(Change(target="tech.hosting",
                         operation=ChangeOperation.MOVE,
                         edge={"type": "supports",
                               "from": "app.customer-platform",
                               "to": "cap.customer-service"}))
    sim = engine.simulate(sc, baseline)
    node = sim.get_entity("app.customer-platform")
    assert node.properties["criticality"] == "high"
    assert node.properties["scale"] == 3
    assert [n.id for n in sim.neighbors("tech.hosting")] == ["cap.customer-service"]


def test_remove_and_disconnect(engine, baseline):
    sc = defined_scenario()
    sc.add_change(Change(target="tech.hosting",
                         operation=ChangeOperation.DISCONNECT,
                         edge={"type": "supports", "to": "app.customer-platform"}))
    sc.add_change(Change(target="tech.hosting", operation=ChangeOperation.REMOVE))
    sim = engine.simulate(sc, baseline)
    assert not sim.has_entity("tech.hosting")
    assert sim.has_entity("app.customer-platform")


# ---- validation ----

def test_invalid_delta_rejected_and_not_applied(engine, baseline):
    sc = defined_scenario()
    sc.add_change(Change(target="app.nonexistent", operation=ChangeOperation.REMOVE))
    with pytest.raises(ScenarioValidationError, match="not present"):
        engine.simulate(sc, baseline)
    assert sc.status == ScenarioStatus.DEFINED  # not advanced on failure


def test_unknown_type_and_relationship_rejected(engine, baseline):
    sc = defined_scenario()
    sc.add_change(Change(target="x.y", operation=ChangeOperation.ADD,
                         node={"type": "NotAType", "name": "X"}))
    with pytest.raises(ScenarioValidationError, match="DEA-E001"):
        engine.simulate(sc, baseline)


def test_wrong_baseline_rejected(engine, baseline):
    sc = Scenario(id="scenario.wrong", name="W", baseline="baseline.other")
    sc.transition(ScenarioStatus.DEFINED)
    with pytest.raises(ScenarioValidationError, match="references baseline"):
        engine.simulate(sc, baseline)


# ---- CR-10AG: evaluated scenarios are immutable; change = new version ----

def test_evaluated_scenario_is_frozen(engine, baseline):
    sc = defined_scenario()
    sc.add_change(Change(target="app.customer-platform",
                         operation=ChangeOperation.DISABLE))
    engine.simulate(sc, baseline)
    with pytest.raises(ScenarioError, match="frozen"):
        sc.add_change(Change(target="x.y", operation=ChangeOperation.REMOVE))


def test_new_version_supersedes(engine, baseline):
    sc = defined_scenario()
    sc.add_change(Change(target="app.customer-platform",
                         operation=ChangeOperation.DISABLE))
    engine.simulate(sc, baseline)
    v2 = sc.new_version()
    assert v2.version == 2 and not v2.frozen
    assert v2.status == ScenarioStatus.DRAFT
    assert v2.provenance["supersedes"] == f"{sc.id}@v1"
    assert sc.status == ScenarioStatus.SUPERSEDED
    v2.add_change(Change(target="tech.hosting", operation=ChangeOperation.REMOVE))


# ---- CR-10AF: reproducibility ----

def test_reproducibility_hash_stable():
    def build():
        sc = Scenario(id="scenario.hash", name="H", baseline="baseline.2026-q3")
        sc.add_change(Change(target="app.customer-platform",
                             operation=ChangeOperation.REPLACE,
                             node={"id": "platform.customer-v2",
                                   "type": "ApplicationComponent", "name": "B"}))
        sc.add_assumption(Assumption(id="ASM-001", statement="s", value=12,
                                     unit="months", confidence=0.75))
        return sc.reproducibility_hash()
    assert build() == build()


def test_hash_changes_with_definition():
    a = Scenario(id="scenario.hash", name="H", baseline="baseline.2026-q3")
    b = Scenario(id="scenario.hash", name="H", baseline="baseline.2026-q3")
    b.add_change(Change(target="x.y", operation=ChangeOperation.REMOVE))
    assert a.reproducibility_hash() != b.reproducibility_hash()


# ---- CR-10I/O: outcomes carry uncertainty ----

def test_outcomes_carry_uncertainty():
    o = Outcome(metric="customer wait time", baseline=8, expected=4.5,
                target=5, unit="min", confidence=0.82,
                uncertainty=Uncertainty.ESTIMATED, timeframe="12 months")
    d = o.as_dict()
    assert d["uncertainty"] == "estimated"
    assert d["expected"] == 4.5 and d["target"] == 5


def test_affected_entities_derived():
    sc = defined_scenario()
    sc.add_change(Change(target="app.customer-platform",
                         operation=ChangeOperation.REPLACE,
                         node={"id": "platform.customer-v2",
                               "type": "ApplicationComponent", "name": "B"}))
    assert sc.affected_entities == ["app.customer-platform", "platform.customer-v2"]
