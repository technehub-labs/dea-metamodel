"""Orchestrator — generated from schemas/entities/orchestrator.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Orchestrator(Entity):
    """Coordinates multiple actors, agents, services and workflows toward a goal (CR-7 §46/§47). Distinct from Agent (bounded cognitive/action role) and Controller (enforces execution/state/control conditions) — the three are never collapsed (§46)."""

    type: Literal['Orchestrator']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    coordination_scope: Optional[str] = None
