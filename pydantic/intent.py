"""Intent — generated from schemas/entities/intent.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Intent(Entity):
    """The desired direction or purpose behind an architectural or organizational decision (CR-7 §3) — e.g. improve customer experience, increase resilience, become AI-enabled. Intent is not a goal metric: Intent motivates Objective, Objective is measured, Outcome is what actually happened (§6)."""

    type: Literal['Intent']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    intent_kind: Optional[str] = None
    """e.g. enterprise, strategic, transformation — composition is supported, never hard-coded (§4)."""
    statement: Optional[str] = None
