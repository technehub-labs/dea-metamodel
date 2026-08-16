"""PhysicalResource — generated from schemas/entities/physical-resource.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class PhysicalResource(Entity):
    """Tangible asset requiring an ongoing maintenance regime (equipment, vehicles, premises, inventory stock). Specializes Resource (OpenDEAM v0.5.0, ADR-0005 D3, L3/Enterprise Resources). Catalog: technehub-labs/dea-catalog-physical-resources."""

    type: Literal['PhysicalResource']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    maintenance_regime: Optional[str] = None
    """The upkeep schedule/regime this asset requires — the governance dimension for this specialization (ADR-0005 D3)."""
    location: Optional[str] = None
    """Where the asset is sited (site, region, or logical location)."""
