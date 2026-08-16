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
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    service_type: Literal['internal', 'external', 'partner', 'public']
    """Service exposure scope."""
    sla: Optional[dict[str, Any]] = None
