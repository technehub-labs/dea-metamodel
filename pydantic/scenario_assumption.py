"""ScenarioAssumption — generated from schemas/entities/scenario-assumption.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ScenarioAssumption(Entity):
    """A declared assumption under which a Scenario holds (CR-6 §25). Assumptions make the difference between a scenario and a target explicit and auditable."""

    type: Literal['ScenarioAssumption']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    scenario_ref: Optional[str] = None
    statement: Optional[str] = None
