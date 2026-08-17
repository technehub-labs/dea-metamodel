"""Action — generated from schemas/entities/action.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Action(Entity):
    """A unit of execution that follows from a Decision (CR-7 §13). Decision ≠ Action: 'approve migration' vs 'execute migration'. Performed by an Actor or Agent (§65) within authority and policy boundaries; reversibility is explicit (§41) and drives control strictness."""

    type: Literal['Action']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    action_kind: Optional[str] = None
    decision_ref: Optional[str] = None
    reversibility: Optional[Literal['reversible', 'irreversible', 'conditionally-reversible']] = None
    materiality: Optional[str] = None
    """e.g. financial, external, safety, legal — drives control strictness (§41)."""
