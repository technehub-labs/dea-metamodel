"""AggregationRule  :  generated from schemas/entities/aggregation-rule.json.

Do not edit manually  :  regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import Field

from entity import Entity, EntityMetadata, RelationshipInstance



class AggregationRule(Entity):
    """Declares how lower-level results combine into higher-level results (CR-5 §25): weighted averages, minimum thresholds, gating criteria, ceilings, qualitative judgement, evidence sufficiency or rule-based scoring. Never assumed to be a simple arithmetic mean (A009)."""

    type: Literal['AggregationRule']
    lifecycle_status: Optional[Literal['proposed', 'planned', 'active', 'deprecated', 'retired']] = None
    """CR-3R: lifecycle state from metamodel/vocabularies/lifecycle.yaml."""
    external_references: Optional[list[str]] = None
    """CR-3P: identifiers in external systems. Never a substitute for the OpenDEA id (E004)."""
    rule_kind: Optional[Literal['weighted-average', 'minimum-threshold', 'gating', 'ceiling', 'qualitative-judgement', 'evidence-sufficiency', 'rule-based']] = None
    operator: Optional[Literal['SUM', 'COUNT', 'MIN', 'MAX', 'MEAN', 'WEIGHTED_MEAN', 'MEDIAN', 'PERCENTILE', 'RATE', 'RATIO', 'DISTINCT_COUNT']] = None
    """The aggregation operator (CR-MET-005). 11-value enum per the user-supplied binding section 6."""
    weight_basis: Optional[str] = None
    """Required when operator is WEIGHTED_MEAN; the basis for the weighting (e.g. 'numerator_denominator', 'population_size', 'time_period'). CR-MET-005 binding cross-field invariant."""
    unit_semantics: Optional[dict[str, Any]] = None
    """The input and output unit references for the aggregation (CR-MET-005)."""
    weights: Optional[dict[str, Any]] = None
    """Optional criterion/dimension weight map."""
    expression: Optional[str] = None
