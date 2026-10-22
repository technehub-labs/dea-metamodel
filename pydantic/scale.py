"""Scale  :  generated from schemas/entities/scale.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Scale(Entity):
    """A declared ordered value space for scores and measures (CR-5 Phase 2; A004); e.g. a 0..1 ratio or a 1..5 ordinal range."""

    type: Literal['Scale']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    scale_type: Optional[Literal['nominal', 'ordinal', 'interval', 'ratio', 'categorical', 'boolean']] = None
    """The scale type (CR-5 Phase 2; CR-MET-005 binding extension). Categorical and boolean added in CR-MET-005 per the user-supplied binding; ordinal/categorical/boolean scales must not be treated as physical measurement units."""
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    scale_values: Optional[list[str]] = None
    """The allowed values for the scale (CR-MET-005). Required for scale_type: categorical, ordinal, and boolean (boolean MUST have exactly two entries). Optional for scale_type: nominal. For scale_type: interval and ratio, the numeric minimum/maximum apply."""
    ordered: Optional[bool] = None
    """Whether the scale is ordered (CR-MET-005). True for ordinal, interval, ratio; false for nominal, categorical, boolean (boolean is two-valued but not ordinal)."""
