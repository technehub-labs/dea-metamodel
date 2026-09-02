"""Business Capability — generated from schemas/entities/business-capability.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class BusinessCapability(Entity):
    """A business capability that an enterprise possesses or requires to produce, enable, control, preserve or realize a meaningful business outcome. Specialization of dea:Capability per ADR-015 / CR-MM-02. The entity type (BusinessCapability) carries the kind information that the deprecated capability_type string used to carry."""

    type: Literal['BusinessCapability']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    capability_layer: Optional[Literal['strategic', 'operational', 'support']] = None
    """Abstraction level of the capability (ADR-015 section 5): strategic, operational, or support. Governed enumeration attribute; orthogonal to kind (entity type) and to ECF coordinates."""
    domain: Optional[str] = None
    """Business domain this capability belongs to."""
