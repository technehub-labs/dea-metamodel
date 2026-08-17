"""DecisionRecord — generated from schemas/entities/decision-record.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class DecisionRecord(Entity):
    """The audit record of a Decision (CR-7 §11): who/what decided, what, why, on what evidence, under what authority, among which alternatives, with what consequences."""

    type: Literal['DecisionRecord']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    decision_ref: Optional[str] = None
    recorded_at: Optional[str] = None
    authority_ref: Optional[str] = None
    rationale: Optional[str] = None
