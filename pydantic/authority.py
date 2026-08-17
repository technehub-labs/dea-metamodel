"""Authority — generated from schemas/entities/authority.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Authority(Entity):
    """The right to decide or act within defined limits (CR-7 §18). Capability to perform an action is not authority to perform it: an agent may be capable of approving transactions yet authorized only up to $10,000. This distinction is structural, not documentary."""

    type: Literal['Authority']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    scope: Optional[str] = None
    """G005/G006: what the authority covers."""
    limits: Optional[str] = None
    """e.g. value ceilings, domains, conditions."""
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
