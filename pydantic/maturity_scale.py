"""MaturityScale — generated from schemas/entities/maturity-scale.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class MaturityScale(Entity):
    """The scale over which a maturity model's levels are defined (CR-5 §12), e.g. a 1..5 ordered range."""

    type: Literal['MaturityScale']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    model_ref: Optional[str] = None
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    granularity: Optional[float] = None
