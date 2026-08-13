"""Stakeholder — generated from schemas/entities/stakeholder.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Stakeholder(Entity):
    """An external or affected party whose relationship with the enterprise is engaged in or affected by enterprise processes. Stakeholders are NOT internal performers — internal performers (employees, teams, systems, AI agents) are Actors, not Stakeholders. Catalog: technehub-labs/dea-catalog-stakeholders."""

    type: Literal['Stakeholder']
    stakeholder_type: Literal['customer', 'partner', 'supplier', 'regulator', 'investor', 'community', 'board']
    """The relationship class the stakeholder holds with the enterprise. Open set — new stakeholder types (e.g. AI agents, DAO treasuries) can be added without schema changes when enterprise relationships genuinely require them."""
    relationship_direction: Optional[Literal['inbound', 'outbound', 'bidirectional', 'governance']] = None
    """How value flows between the stakeholder and the enterprise: inbound (enterprise receives value), outbound (enterprise delivers value), bidirectional (co-created/shared), governance (accountability/compliance)."""
    primary_contact: Optional[str] = None
    external_identifiers: Optional[dict[str, Any]] = None
    """External IDs — registration numbers, LEI, DUNS, ticker, etc. Free-form key/value."""
