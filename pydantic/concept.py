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
    definition: str
    """Canonical definition of this concept."""
    abbreviation: Optional[str] = None
    """Common abbreviation."""
    synonyms: Optional[list[str]] = None
    """Alternative names for this concept."""
    parent_concept: Optional[Any] = None
    """ID of the parent Concept in the concept graph (null/omitted = root). Replaces TaxonomyNode's tree structure (ADR-0004 D2)."""
    related_concepts: Optional[list[str]] = None
    """IDs of related Concepts (non-hierarchical links)."""
    defines_entities: Optional[list[str]] = None
    """Entity IDs across L1-L5 that carry defined_by pointing at this Concept."""
    usage_context: Optional[str] = None
    """When and how to use this concept."""
