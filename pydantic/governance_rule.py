"""GovernanceRule — generated from schemas/entities/governance-rule.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class GovernanceRule(Entity):
    """A rule established by a GovernanceBody (CR-7 §34) as part of the governance mechanism."""

    type: Literal['GovernanceRule']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    body_ref: Optional[str] = None
    statement: Optional[str] = None
    enforced_by: Optional[str] = None
