"""GlossaryTerm — generated from schemas/entities/glossary-term.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class GlossaryTerm(Entity):
    """A controlled vocabulary term with definition and cross-references."""

    type: Literal['GlossaryTerm']
    definition: str
    """Canonical definition of this term."""
    abbreviation: Optional[str] = None
    """Common abbreviation."""
    synonyms: Optional[list[str]] = None
    """Alternative names for this term."""
    antonyms: Optional[list[str]] = None
    related_terms: Optional[list[str]] = None
    metamodel_entity: Optional[str] = None
    """The metamodel Entity type this term maps to."""
    usage_context: Optional[str] = None
    """When and how to use this term."""
