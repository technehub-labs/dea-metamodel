"""CR-11 Phase 6 — canonical event envelope (CR-11AF).

The canonical event envelope extends the CR-9H envelope with two
interoperability concerns:

1. **Schema-first JSON representation.** Every event emitted or accepted by
   the OpenDEA runtime is valid against :data:`EVENT_JSON_SCHEMA`. The
   schema is derived from :class:`runtime.temporal.Event` and the spec
   shape from CR-11 §34 (CR-11AF). Anything that fails validation is
   refused at the boundary — never silently coerced.

2. **Connection to the CR-11 interoperability machinery.** The envelope
   carries the same ``source`` concept as CR-11B/C/D (ExternalSystem or
   ``opendea``), the same ``version`` concept as CR-11V (Exchange), and
   the same ``provenance`` shape as the Exchange envelope. A consumer
   reading the EventLog can therefore audit and reconcile events with
   no extra translation step.
"""
from __future__ import annotations

from typing import Any, Dict

import jsonschema


class CanonicalEventError(Exception):
    """Canonical event envelope invariant violated."""


class EventIngestError(Exception):
    """Pipeline refused to ingest an external event."""


# Canonical JSON Schema for the CR-11 envelope. Mirrors CR-9H fields
# + the optional ``provenance`` bag that matches CR-11S/T/U's Exchange
# envelope shape (CR-11AF §34).
EVENT_JSON_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "OpenDEA Canonical Event Envelope",
    "type": "object",
    "required": ["id", "type", "subject", "occurredAt", "observedAt",
                "source", "version"],
    "additionalProperties": False,
    "properties": {
        "id":         {"type": "string", "minLength": 1},
        "type":       {"type": "string", "minLength": 1,
                       "enum": [
                           "ENTITY_CREATED", "ENTITY_CHANGED",
                           "ENTITY_DELETED", "RELATIONSHIP_CHANGED",
                           "OBSERVATION_RECEIVED", "ASSESSMENT_UPDATED",
                           "SCENARIO_CREATED", "DECISION_APPROVED",
                       ]},
        "subject":    {"type": "string", "minLength": 1},
        "occurredAt": {"type": "string", "minLength": 1,
                       "description": "ISO-8601 timestamp at which the event fact was true."},
        "observedAt": {"type": "string", "minLength": 1,
                       "description": "ISO-8601 timestamp at which the event was observed by the source."},
        "source":     {"type": "string", "minLength": 1,
                       "description": "ExternalSystem id or 'opendea' for runtime-internal events."},
        "version":    {"type": "string", "minLength": 1,
                       "description": "SemVer of the emitting schema/contract (CR-11V)."},
        "payload":    {"type": "object", "default": {},
                       "description": "Type-specific event payload (JSON object)."},
        "provenance": {"type": "object", "default": {},
                       "description": "Optional provenance bag mirroring CR-11S/T/U exchange provenance."},
    },
}


def event_json_schema() -> Dict[str, Any]:
    """Return the canonical event envelope schema (Draft 7)."""
    return dict(EVENT_JSON_SCHEMA)


def validate_envelope(envelope: Dict[str, Any]) -> Dict[str, Any]:
    """Validate an event envelope against :data:`EVENT_JSON_SCHEMA`.

    Returns the (possibly defaulted) envelope on success. Raises
    :class:`CanonicalEventError` with the underlying jsonschema error
    list when the envelope is invalid. The envelope is never silently
    rewritten — invalid input fails loud.
    """
    if not isinstance(envelope, dict):
        raise CanonicalEventError("event envelope must be a JSON object")
    try:
        jsonschema.Draft7Validator.check_schema(EVENT_JSON_SCHEMA)
    except jsonschema.SchemaError as exc:
        raise CanonicalEventError(f"event schema error: {exc}") from exc
    errors = sorted(
        jsonschema.Draft7Validator(EVENT_JSON_SCHEMA).iter_errors(envelope),
        key=lambda e: list(e.absolute_path),
    )
    if errors:
        message = "; ".join(
            f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
            for e in errors)
        raise CanonicalEventError(f"event envelope invalid: {message}")
    # Apply defaults so callers don't have to handle missing payload.
    with_defaults = dict(envelope)
    with_defaults.setdefault("payload", {})
    with_defaults.setdefault("provenance", {})
    return with_defaults
