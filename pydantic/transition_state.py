"""TransitionState — generated from schemas/entities/transition-state.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class TransitionState(Entity):
    """An intermediate architecture state between Current and Target (CR-6 §13): real transformation moves Current → Transition 1 → … → Target, never in one jump."""

    type: Literal['TransitionState']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    sequence: Optional[int] = None
    phase_ref: Optional[str] = None
    """The phase/plateaux this state represents (e.g. ERP migration phase 1)."""
