"""Conformance runner + CLI (CR-9.10 + CR-11AN).

The runtime aggregate is a small typed function — pytest does the
actual execution. The CLI binding exists so a downstream implementation
can produce a conformance report without inventing a runner. The
shipped default suites are:

* **Interop test suite** — round-trips through exchange, mapping,
  identity, provenance, federation. The runtime ships this suite
  pre-populated; consumers can add their own.
* **Golden dataset suite** — every :class:`GoldenGraph` loaded with its
  expected structural assertions (CR-11AO).
"""
from __future__ import annotations

import argparse
import sys
from typing import Iterable, List, Optional

from .interop import INTEROP_SCENARIOS
from .golden import GOLDEN_GRAPHS, golden_graph_assertions
from .model import (ConformanceClass, ConformanceReport, ConformanceSuite)


def default_suites() -> List[ConformanceSuite]:
    """Return the runtime-shipped conformance suites (CR-11AN + CR-11AO)."""
    interop = ConformanceSuite(
        name="interop-roundtrip",
        classes=[
            ConformanceClass.EXCHANGE,
            ConformanceClass.MAPPING,
            ConformanceClass.IDENTITY,
            ConformanceClass.PROVENANCE,
            ConformanceClass.FEDERATION,
        ],
        description=("Round-trip CR-11/CR-9 surfaces: exchange, mapping, "
                    "identity, provenance, and federation."),
    )
    return [interop]


def _golden_suites() -> List[ConformanceSuite]:
    """Build a suite per registered golden graph (CR-11AO)."""
    suites: List[ConformanceSuite] = []
    for name, _path in GOLDEN_GRAPHS.items():
        suites.append(ConformanceSuite(
            name=f"golden-{name}",
            classes=[ConformanceClass.CORE, ConformanceClass.VALIDATION],
            description=f"Golden dataset fixture: {name}",
        ))
    return suites


def run_conformance(
    suites: Optional[Iterable[ConformanceSuite]] = None,
    *,
    runtime_version: str = "0.0.0",
    spec_version: str = "1.0.0",
) -> ConformanceReport:
    """Aggregate conformance suites into a single report.

    The runner is deliberately simple: it does not execute tests — pytest
    does. The runner is the place where class coverage is collected and
    the public report is composed so the contract is auditable
    independent of any test runner.
    """
    suites_used = list(suites) if suites is not None else default_suites()
    return ConformanceReport.build(
        suites=suites_used,
        runtime_version=runtime_version,
        spec_version=spec_version,
    )


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="opendea-conformance",
        description=("OpenDEA CR-11AN conformance report command. "
                     "Renders a unified conformance report from the "
                     "shipped + golden suites; does not execute tests."))
    parser.add_argument("--format", choices=("json", "text"), default="text",
                        help="Output format (default: text)")
    parser.add_argument("--runtime-version", default="0.0.0",
                        help="Runtime version stamp (default 0.0.0)")
    parser.add_argument("--spec-version", default="1.0.0",
                        help="Spec version stamp (default 1.0.0)")
    parser.add_argument("--include-golden", action="store_true",
                        help="Include golden-dataset suites (CR-11AO)")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_cli_parser()
    args = parser.parse_args(argv)
    suites = default_suites()
    if args.include_golden:
        suites.extend(_golden_suites())
    report = run_conformance(
        suites=suites,
        runtime_version=args.runtime_version,
        spec_version=args.spec_version,
    )
    if args.format == "json":
        print(report.render_json())
    else:
        print(report.render_text())
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
