"""CR-AM-07 Phase 3 — percentile & ranking engine.

The standings engine answers the second half of "how do we compare it?"
(CR-AM-07 §5, §6): given the admitted members of a BenchmarkCohort and
the distribution computed in Phase 2, assign each member a percentile, a
rank, and a peer position (e.g. 4/27).

Boundaries enforced by construction:

* Declared methods only (CR-AM-07 §5, §6). The percentile method
  (inclusive / exclusive) and ranking rule (competition / dense) are
  explicit parameters drawn from the governed vocabularies
  (vocabulary/percentile-methods.yaml, vocabulary/ranking-rules.yaml).
* Ties share standing (CR-AM-07 §5, §6). Members with equal scores share
  the same percentile and the same rank; ties are never broken by member
  identity. Under competition ranking the ranks after a tie skip
  (1,2,2,4); under dense ranking they do not (1,2,2,3).
* Eligibility is the only door (CR-AM-07 §10 constraint 4) — the same
  admission guard as the distribution engine.
* Missing data is N/A (CR-AM-07 §10 constraint 2) — the same exclusion
  rules as the distribution engine; excluded members carry reasons and
  never receive a standing.
* Reproducibility (CR-AM-07 §10 constraint 1) — standings are a pure
  function of the included score multiset; the reproducibility hash is
  shared with the distribution over the same inputs.

Percentile conventions (percentile = share of the population strictly
below the member):

* inclusive — below / (n − 1) × 100; the maximum member reaches 100.
  For n = 1 the single member is defined as percentile 100.0.
* exclusive — below / (n + 1) × 100; no member reaches 0 or 100.

Percentiles are rounded to one decimal place (the worked-example
convention).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional, Sequence

from .engine import (
    ComparisonError,
    DistributionEngine,
    DistributionResult,
    ExcludedMember,
    MemberScore,
    _is_numeric,
)


class PercentileMethod(str, Enum):
    """Governed percentile methods (vocabulary/percentile-methods.yaml)."""

    INCLUSIVE = "inclusive"
    EXCLUSIVE = "exclusive"


class RankingRule(str, Enum):
    """Governed ranking rules (vocabulary/ranking-rules.yaml)."""

    COMPETITION = "competition"
    DENSE = "dense"


def _percentile_method(value: "PercentileMethod | str") -> PercentileMethod:
    if isinstance(value, PercentileMethod):
        return value
    try:
        return PercentileMethod(str(value))
    except ValueError:
        raise ComparisonError(
            f"unknown percentile_method {value!r} — must be one of "
            f"{[m.value for m in PercentileMethod]} "
            "(vocabulary/percentile-methods.yaml)"
        ) from None


def _ranking_rule(value: "RankingRule | str") -> RankingRule:
    if isinstance(value, RankingRule):
        return value
    try:
        return RankingRule(str(value))
    except ValueError:
        raise ComparisonError(
            f"unknown ranking_rule {value!r} — must be one of "
            f"{[r.value for r in RankingRule]} (vocabulary/ranking-rules.yaml)"
        ) from None


@dataclass(frozen=True)
class Standing:
    """One member's standing within the cohort (CR-AM-07 §5, §6)."""

    member: str
    score: float
    percentile: float
    rank: int
    peer_position: str
    member_version: str = "1.0.0"

    def as_dict(self) -> dict:
        """Schema-shaped standings entry (benchmark-comparison.schema.json)."""
        return {
            "member": {"id": self.member, "version": self.member_version},
            "score": self.score,
            "percentile": self.percentile,
            "rank": self.rank,
            "peer_position": self.peer_position,
        }


@dataclass(frozen=True)
class StandingsResult:
    """Phase 3 output: per-member standings + exclusions + shared hash."""

    standings: tuple[Standing, ...]
    excluded_members: tuple[ExcludedMember, ...]
    n: int
    percentile_method: PercentileMethod
    ranking_rule: RankingRule
    reproducibility_hash: str

    def as_standing_dicts(self) -> list[dict]:
        return [s.as_dict() for s in self.standings]

    def as_exclusion_dicts(self) -> list[dict]:
        return [
            {"member": {"id": e.member}, "reason": e.reason}
            for e in self.excluded_members
        ]


class StandingsEngine:
    """Computes percentile, rank, and peer position per member."""

    def __init__(self) -> None:
        self._distribution = DistributionEngine()

    def compute(
        self,
        cohort: Mapping[str, Any],
        members: Sequence[MemberScore],
        percentile_method: "PercentileMethod | str" = PercentileMethod.INCLUSIVE,
        ranking_rule: "RankingRule | str" = RankingRule.COMPETITION,
        admitted_ids: Optional[Sequence[str]] = None,
    ) -> StandingsResult:
        """Compute standings for a cohort's admitted members.

        Minimum-sample enforcement and admission guarding are inherited
        from the distribution engine (CR-AM-07 §10): below-threshold
        populations are refused, and non-admitted members raise
        ComparisonError.
        """
        method = _percentile_method(percentile_method)
        rule = _ranking_rule(ranking_rule)

        distribution = self._distribution.compute(
            cohort, members, admitted_ids=admitted_ids
        )

        included: list[tuple[str, float, str]] = [
            (m.member, float(m.score), m.member_version)
            for m in members
            if _is_numeric(m.score)
        ]
        scores = [score for _, score, _ in included]
        n = len(scores)

        standings = tuple(
            self._standing(member, score, version, scores, n, method, rule)
            for member, score, version in included
        )
        return StandingsResult(
            standings=standings,
            excluded_members=distribution.excluded_members,
            n=n,
            percentile_method=method,
            ranking_rule=rule,
            reproducibility_hash=distribution.reproducibility_hash,
        )

    @staticmethod
    def _standing(
        member: str,
        score: float,
        member_version: str,
        scores: Sequence[float],
        n: int,
        method: PercentileMethod,
        rule: RankingRule,
    ) -> Standing:
        below = sum(1 for s in scores if s < score)
        if method is PercentileMethod.INCLUSIVE:
            # n == 1: the only member is defined as percentile 100.0.
            percentile = 100.0 if n == 1 else below / (n - 1) * 100
        else:
            percentile = below / (n + 1) * 100
        percentile = round(percentile, 1)

        if rule is RankingRule.COMPETITION:
            rank = 1 + sum(1 for s in scores if s > score)
        else:
            rank = 1 + len({s for s in scores if s > score})

        return Standing(
            member=member,
            score=score,
            percentile=percentile,
            rank=rank,
            peer_position=f"{rank}/{n}",
            member_version=member_version,
        )
