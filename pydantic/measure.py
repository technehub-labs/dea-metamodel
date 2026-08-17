"""Measure — generated from schemas/entities/measure.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Measure(Entity):
    """A quantifiable observation of an indicator — value, unit, observation time and source (CR-5 §9). The unit is referenced, never encoded into the entity name."""

    type: Literal['Measure']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    indicator_ref: Optional[str] = None
    value: Optional[float] = None
    unit_ref: Optional[str] = None
    """Reference to the Unit the value is expressed in."""
    observed_at: Optional[str] = None
    source: Optional[str] = None
