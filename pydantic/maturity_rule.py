"""MaturityRule — generated from schemas/entities/maturity-rule.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class MaturityRule(Entity):
    """A framework-defined rule mapping scores or measures to maturity levels, including gating criteria and maturity ceilings (CR-5 §12/§26)."""

    type: Literal['MaturityRule']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    rule_type: Optional[Literal['mapping', 'gating', 'ceiling', 'threshold']] = None
    expression: Optional[str] = None
    """Machine- or human-readable rule expression."""
    applies_to: Optional[str] = None
    """Criterion, dimension or model reference the rule applies to."""
