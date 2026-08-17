"""ScenarioState — generated from schemas/entities/scenario-state.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ScenarioState(Entity):
    """A hypothetical architecture state contained within a Scenario (CR-6 §25/§26). Scenario elements live inside the scenario container — they are never inserted into CurrentState (T007)."""

    type: Literal['ScenarioState']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    scenario_ref: Optional[str] = None
