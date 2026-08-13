"""Viewpoint — generated from schemas/entities/viewpoint.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Viewpoint(Entity):
    """A filtered perspective on the metamodel for a specific stakeholder or concern."""

    type: Literal['Viewpoint']
    stakeholder: str
    """Primary stakeholder this viewpoint serves."""
    concern: str
    """The architectural concern this viewpoint addresses."""
    entities_included: Optional[list[str]] = None
    """Metamodel entity types shown in this viewpoint."""
    entities_excluded: Optional[list[str]] = None
    relationships_included: Optional[list[str]] = None
    """Relationship types shown."""
    filter_criteria: Optional[dict[str, Any]] = None
    """Dynamic filters: tags, domains, maturity levels, etc."""
    presentation_format: Optional[Literal['diagram', 'table', 'matrix', 'dashboard', 'narrative', 'multi']] = None
    generated_from: Optional[str] = None
    """Catalog or repository this viewpoint is generated from."""
