"""IntegrationInterface  :  generated from schemas/entities/integration-interface.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class IntegrationInterface(Entity):
    """A defined interaction boundary between an information system (or one of its components) and one or more internal or external consumers or providers, specifying the means, protocols, interaction patterns and contractual constraints through which information or functionality is exchanged. The interaction boundary is distinct from the API contract (dea:API) that may specify it. Relationship connections (exposure, use, specification, exchange) are expressed via the canonical relationship vocabulary (dea:exposes, dea:uses, dea:specifies, dea:exchanges) and are not duplicated as inline relationship state on this entity, per CR-3."""

    type: Literal['IntegrationInterface']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
