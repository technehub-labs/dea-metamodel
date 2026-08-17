"""AutonomyLevel — generated from schemas/entities/autonomy-level.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AutonomyLevel(Entity):
    """One level in a configurable autonomy model (CR-7 §23), e.g. 0 Inform · 1 Recommend · 2 Prepare · 3 Execute-with-approval · 4 Execute-within-delegated-authority · 5 Autonomous. The scale is a profile concern, never a boolean."""

    type: Literal['AutonomyLevel']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    model_ref: Optional[str] = None
    """The AutonomyPolicy/model this level belongs to."""
    level_order: Optional[int] = None
    level_name: Optional[str] = None
