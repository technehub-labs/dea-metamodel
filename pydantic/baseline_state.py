"""BaselineState — generated from schemas/entities/baseline-state.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class BaselineState(Entity):
    """A formally adopted reference state of the architecture (CR-6 §10) — a declared snapshot, not 'whatever the model happens to contain'. A snapshot may become a baseline (§31); they are not the same thing."""

    type: Literal['BaselineState']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    captured_at: Optional[str] = None
    valid_at: Optional[str] = None
    scope: Optional[str] = None
    source: Optional[str] = None
    adopted_by: Optional[str] = None
    """Authority that formally adopted this baseline."""
