"""AssessmentTarget — generated from schemas/entities/assessment-target.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AssessmentTarget(Entity):
    """A desired future value or maturity level for a subject and criterion, with target date, rationale and approver (CR-5 §21). Targets live in the assessment layer — never on the architectural entity."""

    type: Literal['AssessmentTarget']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    subject_ref: Optional[str] = None
    framework_ref: Optional[str] = None
    criterion_ref: Optional[str] = None
    target_value: Optional[float] = None
    target_level_ref: Optional[str] = None
    target_date: Optional[str] = None
    """A010: temporal targets must identify their target date."""
    rationale: Optional[str] = None
    approved_by: Optional[str] = None
