"""Objective — generated from schemas/entities/objective.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Objective(Entity):
    """Makes an Intent operationally measurable (CR-7 §5): statement, target value, unit, target date. Objective ≠ Outcome (§6): an objective is what we intend to achieve; an outcome is what happened. Connects to CR-5 via AssessmentTarget."""

    type: Literal['Objective']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    intent_ref: Optional[str] = None
    statement: Optional[str] = None
    target_value: Optional[float] = None
    unit: Optional[str] = None
    target_date: Optional[str] = None
