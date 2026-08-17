"""LifecycleTransition — generated from schemas/entities/lifecycle-transition.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class LifecycleTransition(Entity):
    """A declared, allowed movement between two LifecycleStates for an entity scope (CR-6 §7; T002). Retired → Active is impossible unless an explicit reactivation transition is declared."""

    type: Literal['LifecycleTransition']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    from_state_ref: Optional[str] = None
    to_state_ref: Optional[str] = None
    entity_scope: Optional[str] = None
    """Entity type or profile this transition applies to."""
    reactivation: Optional[bool] = None
    """T002: marks a transition that legitimately reverses a terminal state."""
