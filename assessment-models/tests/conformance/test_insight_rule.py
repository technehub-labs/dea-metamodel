"""CR-AM-08 Phase 2 insight rule conformance tests.

Covers the Phase 2 contract (CR-AM-08 §12 Phase 2): the InsightRule
schema, the worked below-median rule, and rule-driven derivation of
AssessmentInsight documents over CR-AM-07 comparisons — including
reproducibility, evidence fidelity, and confidence enforcement.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, RefResolver

from runtime.comparison import MemberScore, compose_comparison
from runtime.insights import (
    CONDITION_METRICS,
    INSIGHT_TYPES,
    OPERATORS,
    SIGNIFICANCE_LEVELS,
    InsightRuleError,
    derive_insight,
    validate_rule,
)

REPO_ROOT = Path(__file__).resolve().parents[3]

RULE_SCHEMA_PATH = "assessment-models/schemas/insight-rule.schema.json"
INSIGHT_SCHEMA_PATH = "assessment-models/schemas/assessment-insight.schema.json"
RULE_EXAMPLE_PATH = "assessment-models/insights/rules/benchmark-below-median.yaml"
INSIGHT_EXAMPLE_PATH = (
    "assessment-models/insights/examples/"
    "telecom-sa-2026-automation-coverage-gap.yaml"
)
COHORT_PATH = (
    "assessment-models/benchmark/cohort-examples/"
    "telecom-service-assurance-2026.yaml"
)
INSIGHT_TYPES_PATH = "assessment-models/vocabulary/insight-types.yaml"
SIGNIFICANCE_PATH = "assessment-models/vocabulary/significance-levels.yaml"

FORBIDDEN_TERMS = [
    "project", "program", "initiative", "investment", "business_case",
    "roadmap", "recommendation", "transformation_action",
]
FROZEN_SURFACE_TERMS = ["eligibility_criteria", "benchmark-status"]


def _preserve_timestamp_strings(loader, node):
    return loader.construct_scalar(node)


yaml.SafeLoader.add_constructor("tag:yaml.org,2002:timestamp", _preserve_timestamp_strings)


def load_yaml(rel_path: str):
    return yaml.safe_load((REPO_ROOT / rel_path).read_text())


def load_json(rel_path: str):
    return json.loads((REPO_ROOT / rel_path).read_text())


def _validator(schema_path: str):
    schema = load_json(schema_path)
    common = load_json("assessment-models/schemas/common.schema.json")
    store = {
        "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
        "common.schema.json": common,
    }
    resolver = RefResolver(base_uri="", referrer=schema, store=store)
    return Draft202012Validator(schema, resolver=resolver)


def vocab_ids(rel_path: str) -> set:
    return {v["id"] for v in load_yaml(rel_path)["values"]}


def _comparison(member_scores, computed_at="2026-08-25T00:00:00Z"):
    """Compose a real comparison through the CR-AM-07 engine."""
    cohort_doc = load_yaml(COHORT_PATH)
    members = [MemberScore(m, s) for m, s in member_scores]
    return compose_comparison(
        cohort_doc,
        members,
        comparison_id="dea:comparison-insight-derivation-test",
        comparison_axis_measure={"id": "automation-coverage", "version": "1.0.0"},
        computed_at=computed_at,
    )


# Subject scores: org-low at 58 sits at the bottom of a six-member
# population (inclusive percentile 0.0) — below the rule's threshold 50.
MEMBERS = [
    ("dea:result-org-low", 58),
    ("dea:result-org-2", 70),
    ("dea:result-org-3", 72),
    ("dea:result-org-4", 75),
    ("dea:result-org-5", 80),
    ("dea:result-org-6", 85),
]


class InsightRuleSchemaTest(unittest.TestCase):
    """Rule schema integrity and worked-rule validation."""

    def test_rule_schema_parses_as_draft_2020_12(self):
        schema = load_json(RULE_SCHEMA_PATH)
        self.assertEqual(
            schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_worked_rule_validates_against_schema(self):
        doc = load_yaml(RULE_EXAMPLE_PATH)
        errors = list(_validator(RULE_SCHEMA_PATH).iter_errors(doc))
        self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors])

    def test_worked_rule_passes_runtime_validation(self):
        validate_rule(load_yaml(RULE_EXAMPLE_PATH))

    def test_rule_vocabulary_parity_three_way(self):
        """Schema enums ≡ vocabulary YAMLs ≡ runtime constants."""
        schema = load_json(RULE_SCHEMA_PATH)
        self.assertEqual(
            set(schema["properties"]["result"]["properties"]["insight_type"]["enum"]),
            vocab_ids(INSIGHT_TYPES_PATH))
        self.assertEqual(vocab_ids(INSIGHT_TYPES_PATH), set(INSIGHT_TYPES))
        self.assertEqual(
            set(schema["properties"]["result"]["properties"]["significance"]["enum"]),
            vocab_ids(SIGNIFICANCE_PATH))
        self.assertEqual(vocab_ids(SIGNIFICANCE_PATH), set(SIGNIFICANCE_LEVELS))

    def test_rule_condition_enums_match_runtime(self):
        schema = load_json(RULE_SCHEMA_PATH)
        cond = schema["properties"]["condition"]["properties"]
        self.assertEqual(set(cond["metric"]["enum"]), set(CONDITION_METRICS))
        self.assertEqual(set(cond["operator"]["enum"]), set(OPERATORS))

    def test_invalid_rule_is_refused_with_all_violations(self):
        bad = {
            "id": "dea:rule-bad",
            "condition": {"evidence": "vibes", "metric": "mood",
                          "operator": "~", "threshold": "high"},
            "result": {"insight_type": "ai-readiness-insight"},
            "confidence": {"level": "very-high"},
        }
        with self.assertRaises(InsightRuleError) as ctx:
            validate_rule(bad)
        message = str(ctx.exception)
        for fragment in ("version", "evidence", "metric", "operator",
                         "threshold", "insight_type", "significance",
                         "interpretation_template", "level"):
            self.assertIn(fragment, message)


def _derive(rule, comparison, member_id, **kwargs) -> dict:
    """Derive and narrow to dict — tests in this class expect a match."""
    insight = derive_insight(rule, comparison, member_id, **kwargs)
    assert insight is not None, f"expected rule match for {member_id}"
    return insight


class RuleDerivationTest(unittest.TestCase):
    """Rule-driven derivation over CR-AM-07 comparisons."""

    def setUp(self):
        self.rule = load_yaml(RULE_EXAMPLE_PATH)
        self.comparison = _comparison(MEMBERS)

    def test_derivation_produces_schema_valid_insight(self):
        insight = _derive(
            self.rule, self.comparison, "dea:result-org-low",
            generated_at="2026-08-25T00:00:00Z")
        errors = list(_validator(INSIGHT_SCHEMA_PATH).iter_errors(insight))
        self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors])

    def test_no_match_produces_no_insight(self):
        insight = derive_insight(self.rule, self.comparison, "dea:result-org-6")
        self.assertIsNone(insight, "no fabrication of negative statements")

    def test_derivation_is_reproducible(self):
        a = _derive(self.rule, self.comparison, "dea:result-org-low",
                    generated_at="2026-08-25T00:00:00Z")
        b = _derive(self.rule, self.comparison, "dea:result-org-low",
                    generated_at="2026-08-25T00:00:00Z")
        self.assertEqual(a, b, "same evidence + same rule version → same insight")

    def test_evidence_fidelity(self):
        """The derived insight cites exactly the comparison it derives from."""
        insight = _derive(self.rule, self.comparison, "dea:result-org-low",
                          generated_at="2026-08-25T00:00:00Z")
        cited = insight["evidence"]["benchmark_comparisons"]
        self.assertEqual([{"id": self.comparison["id"],
                           "version": self.comparison["version"]}], cited)
        self.assertEqual(cited, insight["lineage"]["sources"]["benchmark_comparisons"])

    def test_lineage_carries_rule_identity(self):
        insight = _derive(self.rule, self.comparison, "dea:result-org-low",
                          generated_at="2026-08-25T00:00:00Z")
        self.assertEqual({"id": "dea:rule-benchmark-below-median", "version": "1.0.0"},
                         insight["lineage"]["insight_rule"])
        self.assertEqual("rule", insight["generation"]["method"])

    def test_interpretation_template_is_substituted(self):
        insight = _derive(self.rule, self.comparison, "dea:result-org-low",
                          generated_at="2026-08-25T00:00:00Z")
        statement = insight["interpretation"]["statement"]
        self.assertNotIn("{", statement)
        self.assertIn("percentile 0", statement)
        self.assertIn("6", statement)

    def test_confidence_downgrade_below_minimum_population(self):
        """Rule declares minimum_population 10; population is 6 → low +
        small-cohort-size (confidence never exceeds the evidence)."""
        rule = dict(self.rule)
        rule["confidence"] = {"level": "high", "minimum_population": 10,
                              "limitations": []}
        insight = _derive(rule, self.comparison, "dea:result-org-low",
                          generated_at="2026-08-25T00:00:00Z")
        self.assertEqual("low", insight["confidence"]["level"])
        self.assertIn("small-cohort-size", insight["confidence"]["limitations"])

    def test_confidence_holds_when_population_satisfies_minimum(self):
        insight = _derive(self.rule, self.comparison, "dea:result-org-low",
                          generated_at="2026-08-25T00:00:00Z")
        self.assertEqual("high", insight["confidence"]["level"])

    def test_subject_without_standing_is_refused(self):
        with self.assertRaises(InsightRuleError):
            derive_insight(self.rule, self.comparison, "dea:result-org-ghost")

    def test_subject_measure_comes_from_comparison_axis(self):
        insight = _derive(self.rule, self.comparison, "dea:result-org-low",
                          generated_at="2026-08-25T00:00:00Z")
        self.assertEqual({"id": "automation-coverage", "version": "1.0.0"},
                         insight["subject"]["measure"])


class PhaseOneReferenceClosureTest(unittest.TestCase):
    """The Phase 1 worked insight references dea:rule-benchmark-below-median
    v1.0.0 — Phase 2 lands that rule; the reference must resolve."""

    def test_phase1_example_rule_reference_resolves(self):
        insight = load_yaml(INSIGHT_EXAMPLE_PATH)
        rule = load_yaml(RULE_EXAMPLE_PATH)
        ref = insight["lineage"]["insight_rule"]
        self.assertEqual(rule["id"], ref["id"])
        self.assertEqual(rule["version"], ref["version"])

    def test_phase1_example_type_matches_rule_result(self):
        insight = load_yaml(INSIGHT_EXAMPLE_PATH)
        rule = load_yaml(RULE_EXAMPLE_PATH)
        self.assertEqual(rule["result"]["insight_type"], insight["type"])


class RuleBoundaryGuardTest(unittest.TestCase):
    """CR-AM-08 §9/§10 boundaries for the rule schema."""

    def test_rule_schema_carries_no_action_vocabulary(self):
        text = (REPO_ROOT / RULE_SCHEMA_PATH).read_text().lower()
        for term in FORBIDDEN_TERMS:
            self.assertNotIn(term, text,
                             f"rule schema must not contain '{term}' (CR-AM-08 §9)")

    def test_rule_schema_does_not_redefine_frozen_surfaces(self):
        text = (REPO_ROOT / RULE_SCHEMA_PATH).read_text()
        for term in FROZEN_SURFACE_TERMS:
            self.assertNotIn(term, text,
                             f"rule schema must not touch frozen surface '{term}'")


if __name__ == "__main__":
    unittest.main()
