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
    required_skills: Optional[list[str]] = None
    """Skill ids required by this role."""
    fulfilled_by: Optional[list[str]] = None
    """Actor ids currently fulfilling this role. DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
