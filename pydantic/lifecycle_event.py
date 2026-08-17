"""LifecycleEvent — generated from schemas/entities/lifecycle-event.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class LifecycleEvent(Entity):
    """An auditable event that moves a subject through its lifecycle (CR-6 §28): created, approved, activated, modified, suspended, deprecated, retired, reactivated, superseded. Captures subject, timestamp, actor, reason and source — the raw material of architectural history (§17)."""

    type: Literal['LifecycleEvent']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    event_type: Optional[Literal['created', 'approved', 'activated', 'modified', 'suspended', 'deprecated', 'retired', 'reactivated', 'superseded']] = None
    subject_ref: Optional[str] = None
    """Entity the event happened to."""
    occurred_at: Optional[str] = None
    actor: Optional[str] = None
    """Who/what performed or authorized the event."""
    reason: Optional[str] = None
    source: Optional[str] = None
