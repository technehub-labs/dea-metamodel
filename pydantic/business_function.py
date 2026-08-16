"""Business Function — generated from schemas/entities/business-function.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class BusinessFunction(Entity):
    """A grouping of business capabilities by organisational function; owned by an organizational unit. OpenDEAM v0.2.0, L3 Business Operating Model / Work Organization. Replaces the v2 CAP→OU direct edge: CAP → BF → OU (capabilities grouped by function, function owned by an organizational unit)."""

    type: Literal['BusinessFunction']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    owning_unit_ref: Optional[str] = None
    """Reference to the Organizational Unit that owns this function (BF → OU, cardinality 1:1)."""
