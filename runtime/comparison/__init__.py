"""CR-AM-07 — comparative benchmarking runtime (Phase 2: distribution; Phase 3: percentile & ranking; Phase 4: report surfacing)."""
from .compose import compose_comparison, membership_hash

# Phase 4 report exports are lazy (PEP 562) so that
# `python -m runtime.comparison.report` does not trip the runpy
# "found in sys.modules" warning from an eager package-level import.
_LAZY_EXPORTS = ("render_text", "render_json", "FORBIDDEN_REPORT_TERMS")


def __getattr__(name: str):
    if name in _LAZY_EXPORTS:
        from . import report

        return getattr(report, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
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
    "render_json",
    "render_text",
    "FORBIDDEN_REPORT_TERMS",
]
