"""FinancialResource — generated from schemas/entities/financial-resource.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class FinancialResource(Entity):
    """Liquid or near-liquid economic value the enterprise holds (accounts, instruments, funding lines). Specializes Resource (OpenDEAM v0.5.0, ADR-0005 D3, L3/Enterprise Resources). Catalog: technehub-labs/dea-catalog-financial-resources."""

    type: Literal['FinancialResource']
    liquidity: Optional[Literal['cash', 'near-liquid', 'credit-facility', 'instrument', 'other']] = None
    """Liquidity classification — the governance dimension for this specialization (ADR-0005 D3)."""
    currency: Optional[str] = None
    """ISO 4217 currency code, where applicable."""
