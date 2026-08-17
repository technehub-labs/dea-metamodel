"""AssessmentSubject — generated from schemas/entities/assessment-subject.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AssessmentSubject(Entity):
    """The thing being evaluated — a reference to a DEA entity at an explicit scope (CR-5 §14). Allows the same entity to be assessed at different organizational scopes."""

    type: Literal['AssessmentSubject']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    entity_ref: Optional[str] = None
    """Reference to the assessed DEA entity."""
    scope_qualifiers: Optional[dict[str, Any]] = None
    """e.g. organizational_unit, geography, business_unit."""
