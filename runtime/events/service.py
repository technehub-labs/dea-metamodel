"""CR-11 Phase 6 — event publication / ingestion pipeline (CR-11AG).

The pipeline realises the spec flow:

    External Event
        ↓
    Event Adapter
        ↓
    OpenDEA Event
        ↓
    Knowledge Update
        ↓
    Rules → Assessment → Agent / Decision

The implementation is intentionally simple and runtime-graph-agnostic:
every stage exposes a typed input and a typed output. Callers wire the
graph store, assessment service, and rule engine of their choosing via
constructor injection. The contract is what matters, not the wiring.

Knowledge updates are produced for the four types that the runtime
treats as graph mutations: ENTITY_CREATED / ENTITY_CHANGED /
ENTITY_DELETED / RELATIONSHIP_CHANGED. Any other event type is
published but does not produce a knowledge update by itself — it
informally notifies downstream consumers (assessment / decision / agent).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ..graph.base import utcnow
from ..temporal import Event, EventType
from .envelope import (CanonicalEventError, EventIngestError,
                        validate_envelope)


# --------------------------------------------------------------------- types


@dataclass(frozen=True)
class KnowledgeUpdate:
    """A mutation hint derived from an event.

    The runtime uses the standard CRUD API to apply the update;
    ``KnowledgeUpdate`` is the structured payload that drives it.
    """

    operation: str            # "create" | "update" | "delete" | "relate" | "unrelate"
    entity_id: str
    entity_type: Optional[str] = None
    name: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    target_id: Optional[str] = None   # for relate / unrelate
    relationship: Optional[str] = None
    source_event_id: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v not in (None, "")}


@dataclass(frozen=True)
class EventIngestResult:
    """Outcome of the :meth:`EventPipeline.ingest` step."""

    accepted: bool
    event_id: str
    knowledge_updates: List[KnowledgeUpdate]
    downstream_invoked: List[str]   # names of stages that processed the event
    notes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class EventPublishResult:
    """Outcome of :meth:`EventPublicationService.publish`."""

    accepted: bool
    event_id: str
    event_type: EventType
    occurred_at: str


# ---------------------------------------------------------------- adapters


class EventAdapter:
    """CR-11AG — converts an *external* event envelope into a canonical one.

    The adapter is the only place external payload shape enters the
    pipeline; once normalised, every downstream stage sees the canonical
    envelope and is decoupled from the producer's wire format.

    Concrete adapters are subclasses or `register_payload_transform`
    callers; the shipped :class:`PassthroughAdapter` accepts envelopes
    that already match the canonical schema.
    """

    def adapt(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("adapt() must be implemented by a subclass")


class PassthroughAdapter(EventAdapter):
    """Default adapter: validates the envelope as-is.

    Use when the upstream system already speaks the canonical shape
    (e.g. an OpenDEA → OpenDEA federation). For ServiceNow / BPMN / etc.
    implementations, subclass and translate the payload before calling
    :func:`runtime.events.validate_envelope`.
    """

    def adapt(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        return validate_envelope(envelope)


# ------------------------------------------------------------------- derives


def derive_updates(event: Event) -> List[KnowledgeUpdate]:
    """Map a canonical :class:`Event` to :class:`KnowledgeUpdate` hints.

    Only the four entity-/relationship-mutating event types produce
    updates; the other event types (OBSERVATION_RECEIVED,
    ASSESSMENT_UPDATED, SCENARIO_CREATED, DECISION_APPROVED) are passed
    through unchanged so downstream stages can react.
    """
    payload = event.payload or {}
    if event.type == EventType.ENTITY_CREATED:
        return [KnowledgeUpdate(
            operation="create",
            entity_id=payload.get("entity_id") or payload.get("id")
                      or event.subject,
            entity_type=payload.get("entity_type"),
            name=payload.get("name"),
            properties=payload.get("properties", {}),
            source_event_id=event.id,
        )]
    if event.type == EventType.ENTITY_CHANGED:
        return [KnowledgeUpdate(
            operation="update",
            entity_id=event.subject,
            entity_type=payload.get("entity_type"),
            properties=payload.get("properties", {}),
            source_event_id=event.id,
        )]
    if event.type == EventType.ENTITY_DELETED:
        return [KnowledgeUpdate(
            operation="delete",
            entity_id=event.subject,
            source_event_id=event.id,
        )]
    if event.type == EventType.RELATIONSHIP_CHANGED:
        return [KnowledgeUpdate(
            operation=payload.get("change", "relate"),
            entity_id=payload.get("source") or event.subject,
            target_id=payload.get("target"),
            relationship=payload.get("relationship"),
            properties=payload.get("properties", {}),
            source_event_id=event.id,
        )]
    return []


# ---------------------------------------------------------------- service


class EventPublicationService:
    """CR-11AG — publishes canonical events into an :class:`EventLog`.

    The publication step is the *only* path that turns a runtime
    mutation into a canonical event (CR-11AF). Downstream stages
    subscribe via :class:`EventPipeline`.
    """

    def __init__(self, log):
        self.log = log

    def publish(self, event_type: EventType, subject: str,
                source: str = "opendea", version: str = "1.0.0",
                payload: Optional[Dict[str, Any]] = None,
                occurred_at: Optional[str] = None,
                observed_at: Optional[str] = None,
                provenance: Optional[Dict[str, Any]] = None,
                event_id: Optional[str] = None,
                ) -> EventPublishResult:
        now = utcnow().isoformat()
        event = Event(
            id=event_id or f"evt.{event_type.value.lower()}.{len(self.log.events) + 1}",
            type=event_type,
            subject=subject,
            occurred_at=occurred_at or now,
            observed_at=observed_at or now,
            source=source,
            version=version,
            payload=payload or {},
        )
        # Validate the envelope shape; CR-11AF requires the canonical schema.
        candidate = {
            "id": event.id, "type": event.type.value,
            "subject": event.subject,
            "occurredAt": event.occurred_at,
            "observedAt": event.observed_at,
            "source": event.source, "version": event.version,
            "payload": event.payload,
            "provenance": provenance or {},
        }
        normalised = validate_envelope(candidate)
        # Round-trip through the dataclass so downstream readers
        # always see Event objects, never raw dicts.
        self.log.append(Event(
            id=normalised["id"], type=event_type,
            subject=normalised["subject"],
            occurred_at=normalised["occurredAt"],
            observed_at=normalised["observedAt"],
            source=normalised["source"],
            version=normalised["version"],
            payload=normalised["payload"],
        ))
        return EventPublishResult(
            accepted=True, event_id=event.id, event_type=event_type,
            occurred_at=event.occurred_at,
        )


# Stage hooks — named callables so tests can assert invocation order.
RulesStage = Callable[[Event], None]
AssessmentStage = Callable[[Event], None]
AgentStage = Callable[[Event], None]


class EventPipeline:
    """CR-11AG — External Event → Adapter → Knowledge Update → Rules → Assessment → Agent.

    The pipeline is composed of independent stages; each stage is a
    callable receiving the canonical :class:`Event`. The pipeline
    doesn't own the runtime store or assessment service — it exposes
    hooks so concrete wiring can adapt to any graph store.
    """

    def __init__(self, publication: EventPublicationService,
                 adapter: Optional[EventAdapter] = None,
                 *,
                 rules: Optional[RulesStage] = None,
                 assessment: Optional[AssessmentStage] = None,
                 agent: Optional[AgentStage] = None,
                 apply_updates: Optional[Callable[[List[KnowledgeUpdate]], None]] = None):
        self.publication = publication
        self.adapter = adapter or PassthroughAdapter()
        self.rules = rules or (lambda event: None)
        self.assessment = assessment or (lambda event: None)
        self.agent = agent or (lambda event: None)
        self._apply_updates = apply_updates

    def ingest(self, envelope: Dict[str, Any]) -> EventIngestResult:
        """Run the full pipeline for an *external* envelope.

        Refuses to ingest unless:
        - the envelope validates against :data:`EVENT_JSON_SCHEMA`;
        - the adapter successfully normalises it.
        Returns an :class:`EventIngestResult` describing knowledge
        updates derived and downstream stages invoked.
        """
        try:
            normalised = self.adapter.adapt(envelope)
            if not isinstance(normalised, dict):
                raise EventIngestError(
                    "adapter must return a canonical envelope dict")
        except CanonicalEventError as exc:
            raise EventIngestError(f"adapter rejected envelope: {exc}") from exc
        event = Event(
            id=normalised["id"],
            type=EventType(normalised["type"]),
            subject=normalised["subject"],
            occurred_at=normalised["occurredAt"],
            observed_at=normalised["observedAt"],
            source=normalised["source"],
            version=normalised["version"],
            payload=normalised.get("payload", {}),
        )
        updates = derive_updates(event)
        if updates and self._apply_updates is not None:
            try:
                self._apply_updates(updates)
            except Exception as exc:  # pragma: no cover — defensive
                raise EventIngestError(
                    f"knowledge update failed: {exc}") from exc

        invoked: List[str] = []
        for stage_name, stage in (("rules", self.rules),
                                  ("assessment", self.assessment),
                                  ("agent", self.agent)):
            try:
                stage(event)
            except Exception as exc:
                raise EventIngestError(
                    f"{stage_name} stage failed: {exc}") from exc
            invoked.append(stage_name)

        notes = []
        if not updates:
            notes.append("non-mutating event type — no knowledge update produced")

        return EventIngestResult(
            accepted=True,
            event_id=event.id,
            knowledge_updates=updates,
            downstream_invoked=invoked,
            notes=notes,
        )
