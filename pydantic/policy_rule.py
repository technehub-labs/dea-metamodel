"""PolicyRule — generated from schemas/entities/policy-rule.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class PolicyRule(Entity):
    """An atomic, evaluable rule within a Policy (CR-7 §7/§38) — the unit policy enforcement evaluates."""

    type: Literal['PolicyRule']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    policy_ref: Optional[str] = None
    expression: Optional[str] = None
    applies_to: Optional[str] = None
