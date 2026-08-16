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
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    change_scope: Optional[Literal['skills', 'roles', 'culture', 'structure']] = None
    """Primary target of the change."""
