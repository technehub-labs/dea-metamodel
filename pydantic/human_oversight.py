"""HumanOversight — generated from schemas/entities/human-oversight.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class HumanOversight(Entity):
    """First-class human oversight of agent behavior (CR-7 §25): approve-before-action, review-after-action, intervene-on-exception, continuous supervision — materially different governance patterns."""

    type: Literal['HumanOversight']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    oversight_pattern: Optional[Literal['approve-before', 'review-after', 'intervene-on-exception', 'continuous-supervision']] = None
    overseer_ref: Optional[str] = None
    """The human/role/body providing oversight."""
