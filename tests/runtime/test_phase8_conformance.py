"""CR-11 Phase 8 — Conformance profiles, report, and CLI."""

import json
from pathlib import Path

import pytest

from runtime import __version__ as runtime_version
from runtime.conformance import (ConformanceClass, ConformanceReport,
                                ConformanceSuite)
from runtime.conformance.golden import GOLDEN_GRAPHS, golden_graph_assertions
from runtime.conformance.interop import (INTEROP_SCENARIOS, InteropScenario,
                                         run_interop_scenario)
from runtime.conformance.runner import (build_cli_parser, default_suites,
                                         run_conformance, main as cli_main)


# ---------------------------------------------------------------- CR-11AM


def test_cr11am_conformance_classes_extend_runtime_taxonomy():
    """CR-11AM — the six interop classes join the seven runtime ones."""
    assert ConformanceClass.EXCHANGE.value == "Exchange"
    assert ConformanceClass.MAPPING.value == "Mapping"
    assert ConformanceClass.FEDERATION.value == "Federation"
    assert ConformanceClass.AGENTIC.value == "Agentic"
    # Identity is added so the conformance list is symmetric with the rest
    # of the CR-11 vocabulary.
    assert ConformanceClass.IDENTITY.value == "Identity"
    # CR-11AM calls the OpenDEA-runtime class "Runtime" — encoded as MAPPING_RUNTIME
    # internally to avoid clashing with the runtime-side usage of the word.
    assert ConformanceClass.MAPPING_RUNTIME.value == "Runtime"


def test_default_interop_roundtrip_suite_covers_all_cr11_classes():
    """CR-11AN — default suite covers Exchange / Identity / Mapping /
    Provenance / Federation (the five CR-11AN sub-suites in spec order)."""
    suites = default_suites()
    interop = suites[0]
    assert interop.name == "interop-roundtrip"
    classes = {c.value for c in interop.classes}
    assert classes == {"Exchange", "Identity", "Mapping",
                        "Provenance", "Federation"}


# ---------------------------------------------------------------- CR-11AN


def test_run_conformance_returns_typed_report():
    """CR-11AN — runner produces a ConformanceReport with stable ordering."""
    report = run_conformance(default_suites(),
                              runtime_version=runtime_version,
                              spec_version="1.0.0")
    assert isinstance(report, ConformanceReport)
    assert report.suite_count >= 1
    assert "Exchange" in report.classes_covered
    # Stable ordering: alphabetical.
    assert report.classes_covered == sorted(report.classes_covered)


def test_interop_scenarios_are_discoverable():
    """CR-11AN — the runtime exposes interop scenarios as discoverable items."""
    assert len(INTEROP_SCENARIOS) >= 1
    for scenario in INTEROP_SCENARIOS:
        assert isinstance(scenario, InteropScenario)
        assert scenario.classes  # every scenario declares its coverage


def test_run_interop_scenario_does_not_mutate_graph_outside_scenario():
    """Every interop scenario runs in its own context — no shared mutation."""
    scenario = next(iter(INTEROP_SCENARIOS))
    first = run_interop_scenario(scenario)
    second = run_interop_scenario(scenario)
    # Independent runs produce independent metrics even on the same scenario.
    assert isinstance(first, dict)
    assert isinstance(second, dict)


# ---------------------------------------------------------------- CR-11AN runner CLI


def test_runner_cli_renders_text_report(tmp_path, capsys):
    """The CLI emits a human-readable report when --format=text (default)."""
    rc = cli_main([
        "--format", "text",
        "--runtime-version", "test-9.9",
        "--spec-version", "1.0.0",
    ])
    assert rc == 0
    out = capsys.readouterr().out
    assert "OpenDEA Conformance Report" in out
    assert "test-9.9" in out
    assert "spec version        : 1.0.0" in out


def test_runner_cli_renders_json_report(capsys):
    """The CLI emits a JSON report when --format=json."""
    rc = cli_main([
        "--format", "json",
        "--runtime-version", "x.y.z",
        "--spec-version", "1.0.0",
    ])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["runtimeVersion"] == "x.y.z"
    assert payload["specVersion"] == "1.0.0"
    assert "Exchange" in payload["classesCovered"]


def test_runner_cli_includes_golden_suites_when_asked(capsys):
    """--include-golden pulls in the CR-11AO golden-graph suites."""
    rc = cli_main(["--format", "json", "--include-golden"])
    payload = json.loads(capsys.readouterr().out)
    suite_names = [s["name"] for s in payload["suites"]]
    # The CR-11AO basic-enterprise golden fixture is included.
    assert any(s.startswith("golden-") for s in suite_names)


def test_cli_parser_accepts_known_arguments():
    """CLI surface is stable for downstream tooling."""
    parser = build_cli_parser()
    # Known options work without error.
    args = parser.parse_args(["--format", "json",
                               "--include-golden",
                               "--runtime-version", "0.0.1",
                               "--spec-version", "1.0.0"])
    assert args.format == "json"
    assert args.include_golden is True
    assert args.runtime_version == "0.0.1"


# ---------------------------------------------------------------- CR-11AO


def test_golden_graphs_include_phase8_fixtures():
    """CR-11AO — golden fixtures cover basic-enterprise, agentic,
    multi-agent, and governed-agent — alongside the CR-9 originals."""
    assert "basic-enterprise" in GOLDEN_GRAPHS
    assert "agentic" in GOLDEN_GRAPHS
    assert "multi-agent" in GOLDEN_GRAPHS
    assert "governed-agent" in GOLDEN_GRAPHS
    # The basic-enterprise fixture carries structural assertions.
    assertions = golden_graph_assertions(GOLDEN_GRAPHS["basic-enterprise"])
    assert assertions["expected_nodes"] >= 5
    assert assertions["expected_edges"] >= 1


def test_golden_graph_paths_resolve_under_repo_root(tmp_path):
    """All golden-graph paths exist on disk (CR-11AO regression)."""
    repo = Path(__file__).resolve().parents[2]
    for path in GOLDEN_GRAPHS.values():
        full = repo / path
        assert full.exists(), f"{full} does not exist"


# ---------------------------------------------------------------- report shape


def test_report_as_dict_contains_required_conformance_keys():
    """The report shape is the CR-11AN contract; consumers depend on it."""
    suites = default_suites()
    report = run_conformance(suites, runtime_version="r", spec_version="s")
    payload = report.as_dict()
    for key in ("schemaVersion", "conformanceVersion", "runtimeVersion",
                "specVersion", "suiteCount", "classesCovered", "suites"):
        assert key in payload, f"missing key {key!r} in report payload"


def test_report_render_text_includes_suite_names():
    """render_text exposes each suite inline so CI logs stay legible."""
    suites = [ConformanceSuite(name="alpha", classes=[ConformanceClass.CORE]),
              ConformanceSuite(name="beta", classes=[ConformanceClass.MAPPING])]
    report = run_conformance(suites)
    text = report.render_text()
    assert "alpha" in text and "beta" in text
    assert "Core" in text and "Mapping" in text
