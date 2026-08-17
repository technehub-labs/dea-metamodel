"""ArchitectureDelta — generated from schemas/entities/architecture-delta.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ArchitectureDelta(Entity):
    """The semantic difference between two architecture states (CR-6 §32): added, removed, modified, replaced, reclassified elements and relationship changes. The native answer to 'what must change to move from here to there?' — the bridge between DMM, target architecture, transformation and roadmaps (§33). Deltas are derived, never hand-authored."""

    type: Literal['ArchitectureDelta']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    from_state_ref: Optional[str] = None
    to_state_ref: Optional[str] = None
    changes: Optional[list[str]] = None
    derived: Optional[Literal[True]] = None
