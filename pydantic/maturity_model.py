"""MaturityModel — generated from schemas/entities/maturity-model.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class MaturityModel(Entity):
    """An ordered set of maturity levels defined, governed and versioned by an assessment framework (CR-5 §12/§33). Maturity belongs to the framework, not to any architectural entity (CR-5 §13)."""

    type: Literal['MaturityModel']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    framework_ref: Optional[str] = None
    model_version: Optional[str] = None
    level_count: Optional[int] = None
