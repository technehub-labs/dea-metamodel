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
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    stakeholder_type: Literal['customer', 'partner', 'supplier', 'regulator', 'investor', 'community', 'board']
    """The relationship class the stakeholder holds with the enterprise. Open set — new stakeholder types (e.g. AI agents, DAO treasuries) can be added without schema changes when enterprise relationships genuinely require them."""
    primary_contact: Optional[str] = None
