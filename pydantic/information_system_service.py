"""InformationSystemService  :  generated from schemas/entities/information-system-service.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class InformationSystemService(Entity):
    """A service provided by an information system or a software platform to a consumer, expressed as a contract about the exchange of capability, functionality or data. Specialises Core dea:Service per the kernel+specialization template (CR-MM-PROC-01 precedent for Process/BusinessProcess; CR-016 precedent for Capability/BusinessCapability; CR-018 precedent for Behavior/InformationSystemFunction; CR-019 precedent for SolutionComponent/InformationSystemComponent). The service contract is operationalised through integration interfaces (deferred to CR-021). Relationship connections (provision, usage, exposure, realises-business-service) are expressed via the canonical relationship vocabulary (dea:provides, dea:uses, dea:exposes, dea:realizes) and are not duplicated as inline relationship state on this entity, per CR-3."""

    type: Literal['InformationSystemService']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
