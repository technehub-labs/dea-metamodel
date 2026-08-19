"""Conformance runner (CR-9.10)."""

from __future__ import annotations

from typing import Iterable, List

from .model import ConformanceReport, ConformanceSuite


def run_conformance(suites: Iterable[ConformanceSuite]) -> ConformanceReport:
    """Aggregate conformance suites into a single report.

    The runner is deliberately simple: it does not execute tests — pytest
    does. The runner is the place where class coverage is collected and the
    public report is composed so the contract is auditable independent of any
    test runner.
    """
    return ConformanceReport(suites=list(suites))
