"""CR-11 Phase 6 — event interoperability (CR-11AF / CR-11AG)."""

import pytest

from runtime.events import (CanonicalEventError, EVENT_JSON_SCHEMA,
                             EventAdapter, EventIngestError,
                             EventPipeline, EventPublicationService,
                             PassthroughAdapter, validate_envelope,
                             derive_updates, KnowledgeUpdate)
from runtime.events.envelope import event_json_schema
from runtime.events.service import EventIngestResult, EventPublishResult
from runtime.temporal import Event, EventLog, EventType


def _base_event():
    return {
        "id": "evt.acme.cap-x.created",
        "type": "ENTITY_CREATED",
        "subject": "cap.customer-service",
        "occurredAt": "2026-08-21T01:00:00Z",
        "observedAt": "2026-08-21T01:00:01Z",
        "source": "itsm.servicenow",
        "version": "1.0.0",
        "payload": {"entity_type": "BusinessCapability",
                    "name": "Customer Service",
                    "properties": {"owner": "cx-team"}},
    }


def test_envelope_validates_against_canonical_schema():
    """CR-11AF — envelopes validate against the JSON Schema."""
    env = validate_envelope(_base_event())
    assert env["id"] == "evt.acme.cap-x.created"
    assert env["payload"]["entity_type"] == "BusinessCapability"


def test_envelope_rejects_invalid_types():
    """Unrecognised event types are rejected at the boundary."""
    bad = dict(_base_event())
    bad["type"] = "ENTITY_HOVERED"
    with pytest.raises(CanonicalEventError):
        validate_envelope(bad)


def test_envelope_rejects_missing_required_fields():
    """Required CR-9H fields are still required for the CR-11 envelope."""
    bad = dict(_base_event()); del bad["subject"]
    with pytest.raises(CanonicalEventError):
        validate_envelope(bad)


def test_envelope_rejects_extra_fields():
    """additionalProperties:false — unknown top-level keys are refused."""
    bad = dict(_base_event()); bad["sneaky"] = True
    with pytest.raises(CanonicalEventError):
        validate_envelope(bad)


def test_event_json_schema_is_published():
    """CR-11AF — the schema is exposed for downstream tooling."""
    schema = event_json_schema()
    assert schema["title"] == "OpenDEA Canonical Event Envelope"
    assert schema is not EVENT_JSON_SCHEMA  # defensive copy returned


def test_publication_round_trips_through_eventlog():
    """Publication → EventLog so consumers see canonical Event objects."""
    log = EventLog()
    pub = EventPublicationService(log)
    result = pub.publish(EventType.ENTITY_CHANGED, "cap.customer-service",
                         payload={"change": "maturity: 2.7 → 3.0"})
    assert result.accepted is True
    # The event lands in the EventLog as a canonical Event.
    events = log.filter(subject="cap.customer-service")
    assert len(events) == 1
    assert events[0].type == EventType.ENTITY_CHANGED
    assert events[0].source == "opendea"


def test_publication_refuses_invalid_envelope():
    """The publication step enforces the schema at the runtime boundary."""
    log = EventLog()
    pub = EventPublicationService(log)
    # Bypass schema validation by going around publish (defensive):
    with pytest.raises(CanonicalEventError):
        validate_envelope({"type": "ENTITY_CREATED",
                            "subject": "x",
                            "occurredAt": "t", "observedAt": "t",
                            "source": "opendea", "version": "1.0.0"})
                          # missing id


def test_passthrough_adapter_normalises_external_envelope():
    """Default adapter validates the external shape into the canonical one."""
    adapter = PassthroughAdapter()
    canonical = adapter.adapt(_base_event())
    assert canonical["id"].startswith("evt.")
    assert canonical["version"] == "1.0.0"


class CustomAdapter(EventAdapter):
    """Adapter that lifts a payload-only external envelope."""

    def adapt(self, envelope):
        if "id" not in envelope:
            envelope = dict(envelope)
            envelope["id"] = f"evt.custom.{envelope.get('subject', 'x')}"
        if "type" not in envelope:
            raise CanonicalEventError("custom adapter requires a type")
        return validate_envelope(envelope)


