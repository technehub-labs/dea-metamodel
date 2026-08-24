"""CR-AM-07 Phase 4 comparison reporting conformance tests.

Covers the Phase 4 contract (CR-AM-07 §11 Phase 4): surfacing of
comparison outputs through the report renderer and CLI. The report is a
view over the derived artifact — it renders exactly what the schema
declares, deterministically, and carries no CR-AM-08 vocabulary
(insight / narrative / recommendation / trend remain parked).
"""
from __future__ import annotations

import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]

sys.path.insert(0, str(REPO_ROOT))

from runtime.comparison import (  # noqa: E402
    FORBIDDEN_REPORT_TERMS,
    render_json,
    render_text,
)
from runtime.comparison.report import main as report_main  # noqa: E402

EXAMPLE_PATH = (
    REPO_ROOT
    / "assessment-models/benchmark/comparison-examples/"
    / "telecom-service-assurance-2026-comparison.yaml"
)
SCHEMA_PATH = (
    REPO_ROOT / "assessment-models/schemas/benchmark-comparison.schema.json"
)


def _load_example() -> dict:
    with open(EXAMPLE_PATH, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class TestRenderText(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.example = _load_example()
        cls.text = render_text(cls.example)

    def test_header_carries_identity_and_cohort(self) -> None:
        self.assertIn(
            "Benchmark Comparison: dea:comparison-telecom-service-assurance-2026-v1",
            self.text,
        )
        self.assertIn(
            "Cohort: telecom-service-assurance-2026 @ 1.0.0", self.text
        )

    def test_distribution_block_matches_example(self) -> None:
        self.assertIn("Distribution (n=27):", self.text)
        self.assertIn("median 71", self.text)
        self.assertIn("mean 69.2", self.text)

    def test_standings_are_rank_ordered(self) -> None:
        org_b = self.text.index("dea:result-org-b-service-assurance-2026")
        org_a = self.text.index("dea:result-org-a-service-assurance-2026")
        self.assertLess(org_b, org_a)  # rank 1 renders before rank 4
        self.assertIn("88.5", self.text)
        self.assertIn("4/27", self.text)

    def test_tie_at_70_shares_rank_15_and_competition_skips_16(self) -> None:
        rows = [
            line.split()
            for line in self.text.splitlines()
            if "dea:result" in line
        ]
        tie = [row for row in rows if row[2] == "70"]
        self.assertEqual(len(tie), 2)
        for row in tie:
            self.assertEqual(row[0], "15")  # shared rank
        self.assertEqual(tie[0][3], tie[1][3])  # shared percentile
        self.assertNotIn("16/27", self.text)  # competition ranking skips 16
        ranks = {row[0] for row in rows}
        self.assertNotIn("16", ranks)

    def test_derivation_block_carries_hashes(self) -> None:
        self.assertIn("percentile_method:    inclusive", self.text)
        self.assertIn("ranking_rule:         competition", self.text)
        self.assertIn("(satisfied)", self.text)
        self.assertIn("reproducibility_hash:", self.text)

    def test_render_is_deterministic(self) -> None:
        self.assertEqual(self.text, render_text(self.example))

    def test_no_cr_am_08_vocabulary(self) -> None:
        lowered = self.text.lower()
        for term in FORBIDDEN_REPORT_TERMS:
            self.assertNotIn(term, lowered)


class TestRenderJson(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.example = _load_example()
        cls.rendered = render_json(cls.example)

    def test_round_trip_preserves_document(self) -> None:
        self.assertEqual(json.loads(self.rendered), self.example)

    def test_canonical_sorted_keys(self) -> None:
        self.assertEqual(
            self.rendered,
            json.dumps(self.example, indent=2, sort_keys=True) + "\n",
        )

    def test_output_keys_are_schema_declared(self) -> None:
        """The report adds no fields beyond the schema (CR-AM-07 §8)."""
        with open(SCHEMA_PATH, "r", encoding="utf-8") as fh:
            schema = json.load(fh)
        declared = set(schema["properties"])
        self.assertLessEqual(set(json.loads(self.rendered)), declared)


class TestReportCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.example = _load_example()

    def _run(self, argv: list[str]) -> str:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = report_main(argv)
        self.assertEqual(exit_code, 0)
        return buffer.getvalue()

    def test_cli_text_default(self) -> None:
        out = self._run([str(EXAMPLE_PATH)])
        self.assertEqual(out, render_text(self.example))

    def test_cli_json_format(self) -> None:
        out = self._run([str(EXAMPLE_PATH), "--format", "json"])
        self.assertEqual(json.loads(out), self.example)

    def test_cli_rejects_unknown_format(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            report_main([str(EXAMPLE_PATH), "--format", "pdf"])
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
