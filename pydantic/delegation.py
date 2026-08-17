"""Delegation — generated from schemas/entities/delegation.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Delegation(Entity):
    """The act of granting authority from a delegator to a delegate (CR-7 §19) with explicit scope, constraints, duration, conditions and revocation (G005)."""

    type: Literal['Delegation']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    delegator_ref: Optional[str] = None
    delegate_ref: Optional[str] = None
    authority_ref: Optional[str] = None
    scope: Optional[str] = None
    conditions: Optional[str] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    revocation: Optional[str] = None
    """Revocation conditions or record."""
