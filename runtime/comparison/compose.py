"""CR-AM-07 Phase 3 — BenchmarkComparison composer.

Composes the Phase 2 distribution and the Phase 3 standings into a
complete BenchmarkComparison document conforming to
assessment-models/schemas/benchmark-comparison.schema.json.

The composer is the ONLY path that assembles a comparison document:
distribution and standings are always derived together from the same
member input, over the same cohort snapshot, so the artifact is
reproducible by construction (CR-AM-07 §10 constraint 1) — a comparison
is a derivation, never a stored truth (CR-AM-07 §13).

Membership hashing: the cohort snapshot's membership_hash is the sha256
of the comma-joined, ascending, canonical score multiset of the admitted
members, with non-numeric scores rendered as "NA" (they remain admitted
to the cohort; they are excluded only from the distribution). When no
member is excluded this equals the distribution's reproducibility hash —
the convention documented in the Phase 1 worked example.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Mapping, Optional, Sequence

from .engine import DistributionEngine, MemberScore, _canonical_score, _is_numeric
from .standings import PercentileMethod, RankingRule, StandingsEngine


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def membership_hash(members: Sequence[MemberScore]) -> str:
    """Content hash of the admitted membership's score multiset."""
    canonical = sorted(
        _canonical_score(float(m.score)) if _is_numeric(m.score) else "NA"
        for m in members
    )
    return "sha256:" + hashlib.sha256(",".join(canonical).encode()).hexdigest()


def compose_comparison(
    cohort: Mapping[str, Any],
    members: Sequence[MemberScore],
    comparison_id: str,
    comparison_axis_measure: Mapping[str, str],
    percentile_method: "PercentileMethod | str" = PercentileMethod.INCLUSIVE,
    ranking_rule: "RankingRule | str" = RankingRule.COMPETITION,
    admitted_ids: Optional[Sequence[str]] = None,
    computed_at: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """Compose a complete BenchmarkComparison document.

    `cohort` is the BenchmarkCohort mapping (providing id, version,
    minimum_sample_size, and comparability_key — inherited verbatim,
    CR-AM-07 §3). Admission and minimum-sample enforcement are inherited
    from the engines (CR-AM-07 §10).
    """
    computed = computed_at or _utc_now()

    distribution = DistributionEngine().compute(
        cohort, members, admitted_ids=admitted_ids
    )
    standings = StandingsEngine().compute(
        cohort,
        members,
        percentile_method=percentile_method,
        ranking_rule=ranking_rule,
        admitted_ids=admitted_ids,
    )

    doc: dict[str, Any] = {
        "id": comparison_id,
        "version": "1.0.0",
        "status": "stable",
        "cohort": {
            "reference": {"id": cohort["id"], "version": cohort["version"]},
            "snapshot": {
                "cohort_version": cohort["version"],
                "snapshot_at": computed,
                "membership_hash": membership_hash(members),
            },
        },
        "comparability_key": cohort["comparability_key"],
        "comparison_axis": {"measure": dict(comparison_axis_measure)},
        "distribution": distribution.as_distribution_dict(),
        "standings": standings.as_standing_dicts(),
        "derivation": {
            "percentile_method": standings.percentile_method.value,
            "ranking_rule": standings.ranking_rule.value,
            "minimum_sample_size": int(cohort["minimum_sample_size"]),
            "minimum_sample_satisfied": True,
            "excluded_members": standings.as_exclusion_dicts(),
            "computed_at": computed,
            "reproducibility_hash": standings.reproducibility_hash,
        },
    }
    if name is not None:
        doc["name"] = name
    if description is not None:
        doc["description"] = description
    return doc
