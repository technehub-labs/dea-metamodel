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
    jurisdiction: Optional[str] = None
    """Jurisdiction or authority imposing the obligation."""
    mandates: Optional[list[str]] = None
    """Control ids required by this regulation. DEPRECATED (CR-002, CR-2F): relationship state is authoritative in the canonical relationship registry (metamodel/registry/relationships.yaml), not in entity schemas. This convenience property will be physically removed in CR-003."""
