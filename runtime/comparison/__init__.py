"""CR-AM-07 — comparative benchmarking runtime (Phase 2: distribution; Phase 3: percentile & ranking)."""
from .compose import compose_comparison, membership_hash
from .engine import (
    EXCLUSION_REASONS,
    ComparisonError,
    DistributionEngine,
    DistributionResult,
    ExcludedMember,
    MemberScore,
)
from .standings import (
    PercentileMethod,
    RankingRule,
    Standing,
    StandingsEngine,
    StandingsResult,
)

__all__ = [
    "EXCLUSION_REASONS",
    "ComparisonError",
    "DistributionEngine",
    "DistributionResult",
    "ExcludedMember",
    "MemberScore",
    "PercentileMethod",
    "RankingRule",
    "Standing",
    "StandingsEngine",
    "StandingsResult",
    "compose_comparison",
    "membership_hash",
]
