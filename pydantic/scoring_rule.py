"""ScoringRule — generated from schemas/entities/scoring-rule.json.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class ScoringRule(Entity):
    """Declares how measures become scores within a framework (CR-5 §11/§25). The framework — not the ontology — defines the transformation."""

    type: Literal['ScoringRule']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    input_measure_refs: Optional[list[str]] = None
    expression: Optional[str] = None
    output_scale_ref: Optional[str] = None
