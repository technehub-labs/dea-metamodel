"""CR-AM-07 Phase 2 — distribution engine.

The distribution engine answers the first half of "how do we compare
it?" (CR-AM-07 §4): given the ADMITTED members of a BenchmarkCohort,
compute the population statistics on the declared comparison axis.

Boundaries enforced by construction:

* Eligibility is the only door (CR-AM-07 §10 constraint 4). The engine
  accepts only admitted cohort members; a member id outside the admitted
  set is a governance breach and raises ComparisonError — it is never
  silently dropped or silently included.
* Minimum sample size is enforced BEFORE any statistic is emitted
  (CR-AM-07 §4, §10 constraint 3). Below the cohort's
  minimum_sample_size the computation is refused with an explicit
  reason — small-population statistics are never silently emitted.
* Missing data is N/A, not zero (CR-AM-07 §10 constraint 2; CR-AM-05).
  A member without a numeric score on the comparison axis is excluded
  from the distribution with an explicit machine-actionable reason
  (vocabulary/comparison-exclusion-reasons.yaml) — never imputed.
* Derivation is reproducible (CR-AM-07 §10 constraint 1). The
  reproducibility hash is a pure function of the canonically sorted
  score multiset; same input always produces the same distribution.
* No standings. Percentile, rank, and peer position are CR-AM-07
  Phase 3 — this engine emits distribution + exclusions only.

Quartile convention: exclusive median-of-halves (the lower/upper halves
exclude the median for odd n). This matches the Phase 1 worked example
(benchmark/comparison-examples/telecom-service-assurance-2026-comparison.yaml)
and is exercised by the conformance suite as a regression pin.
"""
from __future__ import annotations

import hashlib
import statistics
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

# Mirrors vocabulary/comparison-exclusion-reasons.yaml.
EXCLUSION_REASONS = (
    "score-missing-on-comparison-axis",
    "score-not-numeric",
)


class ComparisonError(ValueError):
    """Raised when a comparison derivation violates a CR-AM-07 contract."""


@dataclass(frozen=True)
class MemberScore:
    """One admitted cohort member's value on the comparison axis.

    `score` may be None or non-numeric: such members are excluded from
    the distribution with an explicit reason (missing data is N/A,
    never zero — CR-AM-07 §10 constraint 2).
    """

    member: str
    score: Any
    member_version: str = "1.0.0"


@dataclass(frozen=True)
class ExcludedMember:
    """An admitted member excluded from the distribution, with reason."""

    member: str
    reason: str


@dataclass(frozen=True)
class DistributionResult:
    """The Phase 2 output: distribution statistics + exclusions + hash.

    Deliberately carries NO standings — percentile, rank, and peer
    position are Phase 3 (CR-AM-07 §5, §6).
    """

    n: int
    minimum: float
    q1: float
    median: float
    q3: float
    maximum: float
    mean: float
    standard_deviation: Optional[float]
    iqr: float
    excluded_members: tuple[ExcludedMember, ...] = field(default_factory=tuple)
    reproducibility_hash: str = ""

    def as_distribution_dict(self) -> dict:
        """Schema-shaped distribution block (benchmark-comparison.schema.json)."""
        dist: dict[str, Any] = {
            "n": self.n,
            "minimum": self.minimum,
            "q1": self.q1,
            "median": self.median,
            "q3": self.q3,
            "maximum": self.maximum,
            "mean": self.mean,
            "iqr": self.iqr,
        }
        if self.standard_deviation is not None:
            dist["standard_deviation"] = self.standard_deviation
        return dist

    def as_exclusion_dicts(self) -> list[dict]:
        """Schema-shaped excluded_members entries."""
        return [
            {"member": {"id": e.member}, "reason": e.reason}
            for e in self.excluded_members
        ]


def _is_numeric(value: Any) -> bool:
    # bool is a subclass of int; a boolean is never a score.
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _median_of_halves(sorted_values: Sequence[float]) -> tuple[float, float, float]:
    """Exclusive median-of-halves quartiles.

    Returns (q1, median, q3). For odd n the median is excluded from both
    halves; for even n the halves split the population evenly.
    """
    n = len(sorted_values)
    median = float(statistics.median(sorted_values))
    if n == 1:
        return median, median, median
    mid = n // 2
    lower = sorted_values[:mid]
    upper = sorted_values[mid:] if n % 2 == 0 else sorted_values[mid + 1:]
    return float(statistics.median(lower)), median, float(statistics.median(upper))


def _canonical_score(value: float) -> str:
    """Canonical string form of a score for the reproducibility hash."""
    return f"{value:g}"


class DistributionEngine:
    """Computes cohort distributions over admitted members (CR-AM-07 §4)."""

    def compute(
        self,
        cohort: Mapping[str, Any],
        members: Sequence[MemberScore],
        admitted_ids: Optional[Sequence[str]] = None,
    ) -> DistributionResult:
        """Compute the distribution for a cohort's admitted members.

        Raises ComparisonError when:
        * a member id is outside `admitted_ids` (eligibility is the only
          door — CR-AM-07 §10 constraint 4); or
        * the included population falls below the cohort's
          minimum_sample_size (statistics are refused, never silently
          emitted — CR-AM-07 §4).
        """
        minimum_sample_size = int(cohort.get("minimum_sample_size", 1))
        if minimum_sample_size < 1:
            raise ComparisonError(
                f"cohort minimum_sample_size must be >= 1, got {minimum_sample_size}"
            )

        admitted = set(admitted_ids) if admitted_ids is not None else None
        included: list[tuple[str, float]] = []
        excluded: list[ExcludedMember] = []

        for member in members:
            if admitted is not None and member.member not in admitted:
                raise ComparisonError(
                    f"member {member.member!r} is not an admitted cohort member — "
                    "eligibility is the only door (CR-AM-07 §10)"
                )
            if member.score is None:
                excluded.append(
                    ExcludedMember(member.member, "score-missing-on-comparison-axis")
                )
            elif not _is_numeric(member.score):
                excluded.append(ExcludedMember(member.member, "score-not-numeric"))
            else:
                included.append((member.member, float(member.score)))

        if len(included) < minimum_sample_size:
            raise ComparisonError(
                f"distribution refused: included population n={len(included)} "
                f"is below the cohort minimum_sample_size={minimum_sample_size} "
                "(CR-AM-07 §4, §10)"
            )

        scores = sorted(score for _, score in included)
        n = len(scores)
        q1, median, q3 = _median_of_halves(scores)
        mean = round(statistics.fmean(scores), 6)
        std = round(statistics.stdev(scores), 6) if n >= 2 else None
        digest = hashlib.sha256(
            ",".join(_canonical_score(s) for s in scores).encode()
        ).hexdigest()

        return DistributionResult(
            n=n,
            minimum=scores[0],
            q1=q1,
            median=median,
            q3=q3,
            maximum=scores[-1],
            mean=mean,
            standard_deviation=std,
            iqr=q3 - q1,
            excluded_members=tuple(excluded),
            reproducibility_hash=f"sha256:{digest}",
        )
