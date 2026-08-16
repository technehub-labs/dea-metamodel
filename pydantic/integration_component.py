"""IntegrationComponent — generated from schemas/entities/integration-component.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class IntegrationComponent(Entity):
    """A component that bridges systems via APIs, message queues, file transfers, or event streams. A subClass of SolutionComponent with component_type='integration'. Catalog: technehub-labs/dea-catalog-application-components (shared with ApplicationComponent)."""

    type: Literal['IntegrationComponent']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    integration_pattern: Optional[Literal['api-gateway', 'message-queue', 'file-transfer', 'event-stream', 'etl', 'rpc', 'graphql-federation']] = None
    """Integration pattern this component implements."""
    direction: Optional[Literal['inbound', 'outbound', 'bidirectional']] = None
    """Direction of data flow."""
