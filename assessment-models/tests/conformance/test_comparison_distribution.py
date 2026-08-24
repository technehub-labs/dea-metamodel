"""CR-AM-07 Phase 2 distribution engine conformance tests.

Covers the Phase 2 contract (CR-AM-07 §11 Phase 2): cohort statistics
over admitted members, minimum-sample enforcement, and missing-data
exclusion with explicit reasons — including the regression pin that the
engine reproduces the Phase 1 worked example exactly.
"""
from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]

import sys

sys.path.insert(0, str(REPO_ROOT))

from runtime.comparison import (  # noqa: E402
    EXCLUSION_REASONS,
    ComparisonError,
    DistributionEngine,
    MemberScore,
)

EXAMPLE_PATH = (
    "assessment-models/benchmark/comparison-examples/"
    "telecom-service-assurance-2026-comparison.yaml"
)
COHORT_PATH = (
    "assessment-models/benchmark/cohort-examples/"
    "telecom-service-assurance-2026.yaml"
)
VOCAB_PATH = "assessment-models/vocabulary/comparison-exclusion-reasons.yaml"


def load_yaml(rel_path: str):
    return yaml.safe_load((REPO_ROOT / rel_path).read_text())


def cohort(minimum_sample_size: int = 2) -> dict:
    return {"minimum_sample_size": minimum_sample_size}


class WorkedExampleRegressionTest(unittest.TestCase):
    """The engine must reproduce the Phase 1 worked example exactly."""

    @classmethod
    def setUpClass(cls):
        cls.example = load_yaml(EXAMPLE_PATH)
        cls.engine = DistributionEngine()

    def _compute(self):
        members = [
            MemberScore(s["member"]["id"], s["score"])
            for s in self.example["standings"]
        ]
        return self.engine.compute(cohort(), members)

    def test_reproduces_distribution_statistics(self):
        result = self._compute()
        dist = self.example["distribution"]
        self.assertEqual(result.n, dist["n"])
        self.assertEqual(result.minimum, dist["minimum"])
        self.assertEqual(result.q1, dist["q1"])
        self.assertEqual(result.median, dist["median"])
        self.assertEqual(result.q3, dist["q3"])
        self.assertEqual(result.maximum, dist["maximum"])
        self.assertAlmostEqual(result.mean, dist["mean"], places=1)
        self.assertAlmostEqual(
            result.standard_deviation, dist["standard_deviation"], places=1)
        self.assertEqual(result.iqr, dist["iqr"])

    def test_reproduces_reproducibility_hash(self):
        """CR-AM-07 §10 constraint 1: same snapshot → same hash."""
        result = self._compute()
        self.assertEqual(
            result.reproducibility_hash,
            self.example["derivation"]["reproducibility_hash"],
        )

    def test_computation_is_deterministic(self):
        first, second = self._compute(), self._compute()
        self.assertEqual(first, second)


class MinimumSampleTest(unittest.TestCase):
    """CR-AM-07 §4, §10 constraint 3: statistics refused below threshold."""

    def setUp(self):
        self.engine = DistributionEngine()

    def test_refuses_below_minimum_sample_size(self):
        members = [MemberScore("dea:result-a", 80)]
        with self.assertRaises(ComparisonError) as ctx:
            self.engine.compute(cohort(minimum_sample_size=2), members)
        self.assertIn("minimum_sample_size=2", str(ctx.exception))
        self.assertIn("n=1", str(ctx.exception))

    def test_refuses_empty_population(self):
        with self.assertRaises(ComparisonError):
            self.engine.compute(cohort(minimum_sample_size=1), [])

    def test_exclusions_can_push_below_threshold(self):
        """An excluded member does not count toward the sample size."""
        members = [MemberScore("dea:result-a", 80), MemberScore("dea:result-b", None)]
        with self.assertRaises(ComparisonError) as ctx:
            self.engine.compute(cohort(minimum_sample_size=2), members)
        self.assertIn("n=1", str(ctx.exception))

    def test_invalid_minimum_sample_size_rejected(self):
        with self.assertRaises(ComparisonError):
            self.engine.compute(cohort(minimum_sample_size=0),
                                [MemberScore("dea:result-a", 80)])


