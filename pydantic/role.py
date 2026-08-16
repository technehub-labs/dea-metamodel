"""Role — generated from schemas/entities/role.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Role(Entity):
    """A defined set of required Skills and responsibilities that an Actor fulfills within an Organizational Unit. OpenDEAM v0.3.0 (ADR-0003), L3/People, Skills & Culture."""

    type: Literal['Role']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
