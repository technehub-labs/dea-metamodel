"""Ecosystem Actor — generated from schemas/entities/ecosystem-actor.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class EcosystemActor(Entity):
    """External party that actively exchanges value with the enterprise — supplier, customer, regulator, partner. OpenDEAM v0.2.0, L1 Ecosystem & Value Network / External Parties. Distinct from Stakeholder (affected/engaged, may be passive): an Ecosystem Actor is defined by an active value-exchange relationship."""

    type: Literal['EcosystemActor']
    actor_kind: Literal['customer', 'supplier', 'partner', 'regulator', 'platform', 'competitor']
    """The primary exchange role the actor plays in the enterprise's value network."""
    exchange_directions: Optional[list[str]] = None
    """Directions of value flow between this actor and the enterprise."""
    digital_identity_ref: Optional[str] = None
    """Reference to the Digital Identity representing this actor (EA → DI realization)."""
