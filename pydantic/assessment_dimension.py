"""AssessmentDimension — generated from schemas/entities/assessment-dimension.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AssessmentDimension(Entity):
    """A structured perspective through which a subject is evaluated (CR-5 §6). An assessment perspective, not an architectural entity: a DMM dimension never becomes equivalent to the DEA entities it assesses."""

    type: Literal['AssessmentDimension']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    dimension_order: Optional[int] = None
    evaluation_perspective: Optional[str] = None
