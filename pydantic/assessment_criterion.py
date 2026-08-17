"""AssessmentCriterion — generated from schemas/entities/assessment-criterion.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AssessmentCriterion(Entity):
    """Defines what is evaluated within a dimension — id, name, definition, applicability and evaluation guidance (CR-5 §7). A criterion never contains the result of an evaluation."""

    type: Literal['AssessmentCriterion']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    dimension_ref: Optional[str] = None
    """Reference to the parent AssessmentDimension."""
    applicability: Optional[str] = None
    evaluation_guidance: Optional[str] = None
