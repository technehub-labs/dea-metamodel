"""CR-9.4 — temporal queries, events, snapshots, drift detection."""

import pytest

from runtime.graph import Edge, InMemoryGraphStore, Node
from runtime.temporal import (Event, EventLog, EventType, Snapshot,
                              SnapshotDelta, as_of, diff_snapshots,
                              snapshot_graph, what_is_true_now)


def test_what_is_true_now_filters_out_retired_and_planned():
    """CR-9F + CR-6 §22: planned edges never read as current; retired never read at all."""
    store = InMemoryGraphStore()
    store.create_entity(Node(id="cap.a", type="BusinessCapability", name="Capability"))
    store.create_entity(Node(id="svc.planned", type="BusinessService", name="Planned"))
    store.create_entity(Node(id="svc.retired", type="BusinessService", name="Retired"))
    store.create_entity(Node(id="svc.active", type="BusinessService", name="Active"))

    store.create_relationship(Edge(type="supports", source="svc.planned",
                                   target="cap.a", status="planned"))
    store.create_relationship(Edge(type="supports", source="svc.retired",
                                   target="cap.a", status="retired"))
    store.create_relationship(Edge(type="supports", source="svc.active",
                                   target="cap.a", status="active"))

    current = {n.id for n in what_is_true_now(store, "cap.a")}

    assert current == {"svc.active"}


def test_temporal_query_at_instant_returns_only_active_edges():
    store = InMemoryGraphStore()
    store.create_entity(Node(id="cap.a", type="BusinessCapability", name="Capability"))
    store.create_entity(Node(id="svc.past", type="BusinessService", name="Past"))
    store.create_entity(Node(id="svc.now", type="BusinessService", name="Now"))
    store.create_entity(Node(id="svc.future", type="BusinessService", name="Future"))

    store.create_relationship(Edge(type="supports", source="svc.past",
                                   target="cap.a",
                                   valid_from="2024-01-01T00:00:00Z",
                                   valid_to="2025-12-31T00:00:00Z",
                                   status="active"))
    store.create_relationship(Edge(type="supports", source="svc.now",
                                   target="cap.a",
                                   valid_from="2026-01-01T00:00:00Z",
                                   status="active"))
    store.create_relationship(Edge(type="supports", source="svc.future",
                                   target="cap.a",
                                   valid_from="2027-01-01T00:00:00Z",
                                   status="active"))

    yesterday = {n.id for n in store.neighbors("cap.a", direction="in", at="2024-06-01T00:00:00Z")}
    today = {n.id for n in store.neighbors("cap.a", direction="in", at="2026-06-01T00:00:00Z")}
    next_year = {n.id for n in store.neighbors("cap.a", direction="in", at="2027-06-01T00:00:00Z")}

    assert yesterday == {"svc.past"}
    assert today == {"svc.now"}
    assert next_year == {"svc.now", "svc.future"}


def test_bitemporal_as_of_respects_valid_and_transaction_time():
    """CR-9G: 'what was true at T, as we knew it at RT'."""
    store = InMemoryGraphStore()
    store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
    store.create_entity(Node(id="svc.fix", type="BusinessService", name="Fix"))
    store.create_relationship(
        Edge(type="supports", source="svc.fix", target="cap.a",
             valid_from="2026-01-01T00:00:00Z",
             valid_to="2027-01-01T00:00:00Z",
             status="active",
             properties={"recorded_at": "2026-08-01T00:00:00Z"}))

    def active(valid_at, recorded_at=None):
        kwargs = {"valid_at": valid_at}
        if recorded_at is not None:
            kwargs["recorded_at"] = recorded_at
        return {n.id for n in as_of(store, "cap.a", **kwargs)}

    assert active("2026-06-01T00:00:00Z") == {"svc.fix"}
    assert active("2027-06-01T00:00:00Z") == set()
    assert active("2026-06-01T00:00:00Z",
                 recorded_at="2026-07-01T00:00:00Z") == set()
    assert active("2026-06-01T00:00:00Z",
                 recorded_at="2026-09-01T00:00:00Z") == {"svc.fix"}


def test_event_envelope_carries_temporal_and_provenance_metadata():
    """CR-9H: every event carries id, type, subject, occurredAt, observedAt, source, version, payload."""
    event = Event(
        id="evt.1",
        type=EventType.ENTITY_CREATED,
        subject="app.cs-platform",
        occurred_at="2026-08-19T00:00:00Z",
        observed_at="2026-08-19T00:01:00Z",
        source="system.servicenow",
        version="1.0.0",
        payload={"name": "CS Platform", "lifecycle": "active"},
    )

    assert event.occurred_at == "2026-08-19T00:00:00Z"
    assert event.observed_at != event.occurred_at
    assert event.payload["name"] == "CS Platform"


def test_event_log_is_append_only_and_filters_by_subject_and_type():
    log = EventLog()
    for idx, kind in enumerate([
        EventType.ENTITY_CREATED, EventType.RELATIONSHIP_CHANGED,
        EventType.ENTITY_CHANGED, EventType.RELATIONSHIP_CHANGED,
    ]):
        log.append(Event(
            id=f"evt.{idx}", type=kind, subject="app.a",
            occurred_at=f"2026-01-{idx + 1:02d}T00:00:00Z",
            observed_at=f"2026-01-{idx + 1:02d}T00:01:00Z",
            source="system.test", version="1.0.0", payload={"k": idx}))

    assert [e.id for e in log.events] == ["evt.0", "evt.1", "evt.2", "evt.3"]
    relationship_events = log.filter(subject="app.a",
                                     type=EventType.RELATIONSHIP_CHANGED)
    assert [e.id for e in relationship_events] == ["evt.1", "evt.3"]


def test_snapshot_is_immutable_graph_view():
    store = InMemoryGraphStore()
    store.create_entity(Node(id="app.a", type="ApplicationComponent", name="A"))
    store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
    store.create_relationship(Edge(type="supports", source="app.a",
                                   target="cap.a", status="active"))
    snap = snapshot_graph(store, "snap.1", "initial")

    assert snap.id == "snap.1"
    assert "app.a" in snap.nodes
    assert ("app.a", "supports", "cap.a") in snap.edges

    store.create_entity(Node(id="app.b", type="ApplicationComponent", name="B"))
    assert "app.b" not in snap.nodes


def test_snapshot_diff_detects_added_and_removed_entities_and_edges():
    store = InMemoryGraphStore()
    store.create_entity(Node(id="app.a", type="ApplicationComponent", name="A"))
    store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
    store.create_relationship(Edge(type="supports", source="app.a",
                                   target="cap.a", status="active"))
    before = snapshot_graph(store, "snap.before")

    store.create_entity(Node(id="app.b", type="ApplicationComponent", name="B"))
    store.delete_entity("app.a", cascade=True)
    after = snapshot_graph(store, "snap.after")

    delta = diff_snapshots(before, after)
    assert delta.added_nodes == ["app.b"]
    assert delta.removed_nodes == ["app.a"]
    assert delta.added_edges == []
    assert delta.removed_edges == [("app.a", "supports", "cap.a")]


def test_temporal_symbols_are_exported():
    from runtime.temporal import (Snapshot as ExportedSnapshot,
                                  SnapshotDelta as ExportedDelta)
    assert ExportedSnapshot is Snapshot
    assert ExportedDelta is SnapshotDelta
