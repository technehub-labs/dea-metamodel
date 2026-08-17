"""AssessmentScope — generated from schemas/entities/assessment-scope.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AssessmentScope(Entity):
    """The explicit boundary of an assessment (CR-5 §15), modeled as references to actual enterprise entities wherever possible rather than free-text labels."""

    type: Literal['AssessmentScope']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    scope_kind: Optional[Literal['enterprise', 'domain', 'capability', 'business-unit', 'geography', 'product', 'program']] = None
    entity_refs: Optional[list[str]] = None
    """References to the DEA entities bounding the scope."""
