"""Score — generated from schemas/entities/score.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Score(Entity):
    """A numerical or ordinal evaluation derived from measures against a declared scale (CR-5 §11). A score is not intrinsically a maturity level; the framework defines the transformation. Derivation from measures is expressed via the dea:derives-from relationship (CR-3: no relationship state on entities)."""

    type: Literal['Score']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    value: Optional[float] = None
    scale_ref: Optional[str] = None
    """Reference to the declared Scale (A004: scores use a declared scale)."""
