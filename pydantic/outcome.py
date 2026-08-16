"""Outcome — generated from schemas/entities/outcome.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Outcome(Entity):
    """A resulting state or value (CR-4 §14). Capability is an ability; Outcome is a result. Anchor for strategy, value, DMM, transformation and measurement."""

    type: Literal['Outcome']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    statement: Optional[str] = None
    """The outcome statement in natural language."""
