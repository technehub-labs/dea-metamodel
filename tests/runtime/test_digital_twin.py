"""CR-10 Phase 7 — Digital Twin Foundation tests."""
import pytest

from runtime.api import RuntimeService
from runtime.graph import Edge, InMemoryGraphStore, Node
from runtime.twin import (DigitalTwin, ObservationError, ObservationEvent,
                           OperationalState, StateDiff)


def _runtime():
    service = RuntimeService(InMemoryGraphStore())
    service.create_entity("app.cs", "ApplicationComponent", "CS Platform", lifecycle_status="active")
    service.create_entity("app.retired", "ApplicationComponent", "Retired App")
    return service


def test_digital_twin_observation_records_event():
    service = _runtime()
    twin = DigitalTwin(service)

    event = twin.observe(
        subject="app.cs", observed_state="running", at="2026-08-19T00:00:00Z")

    assert isinstance(event, ObservationEvent)
    assert event.subject == "app.cs"
    assert event.observed_state == "running"
    assert any(ev.id == event.id for ev in twin.observation_log())


def test_current_state_returns_latest_observation():
    service = _runtime()
    twin = DigitalTwin(service)

    twin.observe("app.cs", "starting", at="2026-08-19T00:00:00Z")
    twin.observe("app.cs", "running", at="2026-08-19T01:00:00Z")
    twin.observe("app.cs", "degraded", at="2026-08-19T02:00:00Z")

    current = twin.current_state("app.cs")
    assert isinstance(current, OperationalState)
    assert current.state == "degraded"
    assert current.observed_at == "2026-08-19T02:00:00Z"


def test_observation_distinguishes_architecture_from_observed_state():
    service = _runtime()
    twin = DigitalTwin(service)

    observed = twin.observe("app.cs", "running", at="2026-08-19T00:00:00Z")
    assert observed.subject == "app.cs"
    assert observed.observed_state == "running"
    current = twin.current_state("app.cs")
    assert current.state == "running"
    assert current.state_role == "current"
    assert service.store.get_entity("app.cs").lifecycle_status == "active"


def test_observation_stores_audit_event_on_graph():
    service = _runtime()
    twin = DigitalTwin(service)

    twin.observe("app.cs", "running", at="2026-08-19T00:00:00Z")

    audit_edges = [e for e in service.store.edges_of("app.cs", direction="both")
                   if e.type == "traces-to"]
    assert any(e.source == "app.cs" and e.target.startswith("tw.observation.")
                for e in audit_edges)


def test_state_diff_returns_drift_signals():
    service = _runtime()
    twin = DigitalTwin(service)

    twin.observe("app.cs", "running", at="2026-08-19T00:00:00Z")
    twin.observe("app.cs", "degraded", at="2026-08-19T01:00:00Z")

    diff = twin.state_diff("app.cs")
    assert isinstance(diff, StateDiff)
    assert diff.observed_state == "degraded"
    assert diff.architecture_state == "active"
    assert "drift" in diff.signals or diff.drift_detected is True


def test_unknown_subject_raises():
    service = _runtime()
    twin = DigitalTwin(service)
    with pytest.raises(ObservationError, match="unknown subject"):
        twin.observe("ghost", "running", at="2026-08-19T00:00:00Z")
