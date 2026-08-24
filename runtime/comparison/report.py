"""CR-AM-07 Phase 4 — comparison report renderer + CLI.

Surfaces a BenchmarkComparison document (a derived artifact, CR-AM-07
§3) as a human-readable text report or canonical JSON. The report is a
*view over the derivation*, never a new truth: it renders exactly the
fields the schema declares and adds no interpretation. Insight,
narrative, trend, and recommendation are CR-AM-08 scope (§7, §8) and
this module deliberately has no vocabulary for them.

Determinism (CR-AM-07 §10 constraint 1): the same comparison document
always renders to the same bytes — standings are ordered by (rank,
member id), and the JSON form is serialised with sorted keys.

CLI:

    python -m runtime.comparison.report <comparison.yaml> [--format text|json]
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Mapping, Sequence

# CR-AM-08 boundary vocabulary — the report must never emit these words.
# Tested in assessment-models/tests/conformance/test_comparison_report.py.
FORBIDDEN_REPORT_TERMS = ("insight", "narrative", "recommendation", "trend")


def _fmt_number(value: Any) -> str:
    """Render a numeric value without trailing-zero noise (82 -> '82')."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return f"{value:g}" if isinstance(value, (int, float)) else str(value)


def _fmt_percentile(value: Any) -> str:
    """Percentiles follow the worked-example convention: one decimal."""
    return f"{float(value):.1f}"


def render_text(comparison: Mapping[str, Any]) -> str:
    """Render a BenchmarkComparison document as a human-readable report."""
    cohort = comparison["cohort"]
    snapshot = cohort["snapshot"]
    distribution = comparison["distribution"]
    derivation = comparison["derivation"]
    key = comparison["comparability_key"]
    axis_measure = comparison["comparison_axis"]["measure"]

    lines: list[str] = []
    lines.append(
        f"Benchmark Comparison: {comparison['id']} "
        f"(v{comparison['version']}, {comparison['status']})"
    )
    if comparison.get("name"):
        lines.append(f"Name: {comparison['name']}")
    lines.append(
        f"Cohort: {cohort['reference']['id']} @ {cohort['reference']['version']} "
        f"(snapshot {snapshot['snapshot_at']}, "
        f"membership {snapshot['membership_hash']})"
    )
    lines.append(
        "Comparability key: "
        + " ".join(
            f"{slot}={key[slot]['id']}"
            for slot in (
                "scenario",
                "capability",
                "measure",
                "assessment_model",
                "scoring_model",
                "maturity_model",
            )
        )
    )
    lines.append(f"Comparison axis: {axis_measure['id']}")
    lines.append("")

    dist_parts = [
        f"min {_fmt_number(distribution['minimum'])}",
        f"q1 {_fmt_number(distribution['q1'])}",
        f"median {_fmt_number(distribution['median'])}",
        f"q3 {_fmt_number(distribution['q3'])}",
        f"max {_fmt_number(distribution['maximum'])}",
        f"mean {_fmt_number(distribution['mean'])}",
    ]
    if distribution.get("standard_deviation") is not None:
        dist_parts.append(f"std_dev {_fmt_number(distribution['standard_deviation'])}")
    if distribution.get("iqr") is not None:
        dist_parts.append(f"iqr {_fmt_number(distribution['iqr'])}")
    lines.append(f"Distribution (n={distribution['n']}):")
    lines.append("  " + "  ".join(dist_parts))
    lines.append("")

    standings = sorted(
        comparison["standings"],
        key=lambda s: (int(s["rank"]), str(s["member"]["id"])),
    )
    lines.append(
        f"Standings (percentile={derivation['percentile_method']}, "
        f"ranking={derivation['ranking_rule']}):"
    )
    lines.append(f"  {'rank':>6}  {'member':<48}  {'score':>7}  {'percentile':>10}  peer")
    for standing in standings:
        lines.append(
            f"  {int(standing['rank']):>6}  "
            f"{standing['member']['id']:<48}  "
            f"{_fmt_number(standing['score']):>7}  "
            f"{_fmt_percentile(standing['percentile']):>10}  "
            f"{standing['peer_position']}"
        )
    lines.append("")

    excluded = derivation.get("excluded_members") or []
    if excluded:
        lines.append(f"Excluded members ({len(excluded)}):")
        for entry in excluded:
            lines.append(f"  - {entry['member']['id']}: {entry['reason']}")
    else:
        lines.append("Excluded members: none")
    lines.append("")

    satisfied = "satisfied" if derivation["minimum_sample_satisfied"] else "NOT satisfied"
    lines.append("Derivation:")
    lines.append(f"  percentile_method:    {derivation['percentile_method']}")
    lines.append(f"  ranking_rule:         {derivation['ranking_rule']}")
    lines.append(
        f"  minimum_sample_size:  {derivation['minimum_sample_size']} ({satisfied})"
    )
    lines.append(f"  computed_at:          {derivation['computed_at']}")
    lines.append(f"  membership_hash:      {snapshot['membership_hash']}")
    lines.append(f"  reproducibility_hash: {derivation['reproducibility_hash']}")
    return "\n".join(lines) + "\n"


def render_json(comparison: Mapping[str, Any]) -> str:
    """Canonical JSON serialisation (sorted keys, 2-space indent)."""
    return json.dumps(comparison, indent=2, sort_keys=True) + "\n"


_RENDERERS = {"text": render_text, "json": render_json}


def main(argv: "Sequence[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m runtime.comparison.report",
        description=(
            "Render a BenchmarkComparison document (CR-AM-07) as a text "
            "report or canonical JSON. The report is a view over the "
            "derived artifact — it adds no interpretation (CR-AM-08)."
        ),
    )
    parser.add_argument("comparison", help="Path to a BenchmarkComparison YAML file")
    parser.add_argument(
        "--format",
        choices=sorted(_RENDERERS),
        default="text",
        help="Report format (default: text)",
    )
    args = parser.parse_args(argv)

    import yaml  # local import: the runtime package already depends on PyYAML

    with open(args.comparison, "r", encoding="utf-8") as fh:
        document = yaml.safe_load(fh)

    sys.stdout.write(_RENDERERS[args.format](document))
    return 0


if __name__ == "__main__":
    sys.exit(main())
