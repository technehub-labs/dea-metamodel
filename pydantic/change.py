"""Change — generated from schemas/entities/change.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Change(Entity):
    """A deliberate modification to enterprise capabilities, behavior, services, information, technology, organization or operating model (CR-4 §17). Foundation for transformation, roadmap, transition architecture and migration."""

    type: Literal['Change']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    statement: Optional[str] = None
    """The change statement in natural language."""
