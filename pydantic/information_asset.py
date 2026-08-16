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
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    consumption_form: Optional[Literal['report', 'dashboard', 'document', 'feed', 'other']] = None
    """The form in which the information is consumed."""
