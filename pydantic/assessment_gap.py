"""AssessmentGap — generated from schemas/entities/assessment-gap.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AssessmentGap(Entity):
    """The derived difference between a current result and a target (CR-5 §30). Gaps are derived, never authoritative source data; the authoritative data are current state and target state. Gaps connect assessment to transformation via addressed-by → Change (CR-5 §31)."""

    type: Literal['AssessmentGap']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    subject_ref: Optional[str] = None
    current_result_ref: Optional[str] = None
    target_ref: Optional[str] = None
    gap_value: Optional[float] = None
    derived: Optional[Literal[True]] = None
    """CR-5 §30: gaps are always derived."""
