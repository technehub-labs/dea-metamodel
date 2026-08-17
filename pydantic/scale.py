"""Scale — generated from schemas/entities/scale.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Scale(Entity):
    """A declared ordered value space for scores and measures (CR-5 Phase 2; A004) — e.g. a 0..1 ratio or a 1..5 ordinal range."""

    type: Literal['Scale']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    scale_type: Optional[Literal['nominal', 'ordinal', 'interval', 'ratio']] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
