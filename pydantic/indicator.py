"""Indicator — generated from schemas/entities/indicator.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Indicator(Entity):
    """The observable signal used to evaluate a criterion (CR-5 §8). Criterion = what we evaluate; Indicator = what we observe; Measure = what we quantify; Result = what was assessed."""

    type: Literal['Indicator']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    criterion_ref: Optional[str] = None
    signal_type: Optional[Literal['quantitative', 'qualitative', 'binary']] = None
