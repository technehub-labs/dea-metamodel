"""TargetState — generated from schemas/entities/target-state.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class TargetState(Entity):
    """An intended future condition of the architecture (CR-6 §12). Target ≠ Current, Target ≠ Planned Change, Target ≠ Forecast (§27). Target-state entities must never be read as current-state (T006)."""

    type: Literal['TargetState']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    target_date: Optional[str] = None
    approved_by: Optional[str] = None
    rationale: Optional[str] = None
