"""IntangibleResource — generated from schemas/entities/intangible-resource.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class IntangibleResource(Entity):
    """Legally protected non-physical economic value (patents, trademarks, brand equity, licenses). Specializes Resource (OpenDEAM v0.5.0, ADR-0005 D3, L3/Enterprise Resources). Catalog: technehub-labs/dea-catalog-intangible-resources."""

    type: Literal['IntangibleResource']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    protection_type: Optional[Literal['patent', 'trademark', 'copyright', 'trade-secret', 'license', 'brand', 'other']] = None
    """Legal protection type — the governance dimension for this specialization (ADR-0005 D3)."""
    protection_expiry: Optional[str] = None
    """ISO 8601 date on which the legal protection lapses, where applicable."""
