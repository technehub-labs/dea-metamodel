"""CR-AM-08 Phase 2 — InsightRule loading and validation.

Governed runtime constants mirror the controlled vocabularies (the
CR-AM-07 standings pattern: enum values ≡ vocabulary YAML ids;
three-way parity is asserted by the conformance suite):

- condition.operator / condition.metric  → insight-rule schema enums
- result.insight_type                    → vocabulary/insight-types.yaml
- result.significance                    → vocabulary/significance-levels.yaml

A rule that fails structural validation is refused with an
InsightRuleError listing every violation — never silently coerced.
"""
from __future__ import annotations

from typing import Any, Mapping

# Governed constant sets (≡ vocabulary YAMLs / schema enums).
INSIGHT_TYPES = frozenset({
    "strength", "weakness", "gap", "risk", "opportunity", "trend",
    "anomaly", "benchmark-gap", "maturity-gap", "coverage-gap",
    "confidence-warning",
})
SIGNIFICANCE_LEVELS = frozenset({"low", "moderate", "material", "high", "critical"})
CONFIDENCE_LEVELS = frozenset({"low", "medium", "high"})
CONDITION_METRICS = frozenset({"percentile", "rank", "score"})
OPERATORS = frozenset({"<", "<=", ">", ">=", "==", "!="})
EVIDENCE_CHANNELS = frozenset({"benchmark_comparisons"})


class InsightRuleError(ValueError):
    """Raised when an InsightRule document is structurally invalid."""


def validate_rule(rule: Mapping[str, Any]) -> Mapping[str, Any]:
    """Structurally validate an InsightRule document; return it unchanged.

    Raises InsightRuleError with every violation found (sorted).
    """
    violations: list[str] = []

    for field in ("id", "version", "status", "condition", "result", "confidence"):
        if field not in rule:
            violations.append(f"missing required field: {field}")

    condition = rule.get("condition", {})
    if isinstance(condition, Mapping):
        if condition.get("evidence") not in EVIDENCE_CHANNELS:
            violations.append(
                f"condition.evidence must be one of {sorted(EVIDENCE_CHANNELS)}")
        if condition.get("metric") not in CONDITION_METRICS:
            violations.append(
                f"condition.metric must be one of {sorted(CONDITION_METRICS)}")
        if condition.get("operator") not in OPERATORS:
            violations.append(
                f"condition.operator must be one of {sorted(OPERATORS)}")
        if not isinstance(condition.get("threshold"), (int, float)) \
                or isinstance(condition.get("threshold"), bool):
            violations.append("condition.threshold must be numeric")
    elif "condition" in rule:
        violations.append("condition must be an object")

    result = rule.get("result", {})
    if isinstance(result, Mapping):
        if result.get("insight_type") not in INSIGHT_TYPES:
            violations.append(
                f"result.insight_type must be one of {sorted(INSIGHT_TYPES)}")
        if result.get("significance") not in SIGNIFICANCE_LEVELS:
            violations.append(
                f"result.significance must be one of {sorted(SIGNIFICANCE_LEVELS)}")
        if not result.get("interpretation_template"):
            violations.append("result.interpretation_template is required")
    elif "result" in rule:
        violations.append("result must be an object")

    confidence = rule.get("confidence", {})
    if isinstance(confidence, Mapping):
        if confidence.get("level") not in CONFIDENCE_LEVELS:
            violations.append(
                f"confidence.level must be one of {sorted(CONFIDENCE_LEVELS)}")
        minimum = confidence.get("minimum_population")
        if minimum is not None and (
                not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 1):
            violations.append("confidence.minimum_population must be an integer >= 1")
    elif "confidence" in rule:
        violations.append("confidence must be an object")

    if violations:
        raise InsightRuleError(
            f"invalid InsightRule {rule.get('id', '<unknown>')}: "
            + "; ".join(sorted(violations)))
    return rule
