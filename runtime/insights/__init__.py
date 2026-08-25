"""CR-AM-08 — assessment insights runtime (Phase 2: InsightRule derivation)."""
from .rules import (
    CONDITION_METRICS,
    CONFIDENCE_LEVELS,
    EVIDENCE_CHANNELS,
    INSIGHT_TYPES,
    OPERATORS,
    SIGNIFICANCE_LEVELS,
    InsightRuleError,
    validate_rule,
)
from .derive import derive_insight, evaluate_condition
