"""AssessmentFramework — generated from schemas/entities/assessment-framework.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AssessmentFramework(Entity):
    """The external methodology used to conduct an assessment — its dimensions, criteria, indicators, scoring, maturity model and evidence requirements (CR-5 §5). External to the subject being assessed and versioned independently of OpenDEA Core (CR-5 §33)."""

    type: Literal['AssessmentFramework']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    framework_version: Optional[str] = None
    """Framework's own version, governed independently of the metamodel (A012)."""
    authority: Optional[str] = None
    """The body that owns and publishes the framework."""
    maturity_model_ref: Optional[str] = None
    """Reference to the MaturityModel the framework defines, if any."""
