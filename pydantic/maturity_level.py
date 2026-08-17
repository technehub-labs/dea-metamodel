"""MaturityLevel — generated from schemas/entities/maturity-level.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class MaturityLevel(Entity):
    """A named, ordered position within a maturity model (CR-5 §12). Belongs to the referenced maturity model (A005); results attain levels — entities never carry them intrinsically (A008)."""

    type: Literal['MaturityLevel']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    model_ref: Optional[str] = None
    level_order: Optional[int] = None
    level_name: Optional[str] = None