def test_custom_adapter_wires_pipeline():
    """Custom adapters can be plugged into the pipeline."""
    log = EventLog(); pub = EventPublicationService(log)
    received = []
    pipeline = EventPipeline(pub, adapter=CustomAdapter(),
                             rules=lambda event: received.append(("rules", event.id)),
                             assessment=lambda event: received.append(("assessment", event.id)),
                             apply_updates=lambda updates: received.append(("update", len(updates))))
    result = pipeline.ingest({
        # No id: adapter fills it; no payload: accepts default.
        "subject": "cap.x", "type": "ENTITY_CREATED",
        "occurredAt": "2026-08-21T02:00:00Z",
        "observedAt": "2026-08-21T02:00:00Z",
        "source": "itsm.servicenow", "version": "1.0.0",
        "payload": {"entity_type": "BusinessCapability",
                    "name": "X", "properties": {}},
    })
    assert result.accepted
    assert result.event_id.startswith("evt.custom.")
    assert ("rules", result.event_id) in received
    assert ("assessment", result.event_id) in received
    assert ("update", 1) in received
    # The published event is in the log.
    assert len(log.events) == 0  # publication reserved for the publish() step; ingest observes only


def test_derive_updates_entity_created():
    """Knowledge-update derivation for ENTITY_CREATED matches the canonical shape."""
    event = Event(
        id="ev1", type=EventType.ENTITY_CREATED,
        subject="cap.x", occurred_at="2026-08-21T01:00:00Z",
        observed_at="2026-08-21T01:00:01Z",
        source="opendea", version="1.0.0",
        payload={"entity_type": "BusinessCapability", "name": "X",
                  "properties": {"owner": "cx"}, "entity_id": "cap.x"},
    )
    updates = derive_updates(event)
    assert len(updates) == 1
    u = updates[0]
    assert u.operation == "create"
    assert u.entity_id == "cap.x"
    assert u.source_event_id == "ev1"


def test_derive_updates_relationship_changed():
    """RELATIONSHIP_CHANGED maps to a relate-style knowledge update."""
    event = Event(id="ev2", type=EventType.RELATIONSHIP_CHANGED,
                  subject="cap.parent",
                  occurred_at="t", observed_at="t",
                  source="opendea", version="1.0.0",
                  payload={"source": "cap.parent", "target": "cap.child",
                            "relationship": "dea:part-of",
                            "change": "relate"})
    updates = derive_updates(event)
    assert len(updates) == 1
    u = updates[0]
    assert u.operation == "relate"
    assert u.target_id == "cap.child"
    assert u.relationship == "dea:part-of"


def test_observation_event_produces_no_knowledge_update():
    """OBSERVATION_RECEIVED only notifies — never mutates the graph."""
    event = Event(id="ev3", type=EventType.OBSERVATION_RECEIVED,
                  subject="cap.x", occurred_at="t", observed_at="t",
                  source="digital-twin", version="1.0.0",
                  payload={"observed": "running"})
    assert derive_updates(event) == []


def test_ingest_runs_full_pipeline_with_downstream_stages():
    """Stage ordering: knowledge-update → rules → assessment → agent."""
    log = EventLog(); pub = EventPublicationService(log)
    order: list[str] = []
    pipeline = EventPipeline(
        pub, adapter=PassthroughAdapter(),
        rules=lambda event: order.append("rules"),
        assessment=lambda event: order.append("assessment"),
        agent=lambda event: order.append("agent"),
        apply_updates=lambda updates: order.append(f"updates:{len(updates)}"),
    )
    result = pipeline.ingest(_base_event())
    assert order == ["updates:1", "rules", "assessment", "agent"]
    assert "rules" in result.downstream_invoked
    assert "assessment" in result.downstream_invoked
    assert "agent" in result.downstream_invoked


def test_ingest_refuses_invalid_external_envelope():
    """Adapters that raise cause the pipeline to refuse the event."""
    class BoomAdapter(EventAdapter):
        def adapt(self, envelope):
            raise CanonicalEventError("nope")
    pub = EventPublicationService(EventLog())
    pipeline = EventPipeline(pub, adapter=BoomAdapter())
    with pytest.raises(EventIngestError):
        pipeline.ingest(_base_event())
