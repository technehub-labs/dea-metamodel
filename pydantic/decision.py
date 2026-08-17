"""Decision — generated from schemas/entities/decision.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class Decision(Entity):
    """A determination made by an Actor, system or Agent that selects or authorizes a course of action based on information, rules, objectives and constraints (CR-4 §13). Foundation for agentic architecture (CR-7)."""

    type: Literal['Decision']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    statement: Optional[str] = None
    """The decision statement in natural language."""
    rationale: Optional[str] = None
    """CR-7 §11: why this option was selected (G002)."""
    authority_ref: Optional[str] = None
    """CR-7 §18; G001: the Authority under which the decision was made."""
    confidence: Optional[dict[str, Any]] = None
    """CR-7 §17: decision confidence."""
    uncertainty: Optional[str] = None
    """CR-7 §17: known uncertainty, e.g. cost estimate ±20%."""
    assumptions: Optional[list[str]] = None
    """CR-7 §17: assumptions the decision rests on."""
