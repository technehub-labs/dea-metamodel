"""CR-10 Phase 7 — Digital Twin Foundation (CR-10AA/AB).

The runtime supports observation, operational state and drift detection
against the architecture baseline. The full digital twin claim is deferred
until synchronization and behavioral semantics exist (CR-013).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..api import RuntimeService
from ..graph import GraphStore


class ObservationError(Exception):
    """Digital twin observation invariant violated."""


@dataclass(frozen=True)
class ObservationEvent:
    id: str
    subject: str
    observed_state: str
    at: str
    source: str = "runtime.twin"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "subject": self.subject,
            "observedState": self.observed_state, "at": self.at,
            "source": self.source,
        }


@dataclass(frozen=True)
class OperationalState:
    """CR-10AA — the latest observed state of a subject."""

    subject: str
    state: str
    observed_at: str
    state_role: str = "current"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "subject": self.subject,
            "state": self.state,
            "observedAt": self.observed_at,
            "stateRole": self.state_role,
        }


@dataclass(frozen=True)
class StateDiff:
    """CR-10AB — comparison of architecture vs observed state."""

    subject: str
    architecture_state: str
    observed_state: str
    drift_detected: bool
    signals: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "subject": self.subject,
            "architectureState": self.architecture_state,
            "observedState": self.observed_state,
            "driftDetected": self.drift_detected,
            "signals": list(self.signals),
        }


class DigitalTwin:
    """CR-10 Phase 7 — observation + operational state + drift."""

    def __init__(self, service: RuntimeService):
        self.service = service
        self._observations: Dict[str, List[ObservationEvent]] = {}

    def observe(self, subject: str, observed_state: str,
                at: str = "", source: str = "runtime.twin") -> ObservationEvent:
        if not self.service.store.has_entity(subject):
            raise ObservationError(
                f"unknown subject {subject!r} — refusing to observe "
                "an entity that does not exist in the graph")
        event = ObservationEvent(
            id=f"tw.observation.{subject}.{len(self._observations.get(subject, [])) + 1}",
            subject=subject, observed_state=observed_state,
            at=at or "now", source=source,
        )
        self._observations.setdefault(subject, []).append(event)
        self._record_audit_edge(event)
        return event

    def current_state(self, subject: str) -> OperationalState:
        events = self._observations.get(subject, [])
        if not events:
            raise ObservationError(
                f"no observations recorded for {subject!r}")
        latest = events[-1]
        return OperationalState(
            subject=subject,
            state=latest.observed_state,
            observed_at=latest.at,
            state_role="current",
        )

    def state_diff(self, subject: str) -> StateDiff:
        store: GraphStore = self.service.store
        arch = store.get_entity(subject)
        observed = self.current_state(subject)
        signals = []
        drift = (arch.lifecycle_status != "active"
                 or observed.state != "active")
        if arch.lifecycle_status != "active":
            signals.append(
                f"architecture declares {arch.lifecycle_status!r} but observed "
                f"is {observed.state!r}")
        if observed.state != "active":
            signals.append(
                f"observed state {observed.state!r} diverges from architecture "
                f"active")
        return StateDiff(
            subject=subject,
            architecture_state=arch.lifecycle_status,
            observed_state=observed.state,
            drift_detected=drift,
            signals=signals,
        )

    def observation_log(self) -> List[ObservationEvent]:
        out: List[ObservationEvent] = []
        for events in self._observations.values():
            out.extend(events)
        return out

    def _record_audit_edge(self, event: ObservationEvent) -> None:
        # Mirror the observation into the graph so it survives a process
        # restart and can be queried alongside the architecture model.
        self.service.create_entity(
            event.id, "Observation", event.subject,
            properties={
                "provenance_kind": "observation",
                "observed_state": event.observed_state,
                "recorded_at": event.at,
                "source": event.source,
            })
        self.service.create_relationship(
            event.subject, "traces-to", event.id,
            status="active",
            provenance={"assertedBy": event.source,
                        "recordedAt": event.at})
