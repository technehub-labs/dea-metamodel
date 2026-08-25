"""CR-AM-08 Phase 3 assessment gap conformance tests.

Covers the Phase 3 contract (CR-AM-08 §12 Phase 3): the AssessmentGap
schema, the gap-types vocabulary, explicit reference semantics for all
five gap types, and the worked examples — including the never-conflate
rule (reference kind ↔ gap type) and difference arithmetic consistency.
"""
from __future__ import annotations

import glob
import json
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, RefResolver

REPO_ROOT = Path(__file__).resolve().parents[3]

SCHEMA_PATH = "assessment-models/schemas/assessment-gap.schema.json"
GAP_TYPES_PATH = "assessment-models/vocabulary/gap-types.yaml"
EXAMPLES_GLOB = "assessment-models/gaps/examples/*.yaml"
INSIGHT_EXAMPLE_PATH = (
    "assessment-models/insights/examples/"
    "telecom-sa-2026-automation-coverage-gap.yaml"
)
COMPARISON_EXAMPLE_PATH = (
    "assessment-models/benchmark/comparison-examples/"
    "telecom-service-assurance-2026-comparison.yaml"
)

# Gap type → permitted reference kinds (CR-AM-08 §7: never conflated).
REFERENCE_KIND_BY_GAP_TYPE = {
    "target-gap": {"target"},
    "benchmark-gap": {"cohort-median", "cohort-mean", "cohort-quartile"},
    "trend-gap": {"previous-state"},
    "threshold-gap": {"threshold"},
    "coverage-gap": {"required-scope"},
}
# Gap types whose reference must cite its source artifact.
SOURCE_REQUIRED = {"benchmark-gap", "trend-gap"}

FORBIDDEN_TERMS = [
    "project", "program", "initiative", "investment", "business_case",
    "roadmap", "recommendation", "transformation_action",
]
FROZEN_SURFACE_TERMS = ["eligibility_criteria", "benchmark-status", "standings"]


def _preserve_timestamp_strings(loader, node):
    return loader.construct_scalar(node)


yaml.SafeLoader.add_constructor("tag:yaml.org,2002:timestamp", _preserve_timestamp_strings)


def load_yaml(rel_path: str):
    return yaml.safe_load((REPO_ROOT / rel_path).read_text())


def load_json(rel_path: str):
    return json.loads((REPO_ROOT / rel_path).read_text())


def gap_validator():
    schema = load_json(SCHEMA_PATH)
    common = load_json("assessment-models/schemas/common.schema.json")
    store = {
        "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
        "common.schema.json": common,
    }
    resolver = RefResolver(base_uri="", referrer=schema, store=store)
    return Draft202012Validator(schema, resolver=resolver)


def all_examples():
    return sorted(glob.glob(str(REPO_ROOT / EXAMPLES_GLOB)))


