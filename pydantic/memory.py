"""Memory — generated from schemas/entities/memory.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Memory(Entity):
    """Information retained by or for an Agent (CR-7 §33). The DEA concern is governance, not AI implementation detail: what is retained, who controls it, how long, under what policy, who can access it."""

    type: Literal['Memory']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    memory_kind: Optional[Literal['working', 'persistent', 'episodic', 'semantic']] = None
    retention: Optional[str] = None
    """Retention policy reference or period."""
    controller_ref: Optional[str] = None
    """Who controls the memory."""
