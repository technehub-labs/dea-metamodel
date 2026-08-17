"""LifecycleState — generated from schemas/entities/lifecycle-state.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class LifecycleState(Entity):
    """An explicit operational state of a lifecycle-aware entity (CR-6 §7). Lifecycle state is defined by the entity type or profile — never blindly uniform — and is distinct from maturity level (§8): an Application can be Active while its Capability is assessed at Level 3."""

    type: Literal['LifecycleState']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    state_name: Optional[str] = None
    sequence: Optional[int] = None
    terminal: Optional[bool] = None
    """Whether this state ends the lifecycle absent an explicit reactivation transition (T002)."""
