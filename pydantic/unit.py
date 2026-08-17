"""Unit — generated from schemas/entities/unit.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Unit(Entity):
    """A standard quantity in which a measure is expressed (CR-5 §9/Phase 2) — percent, ratio, months, currency, count. Referenced by measures; never embedded in names."""

    type: Literal['Unit']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    symbol: Optional[str] = None
    quantity_kind: Optional[str] = None
    """e.g. ratio, duration, currency, count."""
