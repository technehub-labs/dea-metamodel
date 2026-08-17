"""Assessment — generated from schemas/entities/assessment.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Assessment(Entity):
    """A structured evaluation of one or more subjects against an assessment framework at a defined point or period in time (CR-5 §4). The evaluation event — never an attribute of the subject."""

    type: Literal['Assessment']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    framework_ref: Optional[str] = None
    """Reference to the AssessmentFramework this assessment is conducted under (A001: exactly one)."""
    scope_ref: Optional[str] = None
    """Reference to the AssessmentScope bounding this assessment (CR-5 §15)."""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    assessor: Optional[str] = None
    """Actor, team or system performing the assessment."""
    assessment_status: Optional[Literal['planned', 'in-progress', 'completed', 'superseded', 'withdrawn']] = None
    methodology: Optional[str] = None
