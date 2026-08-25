"""CR-AM-08 Phase 1 assessment insight conformance tests.

Covers the Phase 1 contract (CR-AM-08 §12 Phase 1): the AssessmentInsight
schema, the insight-type / significance-level / generation-method
vocabularies, and the worked example — including the boundaries that an
insight is an interpretation of evidence (never a fact, never an action)
and that CR-AM-06/07 surfaces stay frozen.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, RefResolver

REPO_ROOT = Path(__file__).resolve().parents[3]

SCHEMA_PATH = "assessment-models/schemas/assessment-insight.schema.json"
COMPARISON_SCHEMA_PATH = "assessment-models/schemas/benchmark-comparison.schema.json"
EXAMPLE_PATH = (
    "assessment-models/insights/examples/"
    "telecom-sa-2026-automation-coverage-gap.yaml"
)
COMPARISON_EXAMPLE_PATH = (
    "assessment-models/benchmark/comparison-examples/"
    "telecom-service-assurance-2026-comparison.yaml"
)
INSIGHT_TYPES_PATH = "assessment-models/vocabulary/insight-types.yaml"
SIGNIFICANCE_PATH = "assessment-models/vocabulary/significance-levels.yaml"
GENERATION_PATH = "assessment-models/vocabulary/insight-generation-methods.yaml"

# CR-AM-08 §9 non-goals: the TRANSFORM vocabulary must never appear in the
# insight schema (also guards description prose, not just field names).
FORBIDDEN_TERMS = [
    "project", "program", "initiative", "investment", "business_case",
    "roadmap", "recommendation", "transformation_action",
]
# CR-AM-06/07 frozen surfaces: the insight schema consumes results, views,
# and comparisons — it never redefines eligibility or comparison.
FROZEN_SURFACE_TERMS = ["eligibility_criteria", "benchmark-status", "standings"]


def _preserve_timestamp_strings(loader: yaml.SafeLoader, node: yaml.ScalarNode) -> str:
    """Keep ISO timestamps as raw strings (schema declares date-time strings)."""
    return loader.construct_scalar(node)


yaml.SafeLoader.add_constructor("tag:yaml.org,2002:timestamp", _preserve_timestamp_strings)


def load_yaml(rel_path: str):
    return yaml.safe_load((REPO_ROOT / rel_path).read_text())


def load_json(rel_path: str):
    return json.loads((REPO_ROOT / rel_path).read_text())


def insight_validator():
    schema = load_json(SCHEMA_PATH)
    common = load_json("assessment-models/schemas/common.schema.json")
    store = {
        "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
        "common.schema.json": common,
    }
    resolver = RefResolver(base_uri="", referrer=schema, store=store)
    return Draft202012Validator(schema, resolver=resolver)


def vocab_ids(rel_path: str) -> set:
    return {v["id"] for v in load_yaml(rel_path)["values"]}


class AssessmentInsightSchemaTest(unittest.TestCase):
    """Schema integrity and example validation (CR-AM-08 §12 Phase 1)."""

    def test_schema_parses_as_draft_2020_12(self):
        schema = load_json(SCHEMA_PATH)
        self.assertEqual(
            schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_required_fields_match_spec(self):
        schema = load_json(SCHEMA_PATH)
        for field in ("id", "version", "status", "type", "subject",
                      "evidence", "interpretation", "confidence",
                      "generation", "lineage"):
            self.assertIn(field, schema["required"])

    def test_worked_example_validates(self):
        doc = load_yaml(EXAMPLE_PATH)
        errors = sorted(insight_validator().iter_errors(doc), key=lambda e: list(e.path))
        self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors])

    def test_evidence_is_mandatory(self):
        doc = load_yaml(EXAMPLE_PATH)
        del doc["evidence"]
        errors = list(insight_validator().iter_errors(doc))
        self.assertTrue(errors, "insight without evidence must be refused")

    def test_empty_evidence_is_refused(self):
        doc = load_yaml(EXAMPLE_PATH)
        doc["evidence"] = {}
        errors = list(insight_validator().iter_errors(doc))
        self.assertTrue(errors, "evidence with no source artifact must be refused")

    def test_lineage_is_mandatory(self):
        doc = load_yaml(EXAMPLE_PATH)
        del doc["lineage"]
        errors = list(insight_validator().iter_errors(doc))
        self.assertTrue(errors, "insight without lineage is not canonical")

    def test_interpretation_statement_is_mandatory(self):
        doc = load_yaml(EXAMPLE_PATH)
        doc["interpretation"] = {}
        errors = list(insight_validator().iter_errors(doc))
        self.assertTrue(errors)

    def test_unknown_top_level_keys_are_refused(self):
        doc = load_yaml(EXAMPLE_PATH)
        doc["recommendation"] = "invest in automation"  # CR-AM-08 §9 boundary
        errors = list(insight_validator().iter_errors(doc))
        self.assertTrue(errors, "additionalProperties: false must refuse TRANSFORM vocabulary")


class VocabularyParityTest(unittest.TestCase):
    """Schema enums must equal the governed vocabularies, both directions
    (the CR-AM-05 separator lesson applied to CR-AM-08)."""

    def test_insight_types_parity(self):
        schema = load_json(SCHEMA_PATH)
        self.assertEqual(set(schema["properties"]["type"]["enum"]),
                         vocab_ids(INSIGHT_TYPES_PATH))

    def test_significance_levels_parity(self):
        schema = load_json(SCHEMA_PATH)
        self.assertEqual(set(schema["properties"]["significance"]["properties"]["level"]["enum"]),
                         vocab_ids(SIGNIFICANCE_PATH))

    def test_generation_methods_parity(self):
        schema = load_json(SCHEMA_PATH)
        self.assertEqual(set(schema["properties"]["generation"]["properties"]["method"]["enum"]),
                         vocab_ids(GENERATION_PATH))

    def test_no_domain_specific_insight_types(self):
        for vid in vocab_ids(INSIGHT_TYPES_PATH):
            self.assertNotIn("readiness", vid)
            self.assertNotIn("autonomous-network", vid)
            self.assertNotIn("techco", vid)


class BoundaryGuardTest(unittest.TestCase):
    """CR-AM-08 §9/§10: no TRANSFORM vocabulary; CR-AM-06/07 frozen
    surfaces untouched."""

    def test_schema_carries_no_action_vocabulary(self):
        text = (REPO_ROOT / SCHEMA_PATH).read_text().lower()
        for term in FORBIDDEN_TERMS:
            self.assertNotIn(term, text,
                             f"insight schema must not contain '{term}' (CR-AM-08 §9)")

    def test_schema_does_not_redefine_frozen_surfaces(self):
        text = (REPO_ROOT / SCHEMA_PATH).read_text()
        for term in FROZEN_SURFACE_TERMS:
            self.assertNotIn(term, text,
                             f"insight schema must not touch CR-AM-06/07 surface '{term}'")

    def test_comparison_schema_gains_no_insight_vocabulary(self):
        """The CR-AM-07 comparison schema is frozen for CR-AM-08: insights
        consume comparisons, never modify them."""
        text = (REPO_ROOT / COMPARISON_SCHEMA_PATH).read_text().lower()
        for term in ("insight", "narrative", "recommendation"):
            self.assertNotIn(term, text,
                             f"comparison schema must not gain '{term}' (CR-AM-08 boundary)")

    def test_confidence_and_significance_are_independent_axes(self):
        schema = load_json(SCHEMA_PATH)
        self.assertIn("confidence", schema["properties"])
        self.assertIn("significance", schema["properties"])
        conf = set(schema["properties"]["confidence"]["properties"]["level"]["enum"])
        sig = set(schema["properties"]["significance"]["properties"]["level"]["enum"])
        self.assertEqual({"low", "medium", "high"}, conf)
        self.assertNotEqual(conf, sig, "significance must not reuse the confidence scale")


class WorkedExampleConsistencyTest(unittest.TestCase):
    """Cross-artifact consistency of the Phase 1 worked example."""

    def test_example_cites_the_landed_comparison(self):
        doc = load_yaml(EXAMPLE_PATH)
        comparison = load_yaml(COMPARISON_EXAMPLE_PATH)
        cited = {r["id"] for r in doc["evidence"]["benchmark_comparisons"]}
        self.assertIn(comparison["id"], cited)

    def test_lineage_mirrors_evidence(self):
        doc = load_yaml(EXAMPLE_PATH)
        ev = {r["id"] for r in doc["evidence"]["benchmark_comparisons"]}
        lin = {r["id"] for r in doc["lineage"]["sources"]["benchmark_comparisons"]}
        self.assertEqual(ev, lin, "every cited artifact must appear in lineage")

    def test_rule_generated_insight_carries_rule_reference(self):
        doc = load_yaml(EXAMPLE_PATH)
        if doc["generation"]["method"] == "rule":
            rule = doc["lineage"].get("insight_rule")
            self.assertIsNotNone(rule, "rule-generated insight must name the InsightRule + version")
            self.assertIn("id", rule)
            self.assertIn("version", rule)


if __name__ == "__main__":
    unittest.main()
