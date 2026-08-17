"""DecisionOption — generated from schemas/entities/decision-option.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class DecisionOption(Entity):
    """An alternative considered in a Decision (CR-7 §14), with cost, benefit, risk, constraint violations, expected outcome, dependencies, time and confidence. Makes decision-making explicit rather than burying rationale in documents."""

    type: Literal['DecisionOption']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    decision_ref: Optional[str] = None
    cost: Optional[str] = None
    benefit: Optional[str] = None
    risk: Optional[str] = None
    expected_outcome: Optional[str] = None
    selected: Optional[bool] = None
