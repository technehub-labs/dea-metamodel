"""CR-9H/I — event envelope and event log (CR-9H canonical event model)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional


class EventType(str, Enum):
    """Canonical event taxonomy (CR-9H)."""

    ENTITY_CREATED = "ENTITY_CREATED"
    ENTITY_CHANGED = "ENTITY_CHANGED"
    ENTITY_DELETED = "ENTITY_DELETED"
    RELATIONSHIP_CHANGED = "RELATIONSHIP_CHANGED"
    OBSERVATION_RECEIVED = "OBSERVATION_RECEIVED"
    ASSESSMENT_UPDATED = "ASSESSMENT_UPDATED"
    SCENARIO_CREATED = "SCENARIO_CREATED"
    DECISION_APPROVED = "DECISION_APPROVED"


@dataclass(frozen=True)
class Event:
    """Canonical event envelope (CR-9H)."""

    id: str
    type: EventType
    subject: str
    occurred_at: str
    observed_at: str
    source: str
    version: str
    payload: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id or not self.subject:
            raise ValueError("event id and subject are required")
        for field_name in ("occurred_at", "observed_at"):
            value = getattr(self, field_name)
            if not value:
                raise ValueError(f"{field_name} is required")

    def for_subject(self, subject: str) -> "Event":
        return self if self.subject == subject else None  # type: ignore

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "type": self.type.value, "subject": self.subject,
            "occurredAt": self.occurred_at, "observedAt": self.observed_at,
            "source": self.source, "version": self.version,
            "payload": self.payload,
        }


class EventLog:
    """Append-only event store (CR-9I)."""

    def __init__(self):
        self._events: List[Event] = []

    def append(self, event: Event) -> Event:
        self._events.append(event)
        return event

    @property
    def events(self) -> List[Event]:
        return tuple(self._events)  # type: ignore[return-value]

    def filter(self, subject: Optional[str] = None,
              type: Optional[EventType] = None) -> List[Event]:
        out: List[Event] = []
        for event in self._events:
            if subject is not None and event.subject != subject:
                continue
            if type is not None and event.type != type:
                continue
            out.append(event)
        return out
