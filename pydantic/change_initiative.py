"""ChangeInitiative — generated from schemas/entities/change-initiative.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ChangeInitiative(Entity):
    """A deliberate effort to shift Skills, Roles, or culture within an Organizational Unit, typically funded by an Investment Initiative. OpenDEAM v0.3.0 (ADR-0003), L3/People, Skills & Culture."""

    type: Literal['ChangeInitiative']
    change_scope: Optional[Literal['skills', 'roles', 'culture', 'structure']] = None
    """Primary target of the change."""
    targets: Optional[list[str]] = None
    """Organizational Unit ids targeted."""
    funded_by: Optional[str] = None
    """Investment Initiative id funding this change. DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
