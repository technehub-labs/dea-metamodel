"""Regulation — generated from schemas/entities/regulation.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Regulation(Entity):
    """An externally imposed obligation (law, industry standard with force, contractual mandate) the enterprise must comply with. OpenDEAM v0.3.0 (ADR-0003), L2/Risk & Compliance."""

    type: Literal['Regulation']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    jurisdiction: Optional[str] = None
    """Jurisdiction or authority imposing the obligation."""
