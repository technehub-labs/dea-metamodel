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
    provided_by: Optional[list[str]] = None
    """SolutionComponent IDs that provide this service."""
    consumed_by: Optional[list[str]] = None
    """SolutionComponent or Process IDs that consume this service."""
    sla: Optional[dict[str, Any]] = None
