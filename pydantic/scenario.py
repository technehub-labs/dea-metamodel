"""Scenario — generated from schemas/entities/scenario.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Scenario(Entity):
    """A hypothetical architecture exploration under a defined set of assumptions (CR-6 §25) — e.g. cloud-first vs hybrid vs on-premise modernization. A scenario is not necessarily the approved target, and must never contaminate the authoritative architecture (T007)."""

    type: Literal['Scenario']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    scenario_status: Optional[Literal['draft', 'under-evaluation', 'adopted-as-target', 'rejected', 'archived']] = None
