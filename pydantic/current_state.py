"""CurrentState — generated from schemas/entities/current-state.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class CurrentState(Entity):
    """The best authoritative representation of what exists at a specified time (CR-6 §11): actual elements, actual relationships, actual lifecycle states. Planned, proposed, target and hypothetical elements are excluded (T003)."""

    type: Literal['CurrentState']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    as_of: Optional[str] = None
    scope: Optional[str] = None