class ExclusionTest(unittest.TestCase):
    """CR-AM-07 §10 constraint 2: missing data is N/A, never imputed."""

    def setUp(self):
        self.engine = DistributionEngine()

    def test_missing_score_excluded_with_reason(self):
        members = [
            MemberScore("dea:result-a", 80),
            MemberScore("dea:result-b", 90),
            MemberScore("dea:result-c", None),
        ]
        result = self.engine.compute(cohort(), members)
        self.assertEqual(result.n, 2)
        self.assertEqual(len(result.excluded_members), 1)
        excluded = result.excluded_members[0]
        self.assertEqual(excluded.member, "dea:result-c")
        self.assertEqual(excluded.reason, "score-missing-on-comparison-axis")

    def test_non_numeric_score_excluded_with_reason(self):
        members = [
            MemberScore("dea:result-a", 80),
            MemberScore("dea:result-b", "high"),
            MemberScore("dea:result-c", 90),
        ]
        result = self.engine.compute(cohort(), members)
        self.assertEqual(result.n, 2)
        self.assertEqual(
            result.excluded_members[0].reason, "score-not-numeric")

    def test_boolean_score_is_not_numeric(self):
        """bool is an int subclass in Python; a boolean is never a score."""
        members = [
            MemberScore("dea:result-a", 80),
            MemberScore("dea:result-b", True),
            MemberScore("dea:result-c", 90),
        ]
        result = self.engine.compute(cohort(), members)
        self.assertEqual(result.n, 2)
        self.assertEqual(
            result.excluded_members[0].reason, "score-not-numeric")

    def test_exclusion_dicts_are_schema_shaped(self):
        members = [MemberScore("dea:result-a", 80), MemberScore("dea:result-b", None)]
        result = self.engine.compute(cohort(minimum_sample_size=1), members)
        exclusions = result.as_exclusion_dicts()
        self.assertEqual(
            exclusions,
            [{"member": {"id": "dea:result-b"},
              "reason": "score-missing-on-comparison-axis"}],
        )

    def test_exclusion_reasons_match_vocabulary(self):
        vocab = load_yaml(VOCAB_PATH)
        vocab_ids = {v["id"] for v in vocab["values"]}
        self.assertEqual(set(EXCLUSION_REASONS), vocab_ids)


class AdmissionGuardTest(unittest.TestCase):
    """CR-AM-07 §10 constraint 4: eligibility is the only door."""

    def test_non_admitted_member_raises(self):
        engine = DistributionEngine()
        members = [MemberScore("dea:result-a", 80), MemberScore("dea:result-x", 90)]
        with self.assertRaises(ComparisonError) as ctx:
            engine.compute(cohort(), members, admitted_ids=["dea:result-a"])
        self.assertIn("not an admitted cohort member", str(ctx.exception))

    def test_all_admitted_passes(self):
        engine = DistributionEngine()
        members = [MemberScore("dea:result-a", 80), MemberScore("dea:result-b", 90)]
        result = engine.compute(
            cohort(), members, admitted_ids=["dea:result-a", "dea:result-b"])
        self.assertEqual(result.n, 2)


class DistributionShapeTest(unittest.TestCase):
    """Schema-shape and statistical-correctness guards."""

    def setUp(self):
        self.engine = DistributionEngine()

    def test_distribution_dict_matches_schema_keys(self):
        members = [MemberScore(f"dea:result-{i}", float(v))
                   for i, v in enumerate((10, 20, 30, 40))]
        result = self.engine.compute(cohort(), members)
        dist = result.as_distribution_dict()
        self.assertLessEqual(
            set(dist),
            {"n", "minimum", "q1", "median", "q3", "maximum", "mean",
             "standard_deviation", "iqr"},
        )

    def test_even_count_quartiles(self):
        # [10, 20, 30, 40]: median 25; halves [10,20]/[30,40] → q1 15, q3 35
        members = [MemberScore(f"dea:result-{i}", float(v))
                   for i, v in enumerate((10, 20, 30, 40))]
        result = self.engine.compute(cohort(), members)
        self.assertEqual((result.q1, result.median, result.q3), (15.0, 25.0, 35.0))

    def test_single_member_distribution(self):
        result = self.engine.compute(
            cohort(minimum_sample_size=1), [MemberScore("dea:result-a", 42)])
        self.assertEqual(result.n, 1)
        self.assertEqual(
            (result.minimum, result.q1, result.median, result.q3, result.maximum),
            (42.0, 42.0, 42.0, 42.0, 42.0),
        )
        self.assertIsNone(result.standard_deviation)
        self.assertNotIn("standard_deviation", result.as_distribution_dict())

    def test_no_standings_in_phase_2_output(self):
        """CR-AM-07 §11: percentile/rank/peer position are Phase 3."""
        members = [MemberScore(f"dea:result-{i}", float(v)) for i, v in enumerate((50, 60))]
        result = self.engine.compute(cohort(), members)
        for forbidden in ("standings", "percentile", "rank", "peer_position"):
            self.assertFalse(hasattr(result, forbidden),
                             f"Phase 2 must not emit {forbidden}")


if __name__ == "__main__":
    unittest.main()
