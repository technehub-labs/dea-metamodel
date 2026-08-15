"""InformationAsset — generated from schemas/entities/information-asset.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class InformationAsset(Entity):
    """Data given context and form for a specific consuming purpose (a report, dashboard, invoice) — distinct from the raw Data Entity it is contextualized from (OpenDEAM v0.5.0, ADR-0005 D4, L4/Information & Knowledge). Catalog: technehub-labs/dea-catalog-information-assets."""

    type: Literal['InformationAsset']
    consumption_form: Optional[Literal['report', 'dashboard', 'document', 'feed', 'other']] = None
    """The form in which the information is consumed."""
    source_data_entities: Optional[list[str]] = None
    """References to Data Entity entries in technehub-labs/dea-catalog-data-entities this asset is contextualized from."""
