"""CR-AM-07 Phase 1 benchmark comparison conformance tests.

Covers the Phase 1 contract (CR-AM-07 §11 Phase 1): the
BenchmarkComparison schema, the percentile-method and ranking-rule
vocabularies, and the worked example — including the boundary that
comparison consumes CR-AM-06 eligibility without redefining it.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, RefResolver

REPO_ROOT = Path(__file__).resolve().parents[3]

SCHEMA_PATH = "assessment-models/schemas/benchmark-comparison.schema.json"
EXAMPLE_PATH = (
    "assessment-models/benchmark/comparison-examples/"
    "telecom-service-assurance-2026-comparison.yaml"
)
COHORT_PATH = (
    "assessment-models/benchmark/cohort-examples/"
    "telecom-service-assurance-2026.yaml"
)
PERCENTILE_VOCAB_PATH = "assessment-models/vocabulary/percentile-methods.yaml"
RANKING_VOCAB_PATH = "assessment-models/vocabulary/ranking-rules.yaml"


def _preserve_timestamp_strings(loader: yaml.SafeLoader, node: yaml.ScalarNode) -> str:
    """Keep ISO timestamps as raw strings (schema declares date-time strings)."""
    return loader.construct_scalar(node)


yaml.SafeLoader.add_constructor("tag:yaml.org,2002:timestamp", _preserve_timestamp_strings)


def load_yaml(rel_path: str):
    return yaml.safe_load((REPO_ROOT / rel_path).read_text())


def load_json(rel_path: str):
    return json.loads((REPO_ROOT / rel_path).read_text())


def comparison_validator():
    schema = load_json(SCHEMA_PATH)
    common = load_json("assessment-models/schemas/common.schema.json")
    store = {
        "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
        "common.schema.json": common,
    }
    resolver = RefResolver(base_uri="", referrer=schema, store=store)
    return Draft202012Validator(schema, resolver=resolver)


class BenchmarkComparisonSchemaTest(unittest.TestCase):
    """Schema integrity and example validation (CR-AM-07 §11 Phase 1)."""

    def test_schema_parses_as_draft_2020_12(self):
        schema = load_json(SCHEMA_PATH)
        Draft202012Validator.check_schema(schema)

    def test_example_validates_against_schema(self):
        example = load_yaml(EXAMPLE_PATH)
        comparison_validator().validate(example)

    def test_percentile_method_enum_matches_vocabulary(self):
        schema = load_json(SCHEMA_PATH)
        vocab = load_yaml(PERCENTILE_VOCAB_PATH)
        vocab_ids = {v["id"] for v in vocab["values"]}
        enum = set(schema["properties"]["derivation"]["properties"]["percentile_method"]["enum"])
        self.assertEqual(vocab_ids, enum)

    def test_ranking_rule_enum_matches_vocabulary(self):
        schema = load_json(SCHEMA_PATH)
        vocab = load_yaml(RANKING_VOCAB_PATH)
        vocab_ids = {v["id"] for v in vocab["values"]}
        enum = set(schema["properties"]["derivation"]["properties"]["ranking_rule"]["enum"])
        self.assertEqual(vocab_ids, enum)


class BenchmarkComparisonExampleTest(unittest.TestCase):
    """Worked-example internal consistency (CR-AM-07 §5, §6, §10)."""

    @classmethod
    def setUpClass(cls):
        cls.example = load_yaml(EXAMPLE_PATH)

    def test_distribution_n_equals_standings_count(self):
        ex = self.example
        self.assertEqual(ex["distribution"]["n"], len(ex["standings"]))

    def test_peer_position_matches_rank_and_population(self):
        ex = self.example
        n = ex["distribution"]["n"]
        for standing in ex["standings"]:
            self.assertEqual(
                standing["peer_position"], f"{standing['rank']}/{n}",
                f"peer_position must render rank/n for {standing['member']['id']}",
            )

    def test_percentiles_within_bounds(self):
        for standing in self.example["standings"]:
            self.assertGreaterEqual(standing["percentile"], 0)
            self.assertLessEqual(standing["percentile"], 100)

    def test_minimum_sample_size_satisfied(self):
        ex = self.example
        cohort = load_yaml(COHORT_PATH)
        self.assertGreaterEqual(
            ex["distribution"]["n"], cohort["minimum_sample_size"],
            "distribution emitted below the cohort minimum sample size (CR-AM-07 §4)",
        )
        self.assertEqual(
            ex["derivation"]["minimum_sample_size"], cohort["minimum_sample_size"])
        self.assertIs(ex["derivation"]["minimum_sample_satisfied"], True)

    def test_comparability_key_inherited_verbatim_from_cohort(self):
        """CR-AM-07 §3: the comparability key is inherited, never widened."""
        ex = self.example
        cohort = load_yaml(COHORT_PATH)
        self.assertEqual(ex["comparability_key"], cohort["comparability_key"])

    def test_ties_share_percentile_and_rank(self):
        """CR-AM-07 §5/§6: tied members share the same percentile and rank."""
        by_score = {}
        for standing in self.example["standings"]:
            by_score.setdefault(standing["score"], []).append(standing)
        tied = [s for s in by_score.values() if len(s) > 1]
        self.assertTrue(tied, "worked example must exercise the tie rule")
        for group in tied:
            percentiles = {s["percentile"] for s in group}
            ranks = {s["rank"] for s in group}
            self.assertEqual(len(percentiles), 1, "tied members must share a percentile")
            self.assertEqual(len(ranks), 1, "tied members must share a rank")

    def test_competition_ranking_skips_after_tie(self):
        """CR-AM-07 §6: under competition ranking, the rank after a tie skips."""
        ex = self.example
        self.assertEqual(ex["derivation"]["ranking_rule"], "competition")
        ranks = sorted(s["rank"] for s in ex["standings"])
        by_score = {}
        for s in ex["standings"]:
            by_score.setdefault(s["score"], []).append(s)
        tie_size = max(len(g) for g in by_score.values())
        self.assertGreater(tie_size, 1)
        # the rank after a tie of size k must skip k-1 positions
        tie_rank = next(iter({s["rank"] for g in by_score.values()
                              if len(g) == tie_size for s in g}))
        self.assertNotIn(tie_rank + 1, ranks)
        self.assertIn(tie_rank + tie_size, ranks)

    def test_rank_order_is_monotonic_with_score(self):
        standings = sorted(self.example["standings"], key=lambda s: -s["score"])
        ranks = [s["rank"] for s in standings]
        self.assertEqual(ranks, sorted(ranks))


class BenchmarkComparisonBoundaryTest(unittest.TestCase):
    """CR-AM-07 §8 boundary: comparison consumes CR-AM-06, never redefines it."""

    def test_schema_defines_no_eligibility_or_membership_rules(self):
        schema_text = (REPO_ROOT / SCHEMA_PATH).read_text()
        for forbidden in ("eligibility_criteria", "eligibility_reasons",
                          "benchmark-status", "eligibility-reasons"):
            self.assertNotIn(forbidden, schema_text,
                             f"schema must not redefine CR-AM-06 surface: {forbidden}")

    def test_schema_has_no_population_membership_writer(self):
        """The cohort reference is read-only: no population/members array."""
        schema = load_json(SCHEMA_PATH)
        cohort_props = schema["properties"]["cohort"]["properties"]
        self.assertNotIn("population", cohort_props)
        self.assertNotIn("members", cohort_props)

    def test_cohort_reference_resolves(self):
        """The worked example references the CR-AM-06 §6 worked cohort."""
        ex = load_yaml(EXAMPLE_PATH)
        cohort = load_yaml(COHORT_PATH)
        self.assertEqual(ex["cohort"]["reference"]["id"], cohort["id"])
        self.assertEqual(ex["cohort"]["reference"]["version"], cohort["version"])

    def test_no_insight_layer_fields(self):
        """CR-AM-07 §7/§9: insights, narrative, and recommendation are CR-AM-08."""
        schema = load_json(SCHEMA_PATH)
        for forbidden in ("insight", "narrative", "recommendation", "trend"):
            self.assertNotIn(forbidden, schema["properties"],
                             f"{forbidden} is CR-AM-08 scope, not CR-AM-07 Phase 1")


if __name__ == "__main__":
    unittest.main()
