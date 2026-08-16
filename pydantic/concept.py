"""Concept — generated from schemas/entities/concept.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Concept(Entity):
    """A canonical, definable unit of meaning (business term or classification node) that other entities link to via defined_by. Merged from Glossary Term + Taxonomy Node in v0.4.0 (ADR-0004 D2) — a queryable concept graph, not a static glossary document. Dimension entity of orthogonal_allocators.semantic-dimension. Catalog: technehub-labs/dea-catalog-concepts."""

    type: Literal['Concept']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    definition: str
    """Canonical definition of this concept."""
    abbreviation: Optional[str] = None
    """Common abbreviation."""
    synonyms: Optional[list[str]] = None
    """Alternative names for this concept."""
    usage_context: Optional[str] = None
    """When and how to use this concept."""
