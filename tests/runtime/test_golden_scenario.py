"""CR-10AS — the golden scenario end-to-end (structural level).

Should the enterprise replace the existing customer-service platform?
Baseline: the CR-8 golden enterprise model. Scenario: REPLACE Application A
with Platform B. Phase-1 verification: delta applies, baseline untouched,
capability support rewired, assumptions/constraints/outcomes explicit,
reproducible.
"""
import pytest

from runtime.graph import InMemoryGraphStore
from runtime.model import load_model
from runtime.scenario import (ScenarioEngine, ScenarioStatus, load_scenario)

from conftest import BASE

SCENARIO_PATH = BASE / "models" / "scenarios" / "customer-platform-replacement.yaml"
BASELINE_MODEL = BASE / "models" / "scenarios" / "customer-service-baseline.yaml"


@pytest.fixture()
def evaluated():
    store = InMemoryGraphStore()
    load_model(BASELINE_MODEL, store)
    engine = ScenarioEngine()
    baseline = engine.create_baseline(store, "baseline.customer-service",
                                      "Customer-Service Current State",
                                      source="scenarios/customer-service-baseline.yaml")
    scenario = load_scenario(str(SCENARIO_PATH))
    scenario.transition(ScenarioStatus.DEFINED)
    sim = engine.simulate(scenario, baseline)
    return store, baseline, scenario, sim


def test_golden_scenario_file_is_wellformed():
    sc = load_scenario(str(SCENARIO_PATH))
    assert sc.id == "scenario.replace-customer-platform"
    assert len(sc.assumptions) == 2
    assert len(sc.constraints) == 3
    assert len(sc.expected_outcomes) == 3
    assert [c.operator for c in sc.constraints] == ["<=", "<=", ">="]


def test_golden_scenario_applies(evaluated):
    store, baseline, scenario, sim = evaluated
    assert scenario.status == ScenarioStatus.EVALUATED
    assert scenario.frozen
    # simulated state: Platform B present, Application A gone, support rewired
    assert sim.has_entity("platform.customer-v2")
    assert not sim.has_entity("app.customer-platform")
    supported = {n.id for n in sim.neighbors("platform.customer-v2")}
    assert "cap.customer-service" in supported


def test_baseline_untouched(evaluated):
    store, baseline, scenario, sim = evaluated
    assert store.has_entity("app.customer-platform")
    assert not store.has_entity("platform.customer-v2")
