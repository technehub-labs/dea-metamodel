"""CR-AM-07 Phase 3 percentile & ranking conformance tests.

Covers the Phase 3 contract (CR-AM-07 §11 Phase 3): per-member
percentile, rank, and peer position with declared tie rules and
reproducibility — including the regression pin that the engine
reproduces the Phase 1 worked example's standings exactly, and the
composition guard that a composed BenchmarkComparison validates against
the Phase 1 schema.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, RefResolver

REPO_ROOT = Path(__file__).resolve().parents[3]

import sys

sys.path.insert(0, str(REPO_ROOT))

from runtime.comparison import (  # noqa: E402
    ComparisonError,
    MemberScore,
    PercentileMethod,
    RankingRule,
    StandingsEngine,
    compose_comparison,
)

EXAMPLE_PATH = (
    "assessment-models/benchmark/comparison-examples/"
    "telecom-service-assurance-2026-comparison.yaml"
)
SCHEMA_PATH = "assessment-models/schemas/benchmark-comparison.schema.json"
PERCENTILE_VOCAB_PATH = "assessment-models/vocabulary/percentile-methods.yaml"
RANKING_VOCAB_PATH = "assessment-models/vocabulary/ranking-rules.yaml"


def load_yaml(rel_path: str):
    return yaml.safe_load((REPO_ROOT / rel_path).read_text())


def load_json(rel_path: str):
    return json.loads((REPO_ROOT / rel_path).read_text())


def cohort(minimum_sample_size: int = 2) -> dict:
    return {"minimum_sample_size": minimum_sample_size}


class WorkedExampleStandingsRegressionTest(unittest.TestCase):
    """The engine must reproduce the Phase 1 worked example standings."""

    @classmethod
    def setUpClass(cls):
        cls.example = load_yaml(EXAMPLE_PATH)
        members = [
            MemberScore(s["member"]["id"], s["score"])
            for s in cls.example["standings"]
        ]
        cls.result = StandingsEngine().compute(cohort(), members)

    def _expected(self):
        return {s["member"]["id"]: s for s in self.example["standings"]}

    def test_reproduces_every_standing(self):
        expected = self._expected()
        self.assertEqual(len(self.result.standings), len(expected))
        for standing in self.result.standings:
            exp = expected[standing.member]
            self.assertEqual(standing.score, exp["score"], standing.member)
            self.assertEqual(standing.percentile, exp["percentile"], standing.member)
            self.assertEqual(standing.rank, exp["rank"], standing.member)
            self.assertEqual(standing.peer_position, exp["peer_position"], standing.member)

    def test_reproduces_methods_and_hash(self):
        derivation = self.example["derivation"]
        self.assertEqual(
            self.result.percentile_method.value, derivation["percentile_method"])
        self.assertEqual(self.result.ranking_rule.value, derivation["ranking_rule"])
        self.assertEqual(
            self.result.reproducibility_hash, derivation["reproducibility_hash"])


class TieRuleTest(unittest.TestCase):
    """CR-AM-07 §5/§6: ties share standing; ranking rule governs the skip."""

    MEMBERS = [
        MemberScore("a", 90), MemberScore("b", 80), MemberScore("c", 80),
        MemberScore("d", 70),
    ]

    def test_competition_ranking_skips_after_tie(self):
        result = StandingsEngine().compute(
            cohort(), self.MEMBERS, ranking_rule=RankingRule.COMPETITION)
        ranks = {s.member: s.rank for s in result.standings}
        self.assertEqual(ranks, {"a": 1, "b": 2, "c": 2, "d": 4})

    def test_dense_ranking_does_not_skip(self):
        result = StandingsEngine().compute(
            cohort(), self.MEMBERS, ranking_rule=RankingRule.DENSE)
        ranks = {s.member: s.rank for s in result.standings}
        self.assertEqual(ranks, {"a": 1, "b": 2, "c": 2, "d": 3})

    def test_ties_share_percentile(self):
        result = StandingsEngine().compute(cohort(), self.MEMBERS)
        tied = [s for s in result.standings if s.member in ("b", "c")]
        self.assertEqual(len({s.percentile for s in tied}), 1)


class PercentileMethodTest(unittest.TestCase):
    """CR-AM-07 §5: percentile semantics under both declared methods."""

    MEMBERS = [MemberScore(m, s) for m, s in (("a", 90), ("b", 80), ("c", 70))]

    def test_inclusive_maximum_reaches_100(self):
        result = StandingsEngine().compute(
            cohort(), self.MEMBERS, percentile_method=PercentileMethod.INCLUSIVE)
        by_member = {s.member: s for s in result.standings}
        self.assertEqual(by_member["a"].percentile, 100.0)
        self.assertEqual(by_member["b"].percentile, 50.0)
        self.assertEqual(by_member["c"].percentile, 0.0)

    def test_exclusive_never_reaches_bounds(self):
        result = StandingsEngine().compute(
            cohort(), self.MEMBERS, percentile_method=PercentileMethod.EXCLUSIVE)
        by_member = {s.member: s for s in result.standings}
        self.assertEqual(by_member["a"].percentile, 50.0)
        self.assertEqual(by_member["b"].percentile, 25.0)
        self.assertEqual(by_member["c"].percentile, 0.0)

    def test_single_member_inclusive_is_100(self):
        result = StandingsEngine().compute(
            cohort(minimum_sample_size=1), [MemberScore("a", 42)],
            percentile_method=PercentileMethod.INCLUSIVE)
        self.assertEqual(result.standings[0].percentile, 100.0)
        self.assertEqual(result.standings[0].peer_position, "1/1")

    def test_unknown_percentile_method_rejected(self):
        with self.assertRaises(ComparisonError):
            StandingsEngine().compute(
                cohort(), self.MEMBERS, percentile_method="nearest-rank")

    def test_unknown_ranking_rule_rejected(self):
        with self.assertRaises(ComparisonError):
            StandingsEngine().compute(
                cohort(), self.MEMBERS, ranking_rule="ordinal")

    def test_methods_accept_string_values(self):
        result = StandingsEngine().compute(
            cohort(), self.MEMBERS,
            percentile_method="inclusive", ranking_rule="competition")
        self.assertEqual(result.percentile_method, PercentileMethod.INCLUSIVE)
        self.assertEqual(result.ranking_rule, RankingRule.COMPETITION)


class BoundaryAndIntegrityTest(unittest.TestCase):
    """CR-AM-07 §10 guards carried through Phase 3."""

    def test_non_admitted_member_raises(self):
        members = [MemberScore("a", 80), MemberScore("x", 90)]
        with self.assertRaises(ComparisonError):
            StandingsEngine().compute(cohort(), members, admitted_ids=["a"])

    def test_excluded_members_get_no_standing(self):
        members = [MemberScore("a", 80), MemberScore("b", None), MemberScore("c", 90)]
        result = StandingsEngine().compute(cohort(), members)
        self.assertEqual({s.member for s in result.standings}, {"a", "c"})
        self.assertEqual(
            [e.reason for e in result.excluded_members],
            ["score-missing-on-comparison-axis"],
        )

    def test_enums_match_vocabularies(self):
        pct_vocab = {v["id"] for v in load_yaml(PERCENTILE_VOCAB_PATH)["values"]}
        rank_vocab = {v["id"] for v in load_yaml(RANKING_VOCAB_PATH)["values"]}
        self.assertEqual({m.value for m in PercentileMethod}, pct_vocab)
        self.assertEqual({r.value for r in RankingRule}, rank_vocab)

    def test_computation_is_deterministic(self):
        members = [MemberScore(m, s) for m, s in (("a", 90), ("b", 80), ("c", 80))]
        first = StandingsEngine().compute(cohort(), members)
        second = StandingsEngine().compute(cohort(), members)
        self.assertEqual(first, second)


class ComposeComparisonTest(unittest.TestCase):
    """The composer emits schema-valid BenchmarkComparison documents."""

    def test_composed_document_validates_against_schema(self):
        cohort_doc = load_yaml(
            "assessment-models/benchmark/cohort-examples/"
            "telecom-service-assurance-2026.yaml"
        )
        example = load_yaml(EXAMPLE_PATH)
        members = [
            MemberScore(s["member"]["id"], s["score"])
            for s in example["standings"]
        ]
        doc = compose_comparison(
            cohort_doc,
            members,
            comparison_id="dea:comparison-telecom-service-assurance-2026-v1",
            comparison_axis_measure={"id": "automation-coverage", "version": "1.0.0"},
            computed_at="2026-08-24T00:00:00Z",
        )

        schema = load_json(SCHEMA_PATH)
        common = load_json("assessment-models/schemas/common.schema.json")
        store = {
            "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
            "common.schema.json": common,
        }
        resolver = RefResolver(base_uri="", referrer=schema, store=store)
        Draft202012Validator(schema, resolver=resolver).validate(doc)

    def test_composed_document_reproduces_worked_example(self):
        """Same inputs through the composer reproduce the canonical example."""
        cohort_doc = load_yaml(
            "assessment-models/benchmark/cohort-examples/"
            "telecom-service-assurance-2026.yaml"
        )
        example = load_yaml(EXAMPLE_PATH)
        members = [
            MemberScore(s["member"]["id"], s["score"])
            for s in example["standings"]
        ]
        doc = compose_comparison(
            cohort_doc,
            members,
            comparison_id="dea:comparison-telecom-service-assurance-2026-v1",
            comparison_axis_measure={"id": "automation-coverage", "version": "1.0.0"},
            computed_at="2026-08-24T00:00:00Z",
        )
        # Exact for the integer-exact statistics; the worked example rounds
        # mean/std to one decimal, so compare those at its precision.
        for key in ("n", "minimum", "q1", "median", "q3", "maximum", "iqr"):
            self.assertEqual(doc["distribution"][key], example["distribution"][key])
        for key in ("mean", "standard_deviation"):
            self.assertAlmostEqual(
                doc["distribution"][key], example["distribution"][key], places=1)
        self.assertEqual(doc["standings"], example["standings"])
        self.assertEqual(doc["comparability_key"], example["comparability_key"])
        self.assertEqual(
            doc["derivation"]["reproducibility_hash"],
            example["derivation"]["reproducibility_hash"],
        )
        self.assertEqual(
            doc["cohort"]["snapshot"]["membership_hash"],
            example["cohort"]["snapshot"]["membership_hash"],
        )


if __name__ == "__main__":
    unittest.main()
