"""CR-11 Phase 6 — Event interoperability (CR-11AF / CR-11AG)."""
from .envelope import (CanonicalEventError, EventIngestError,
                        EVENT_JSON_SCHEMA, event_json_schema,
                        validate_envelope)
from .service import (EventAdapter, EventIngestResult, EventPipeline,
                       EventPublicationService, EventPublishResult,
                       KnowledgeUpdate, PassthroughAdapter,
                       derive_updates)

__all__ = [
    "CanonicalEventError", "EventIngestError",
    "EVENT_JSON_SCHEMA", "event_json_schema", "validate_envelope",
    "EventAdapter", "PassthroughAdapter",
    "EventPublicationService", "EventPipeline",
    "EventIngestResult", "EventPublishResult",
    "KnowledgeUpdate", "derive_updates",
]
