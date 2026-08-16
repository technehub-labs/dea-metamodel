"""BusinessService — generated from schemas/entities/business-service.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class BusinessService(Entity):
    """A service exposed to the business or to external consumers."""

    type: Literal['BusinessService']
    service_type: Literal['internal', 'external', 'partner', 'public']
    """Service exposure scope."""
    owner: Optional[str] = None
    """DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
    provided_by: Optional[list[str]] = None
    """SolutionComponent IDs that provide this service. DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
    consumed_by: Optional[list[str]] = None
    """SolutionComponent or Process IDs that consume this service. DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
    sla: Optional[dict[str, Any]] = None
