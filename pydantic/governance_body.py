"""GovernanceBody — generated from schemas/entities/governance-body.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class GovernanceBody(Entity):
    """A body that sets policy, grants authority, reviews decisions, approves changes, monitors outcomes and enforces constraints (CR-7 §34): Architecture Review Board, AI Governance Board, Data Governance Council, Security Committee, Executive Steering Committee."""

    type: Literal['GovernanceBody']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    body_kind: Optional[str] = None
    mandate: Optional[str] = None
