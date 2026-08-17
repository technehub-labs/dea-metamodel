"""Approval — generated from schemas/entities/approval.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Approval(Entity):
    """An approval act within a human-oversight pattern (CR-7 §25): approver, subject, decision, timestamp. The gate between recommendation and action in approve-before patterns."""

    type: Literal['Approval']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    approver_ref: Optional[str] = None
    subject_ref: Optional[str] = None
    """The action/decision/change being approved."""
    decision: Optional[Literal['granted', 'denied', 'granted-with-conditions']] = None
    approved_at: Optional[str] = None
