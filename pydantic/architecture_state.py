"""ArchitectureState — generated from schemas/entities/architecture-state.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ArchitectureState(Entity):
    """A coherent representation of the enterprise architecture at a defined temporal point or condition (CR-6 §9): contains elements, valid-during an interval. Architecture is a time-dependent state of the enterprise, not a static catalogue (§1). Specialized as Baseline/Current/Target/Transition/Scenario states."""

    type: Literal['ArchitectureState']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    state_kind: Optional[Literal['current', 'baseline', 'target', 'transition', 'scenario']] = None
    captured_at: Optional[str] = None
    valid_at: Optional[str] = None
    scope: Optional[str] = None
    source: Optional[str] = None
