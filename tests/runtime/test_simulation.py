"""CR-10 Phase 5 — SimulationAdapter tests."""
from pathlib import Path

import pytest

from runtime.api import RuntimeService
from runtime.graph import InMemoryGraphStore
from runtime.model import load_model
from runtime.scenario import ScenarioEngine, ScenarioStatus, load_scenario
from runtime.simulation import (SimulationAdapter, SimulationError,
                                  SimulationRegistry, SimulationRequest,
                                  SimulationResult, ScenarioImpactAdapter)

from conftest import BASE


def _scenario_paths():
    return {
        "scenario.replace-customer-platform": str(
            BASE / "models" / "scenarios" / "customer-platform-replacement.yaml"),
    }


def _runtime():
    service = RuntimeService(InMemoryGraphStore())
    load_model(BASE / "models" / "scenarios" / "customer-service-baseline.yaml",
               service.store)
    return service


def _adapter(service):
    return ScenarioImpactAdapter(service, scenarios=_scenario_paths())


def test_simulation_adapter_is_abstract():
    with pytest.raises(TypeError):
        SimulationAdapter()


def test_scenario_impact_adapter_implements_lifecycle():
    service = _runtime()
    engine = ScenarioEngine()
    baseline = engine.create_baseline(service.store, "baseline.adapter",
                                      "Adapter Baseline")
    adapter = _adapter(service)

    request = SimulationRequest(
        id="sim.1", scenario_id="scenario.replace-customer-platform",
        baseline_id="baseline.adapter",
        engine="scenario-impact", engine_version="1.0.0",
        parameters={"key": "value"}, assumptions=(),
        timestamp="2026-08-19T00:00:00Z")
    prepared = adapter.prepare(request)
    executed = adapter.execute(prepared)
    result = adapter.retrieve_results(executed)
    mapped = adapter.map_results(result, service)
    adapter.validate(mapped)

    assert prepared.request is request
    assert executed.prepared is prepared
    assert result.executed is executed
    assert mapped.scenario_id == "scenario.replace-customer-platform"
    assert "platform.customer-v2" in mapped.added_entities


def test_scenario_impact_adapter_rejects_engine_mismatch():
    service = _runtime()
    adapter = _adapter(service)
    request = SimulationRequest(
        id="sim.2", scenario_id="scenario.replace-customer-platform",
        baseline_id="baseline.adapter",
        engine="monte-carlo", engine_version="1.0.0",
        parameters={}, assumptions=(),
        timestamp="2026-08-19T00:00:00Z")
    with pytest.raises(SimulationError, match="engine"):
        adapter.prepare(request)


def test_simulation_registry_dispatches_by_capability():
    service = _runtime()
    registry = SimulationRegistry()
    registry.register(_adapter(service))

    engine = registry.engine_for("scenario-impact")
    assert engine is not None

    with pytest.raises(SimulationError, match="no adapter"):
        registry.engine_for("monte-carlo")


def test_simulation_registry_publishes_registered_capabilities():
    service = _runtime()
    registry = SimulationRegistry()
    registry.register(_adapter(service))

    capabilities = sorted(registry.capabilities())
    assert "scenario-impact" in capabilities


def test_simulation_request_preserves_reproducibility_metadata():
    request = SimulationRequest(
        id="sim.3", scenario_id="asm.x", baseline_id="baseline.x",
        engine="scenario-impact", engine_version="1.0.0",
        parameters={"deg": 1}, assumptions=("customer-stable",),
        timestamp="2026-08-19T00:00:00Z")
    rep = request.as_dict()
    assert rep["engine"] == "scenario-impact"
    assert rep["engineVersion"] == "1.0.0"
    assert rep["assumptions"] == ["customer-stable"]
    assert rep["parameters"] == {"deg": 1}
