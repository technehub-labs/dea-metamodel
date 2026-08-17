"""Transition — generated from schemas/entities/transition.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Transition(Entity):
    """The movement between two architecture states, caused by a Change (CR-6 §14): from-state, to-state, causing change, planned/actual start and end, and status. A planned transition is never actual architecture (§2/§16)."""

    type: Literal['Transition']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    from_state_ref: Optional[str] = None
    to_state_ref: Optional[str] = None
    change_ref: Optional[str] = None
    """The Change causing this transition."""
    planned_start: Optional[str] = None
    planned_end: Optional[str] = None
    actual_start: Optional[str] = None
    actual_end: Optional[str] = None
    transition_status: Optional[Literal['planned', 'active', 'completed', 'cancelled']] = None
