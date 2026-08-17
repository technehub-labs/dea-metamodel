"""Controller — generated from schemas/entities/controller.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Controller(Entity):
    """Enforces execution, state and control conditions in an agentic system (CR-7 §46): evaluates state, enforces policy, controls execution, triggers escalation."""

    type: Literal['Controller']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    control_scope: Optional[str] = None
