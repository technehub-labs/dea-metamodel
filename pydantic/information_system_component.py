"""InformationSystemComponent  :  generated from schemas/entities/information-system-component.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class InformationSystemComponent(Entity):
    """An identifiable architectural constituent of an information system that encapsulates a defined responsibility, structure or execution boundary and participates in the composition or operation of that information system. Abstract kind (D-2 disposition 2026-10-16; CR-019); the concrete ApplicationComponent and IntegrationComponent specialise this kind. The kind covers all first-class IS architectural constituents: it is not merely a technology product, software package, or deployment resource. The ApplicationComponent (APC) and IntegrationComponent (IGC) specialisations retain their component_type discriminator for EGV-004 identity continuity and for catalog search/filter use cases that predate the abstract ISC introduction. Specialises dea:SolutionComponent (the abstract parent kind per ADR-0002 D3). Relationship connections (composition, execution, dependency, service provision, interface exposure) are expressed via the canonical relationship vocabulary (dea:composes, dea:executes, dea:depends-on, dea:provides, dea:exposes) and are not duplicated as inline relationship state on this entity, per CR-3 (no entity contains a relationship that is also independently represented as a relationship instance)."""

    type: Literal['InformationSystemComponent']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
