"""DecisionCriterion — generated from schemas/entities/decision-criterion.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class DecisionCriterion(Entity):
    """A criterion by which decision options are evaluated (CR-7 §15): strategic alignment, cost, risk, time-to-value, security, regulatory compliance, customer impact, complexity, resilience."""

    type: Literal['DecisionCriterion']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    criterion_kind: Optional[str] = None
    weight: Optional[float] = None
    evaluation_guidance: Optional[str] = None