class AssessmentGapSchemaTest(unittest.TestCase):
    """Schema integrity and worked-example validation."""

    def test_schema_parses_as_draft_2020_12(self):
        schema = load_json(SCHEMA_PATH)
        self.assertEqual(
            schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_required_fields_match_spec(self):
        schema = load_json(SCHEMA_PATH)
        for field in ("id", "version", "status", "type", "subject",
                      "current", "reference", "difference", "lineage"):
            self.assertIn(field, schema["required"])

    def test_three_worked_examples_land(self):
        paths = all_examples()
        self.assertEqual(3, len(paths),
                         "Phase 3 ships target-gap, benchmark-gap, trend-gap examples")

    def test_all_examples_validate(self):
        validator = gap_validator()
        for path in all_examples():
            doc = yaml.safe_load(Path(path).read_text())
            errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
            self.assertEqual(
                [], [f"{list(e.path)}: {e.message}" for e in errors],
                f"{Path(path).name} must validate")

    def test_missing_reference_is_refused(self):
        doc = load_yaml("assessment-models/gaps/examples/target-gap-automation-maturity.yaml")
        del doc["reference"]
        errors = list(gap_validator().iter_errors(doc))
        self.assertTrue(errors, "a gap without an explicit reference is not canonical")

    def test_missing_difference_is_refused(self):
        doc = load_yaml("assessment-models/gaps/examples/benchmark-gap-automation-coverage.yaml")
        del doc["difference"]
        errors = list(gap_validator().iter_errors(doc))
        self.assertTrue(errors)

    def test_lineage_is_mandatory(self):
        doc = load_yaml("assessment-models/gaps/examples/trend-gap-automation-maturity.yaml")
        del doc["lineage"]
        errors = list(gap_validator().iter_errors(doc))
        self.assertTrue(errors)

    def test_unknown_top_level_keys_are_refused(self):
        doc = load_yaml("assessment-models/gaps/examples/target-gap-automation-maturity.yaml")
        doc["recommendation"] = "invest in automation"  # CR-AM-08 §9 boundary
        errors = list(gap_validator().iter_errors(doc))
        self.assertTrue(errors, "additionalProperties: false must refuse TRANSFORM vocabulary")


class GapVocabularyTest(unittest.TestCase):
    """Gap-type vocabulary parity and reference semantics."""

    def test_gap_types_parity(self):
        schema = load_json(SCHEMA_PATH)
        vocab = {v["id"] for v in load_yaml(GAP_TYPES_PATH)["values"]}
        self.assertEqual(set(schema["properties"]["type"]["enum"]), vocab)

    def test_reference_kinds_cover_all_gap_types(self):
        """Every gap type has at least one permitted reference kind, and
        every reference kind maps back to exactly one gap type family."""
        schema_kinds = set(
            load_json(SCHEMA_PATH)["properties"]["reference"]["properties"]["kind"]["enum"])
        mapped = set().union(*REFERENCE_KIND_BY_GAP_TYPE.values())
        self.assertEqual(schema_kinds, mapped)
        self.assertEqual(set(REFERENCE_KIND_BY_GAP_TYPE),
                         {v["id"] for v in load_yaml(GAP_TYPES_PATH)["values"]})

    def test_examples_use_the_type_consistent_reference_kind(self):
        """Never conflated: each example's reference.kind must be permitted
        for its declared gap type."""
        for path in all_examples():
            doc = yaml.safe_load(Path(path).read_text())
            permitted = REFERENCE_KIND_BY_GAP_TYPE[doc["type"]]
            self.assertIn(doc["reference"]["kind"], permitted,
                          f"{Path(path).name}: {doc['type']} must use {permitted}")

    def test_source_required_types_cite_source(self):
        for path in all_examples():
            doc = yaml.safe_load(Path(path).read_text())
            if doc["type"] in SOURCE_REQUIRED:
                self.assertIn("source", doc["reference"],
                              f"{doc['type']} must cite its source artifact")


class DifferenceArithmeticTest(unittest.TestCase):
    """difference = current − reference; direction consistent (numeric axes)."""

    LEVEL_ORDINAL = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5}

    def _numeric(self, value):
        if isinstance(value, (int, float)):
            return float(value)
        return float(self.LEVEL_ORDINAL[value])

    def test_difference_arithmetic_and_direction(self):
        for path in all_examples():
            doc = yaml.safe_load(Path(path).read_text())
            current = self._numeric(doc["current"]["value"])
            reference = self._numeric(doc["reference"]["value"])
            absolute = doc["difference"]["absolute"]
            self.assertAlmostEqual(current - reference, absolute,
                                   msg=f"{Path(path).name}: absolute must be current − reference")
            expected = "above" if absolute > 0 else "below" if absolute < 0 else "at"
            self.assertEqual(expected, doc["difference"]["direction"],
                             f"{Path(path).name}: direction inconsistent with sign")


class GapLineageConsistencyTest(unittest.TestCase):
    """Cross-artifact consistency with the landed Phase 1/2 artifacts."""

    def test_benchmark_gap_cites_the_landed_comparison(self):
        doc = load_yaml("assessment-models/gaps/examples/benchmark-gap-automation-coverage.yaml")
        comparison = load_yaml(COMPARISON_EXAMPLE_PATH)
        self.assertEqual(comparison["id"], doc["reference"]["source"]["id"])
        cited = {r["id"] for r in doc["lineage"]["sources"]["benchmark_comparisons"]}
        self.assertIn(comparison["id"], cited)

    def test_benchmark_gap_identified_by_landed_insight(self):
        doc = load_yaml("assessment-models/gaps/examples/benchmark-gap-automation-coverage.yaml")
        insight = load_yaml(INSIGHT_EXAMPLE_PATH)
        identified = {r["id"] for r in doc["lineage"]["identified_by"]}
        self.assertIn(insight["id"], identified)

    def test_trend_gap_sources_include_both_states(self):
        doc = load_yaml("assessment-models/gaps/examples/trend-gap-automation-maturity.yaml")
        sources = {r["id"] for r in doc["lineage"]["sources"]["assessment_results"]}
        self.assertIn(doc["reference"]["source"]["id"], sources,
                      "trend-gap lineage must include the previous-state result")


class GapBoundaryGuardTest(unittest.TestCase):
    """CR-AM-08 §9/§10 boundaries for the gap schema."""

    def test_schema_carries_no_action_vocabulary(self):
        text = (REPO_ROOT / SCHEMA_PATH).read_text().lower()
        for term in FORBIDDEN_TERMS:
            self.assertNotIn(term, text,
                             f"gap schema must not contain '{term}' (CR-AM-08 §9)")

    def test_schema_does_not_redefine_frozen_surfaces(self):
        text = (REPO_ROOT / SCHEMA_PATH).read_text()
        for term in FROZEN_SURFACE_TERMS:
            self.assertNotIn(term, text,
                             f"gap schema must not touch frozen surface '{term}'")


if __name__ == "__main__":
    unittest.main()
