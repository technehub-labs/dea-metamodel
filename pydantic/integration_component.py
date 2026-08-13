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
    integration_pattern: Optional[Literal['api-gateway', 'message-queue', 'file-transfer', 'event-stream', 'etl', 'rpc', 'graphql-federation']] = None
    """Integration pattern this component implements."""
    direction: Optional[Literal['inbound', 'outbound', 'bidirectional']] = None
    """Direction of data flow."""
