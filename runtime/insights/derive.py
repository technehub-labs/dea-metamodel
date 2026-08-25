"""CR-AM-08 Phase 2 — rule-driven insight derivation.

Applies an InsightRule to a BenchmarkComparison document for a subject
member and produces an AssessmentInsight document conforming to
assessment-models/schemas/assessment-insight.schema.json.

Derivation contract (CR-AM-08 §6):

- Reproducible: same comparison + same rule version + same subject →
  same insight (modulo generated_at, caller-stampable for tests).
- Evidence fidelity: the derived insight cites exactly the comparison
  it was derived from — derivation never invents or widens evidence.
- Confidence enforcement: the rule's confidence contract is honoured,
  but if the comparison population is below the rule's
  minimum_population, the insight's confidence is downgraded to `low`
  and `small-cohort-size` is added to limitations. Confidence never
  exceeds what the evidence supports (CR-AM-08 §5).
- No match → no insight (None), never a fabricated negative statement.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from .rules import InsightRuleError, validate_rule

_OPERATOR_FNS = {
    "<": lambda v, t: v < t,
    "<=": lambda v, t: v <= t,
    ">": lambda v, t: v > t,
    ">=": lambda v, t: v >= t,
    "==": lambda v, t: v == t,
    "!=": lambda v, t: v != t,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _find_standing(comparison: Mapping[str, Any], member_id: str) -> Mapping[str, Any]:
    for standing in comparison.get("standings", []):
        if standing.get("member", {}).get("id") == member_id:
            return standing
    raise InsightRuleError(
        f"subject {member_id!r} has no standing in comparison "
        f"{comparison.get('id', '<unknown>')!r} — insights derive only over "
        "admitted cohort members (CR-AM-06/07 frozen surfaces)")


def evaluate_condition(
    rule: Mapping[str, Any],
    comparison: Mapping[str, Any],
    member_id: str,
) -> tuple[bool, float, Mapping[str, Any]]:
    """Evaluate the rule's condition for one subject member.

    Returns (matched, metric_value, standing).
    """
    validate_rule(rule)
    standing = _find_standing(comparison, member_id)
    metric = rule["condition"]["metric"]
    value = standing[metric]
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise InsightRuleError(
            f"standing metric {metric!r} for {member_id!r} is not numeric")
    matched = _OPERATOR_FNS[rule["condition"]["operator"]](
        float(value), float(rule["condition"]["threshold"]))
    return matched, float(value), standing


def derive_insight(
    rule: Mapping[str, Any],
    comparison: Mapping[str, Any],
    member_id: str,
    *,
    insight_id: Optional[str] = None,
    generated_at: Optional[str] = None,
    insight_version: str = "1.0.0",
) -> Optional[dict]:
    """Derive an AssessmentInsight document, or None when the rule's
    condition does not match.

    The comparison document must conform to the CR-AM-07
    benchmark-comparison schema (standings + distribution + cohort
    snapshot). The subject must be an admitted member with a standing.
    """
    matched, value, standing = evaluate_condition(rule, comparison, member_id)
    if not matched:
        return None

    distribution = comparison.get("distribution", {})
    population = distribution.get("n")
    confidence_rule = rule["confidence"]
    limitations = list(confidence_rule.get("limitations", []))
    level = confidence_rule["level"]
    minimum = confidence_rule.get("minimum_population")
    if minimum is not None and isinstance(population, int) and population < minimum:
        level = "low"
        if "small-cohort-size" not in limitations:
            limitations.append("small-cohort-size")

    template = rule["result"]["interpretation_template"]
    statement = (
        template
        .replace("{value}", f"{value:g}")
        .replace("{threshold}", f"{float(rule['condition']['threshold']):g}")
        .replace("{peer_position}", standing.get("peer_position", ""))
        .replace("{median}", f"{float(distribution.get('median', 0)):g}")
        .replace("{n}", str(population if population is not None else ""))
    ).strip()

    comparison_ref = {
        "id": comparison["id"],
        "version": comparison["version"],
    }
    member_ref = standing["member"]
    measure_ref = comparison.get("comparison_axis", {}).get("measure")

    subject: dict[str, Any] = {}
    if measure_ref:
        subject["measure"] = measure_ref

    return {
        "id": insight_id
            or f"dea:insight-{_slug(rule['id'])}-{_slug(member_ref['id'])}",
        "version": insight_version,
        "metamodel_version": comparison.get("metamodel_version", "1.0.0"),
        "status": "stable",
        "type": rule["result"]["insight_type"],
        "subject": subject,
        "evidence": {
            "benchmark_comparisons": [comparison_ref],
        },
        "interpretation": {"statement": statement},
        "confidence": {
            "level": level,
            "limitations": limitations,
        },
        "significance": {"level": rule["result"]["significance"]},
        "generation": {
            "method": "rule",
            "generator": "runtime.insights.derive",
        },
        "lineage": {
            "sources": {"benchmark_comparisons": [comparison_ref]},
            "insight_rule": {"id": rule["id"], "version": rule["version"]},
            "generated_at": generated_at or _utc_now(),
        },
    }
