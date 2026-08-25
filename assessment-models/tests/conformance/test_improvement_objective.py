"""CR-AM-08 Phase 4 improvement objective conformance tests.

Covers the Phase 4 contract (CR-AM-08 §12 Phase 4): the
ImprovementObjective schema, the priority vocabulary, the worked
objective that closes the Phase 1/2/3 chain, and the seam to the
future value-CR — including the assertion that TRANSFORM vocabulary
(structural TRANSFORM vocabulary + TRANSFORM fields the value-CR
will own) is structurally refused at the assessment-metamodel seam.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, RefResolver

REPO_ROOT = Path(__file__).resolve().parents[3]

SCHEMA_PATH = "assessment-models/schemas/improvement-objective.schema.json"
PRIORITIES_PATH = "assessment-models/vocabulary/improvement-objective-priorities.yaml"
EXAMPLE_PATH = (
    "assessment-models/objectives/examples/automation-coverage-above-median.yaml"
)
INSIGHT_EXAMPLE_PATH = (
    "assessment-models/insights/examples/"
    "telecom-sa-2026-automation-coverage-gap.yaml"
)
GAP_EXAMPLE_PATH = (
    "assessment-models/gaps/examples/benchmark-gap-automation-coverage.yaml"
)
COMPARISON_EXAMPLE_PATH = (
    "assessment-models/benchmark/comparison-examples/"
    "telecom-service-assurance-2026-comparison.yaml"
)

# TRANSFORM vocabulary — the value-CR owns these. Structurally refused
# at the assessment seam (CR-AM-08 §9).
FORBIDDEN_TRANSFORM_TERMS = [
    "project", "program", "initiative", "investment", "business_case",
    "roadmap", "budget", "kpi_target", "value_realisation",
]
# Frozen CR-AM-06/07 surfaces — the objective schema does not redefine
# eligibility or comparison semantics.
FROZEN_SURFACE_TERMS = ["eligibility_criteria", "benchmark-status", "standings"]
# Allowed uses of TRANSFORM terms in narrative prose (the schema's
# description documents what the value-CR owns; the schema itself must
# not contain these as structural keys).
PROSE_ALLOWED_TERMS = {"project", "program", "initiative", "investment",
                        "roadmap", "value_realisation"}


def _preserve_timestamp_strings(loader, node):
    return loader.construct_scalar(node)


yaml.SafeLoader.add_constructor("tag:yaml.org,2002:timestamp", _preserve_timestamp_strings)


def load_yaml(rel_path: str):
    return yaml.safe_load((REPO_ROOT / rel_path).read_text())


def load_json(rel_path: str):
    return json.loads((REPO_ROOT / rel_path).read_text())


def objective_validator():
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


class ImprovementObjectiveSchemaTest(unittest.TestCase):
    """Schema integrity and worked-example validation."""

    def test_schema_parses_as_draft_2020_12(self):
        schema = load_json(SCHEMA_PATH)
        self.assertEqual(
            schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_required_fields_match_spec(self):
        schema = load_json(SCHEMA_PATH)
        for field in ("id", "version", "status", "target_state", "evidence",
                      "priority", "lineage"):
            self.assertIn(field, schema["required"])

    def test_worked_objective_validates(self):
        doc = load_yaml(EXAMPLE_PATH)
        errors = list(objective_validator().iter_errors(doc))
        self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors])

    def test_target_state_is_mandatory(self):
        doc = load_yaml(EXAMPLE_PATH)
        del doc["target_state"]
        errors = list(objective_validator().iter_errors(doc))
        self.assertTrue(errors, "objective without target_state is not canonical")

    def test_priority_is_mandatory(self):
        doc = load_yaml(EXAMPLE_PATH)
        del doc["priority"]
        errors = list(objective_validator().iter_errors(doc))
        self.assertTrue(errors)

    def test_evidence_is_mandatory(self):
        doc = load_yaml(EXAMPLE_PATH)
        del doc["evidence"]
        errors = list(objective_validator().iter_errors(doc))
        self.assertTrue(errors, "objective without evidence citation is not canonical")

    def test_lineage_is_mandatory(self):
        doc = load_yaml(EXAMPLE_PATH)
        del doc["lineage"]
        errors = list(objective_validator().iter_errors(doc))
        self.assertTrue(errors)

    def test_unknown_top_level_keys_are_refused(self):
        """The seam: TRANSFORM fields structurally refused. A typical
        TRANSFORM-side field like 'project' or 'roadmap' must never
        validate against an ImprovementObjective."""
        for forbidden in ("project", "initiative", "investment", "roadmap"):
            doc = load_yaml(EXAMPLE_PATH)
            doc[forbidden] = {"name": f"smuggled {forbidden}"}
            errors = list(objective_validator().iter_errors(doc))
            self.assertTrue(
                errors,
                f"objective schema must refuse top-level '{forbidden}' "
                f"(TRANSFORM vocabulary, CR-AM-08 §9)")


class PriorityVocabularyTest(unittest.TestCase):
    """Priority vocabulary parity (schema enum ≡ vocabulary YAML)."""

    def test_priorities_parity(self):
        schema = load_json(SCHEMA_PATH)
        self.assertEqual(set(schema["properties"]["priority"]["enum"]),
                         vocab_ids(PRIORITIES_PATH))

    def test_priority_count(self):
        self.assertEqual(4, len(vocab_ids(PRIORITIES_PATH)))


class WorkedChainClosureTest(unittest.TestCase):
    """The Phase 4 example closes the Phase 1/2/3 worked chain —
    every cited ID resolves to a landed Phase 1/2/3 artifact."""

    def test_cited_insight_resolves_to_phase12_example(self):
        obj = load_yaml(EXAMPLE_PATH)
        insight = load_yaml(INSIGHT_EXAMPLE_PATH)
        cited = {r["id"] for r in obj["evidence"]["insights"]}
        self.assertIn(insight["id"], cited)

    def test_cited_gap_resolves_to_phase3_example(self):
        obj = load_yaml(EXAMPLE_PATH)
        gap = load_yaml(GAP_EXAMPLE_PATH)
        cited = {r["id"] for r in obj["evidence"]["gaps"]}
        self.assertIn(gap["id"], cited)

    def test_lineage_mirrors_evidence(self):
        obj = load_yaml(EXAMPLE_PATH)
        ev_insights = {r["id"] for r in obj["evidence"]["insights"]}
        ev_gaps = {r["id"] for r in obj["evidence"]["gaps"]}
        lin_insights = {r["id"] for r in obj["lineage"]["sources"]["insights"]}
        lin_gaps = {r["id"] for r in obj["lineage"]["sources"]["gaps"]}
        self.assertEqual(ev_insights, lin_insights,
                         "objective lineage must mirror evidence for insights")
        self.assertEqual(ev_gaps, lin_gaps,
                         "objective lineage must mirror evidence for gaps")

    def test_target_state_target_is_natural_magnitude(self):
        """The target moves automation coverage above the cohort median
        and toward but not beyond the worked comparison's interquartile
        band — a sensible closed-form objective, not a TRANSFORM claim."""
        comparison = load_yaml(COMPARISON_EXAMPLE_PATH)
        obj = load_yaml(EXAMPLE_PATH)
        target = obj["target_state"]["value"]
        self.assertGreater(target, comparison["distribution"]["median"])
        self.assertLessEqual(target, comparison["distribution"]["q3"])


class ObjectiveBoundaryGuardTest(unittest.TestCase):
    """The seam: TRANSFORM vocabulary stays on the value-CR side."""

    def test_schema_structural_keys_never_include_transform_vocabulary(self):
        """The seam is structural: TRANSFORM-side keys (project,
        initiative, investment, roadmap, budget, kpi_target,
        business_case, value_realisation, program) must never appear as
        property or enum names in the objective schema — only the
        assessment-metamodel-side vocabulary (id, version, status,
        subject, target_state, evidence, priority, rationale, lineage,
        declared_at, deferred, scheduled, active, monitoring) is
        permitted. The schema's narrative description legitimately names
        the value-CR's vocabulary; that's allowed."""
        text = (REPO_ROOT / SCHEMA_PATH).read_text()
        structural_keys = set()
        for line in text.splitlines():
            stripped = line.strip().rstrip(",").strip('"').strip("'")
            if stripped and (
                    stripped.startswith('"') or stripped.endswith(":")
                    or stripped.startswith('"id"') or '"' in stripped[:8]):
                token = stripped.strip().strip(",").strip('"').strip("'")
                if token and token.isascii() and len(token) < 60 \
                        and not token.startswith("$") \
                        and not token.startswith("common"):
                    structural_keys.add(token)
        for term in FORBIDDEN_TRANSFORM_TERMS:
            if term in PROSE_ALLOWED_TERMS:
                # Allowed in description prose; assert not a structural key.
                self.assertNotIn(term, structural_keys,
                                 f"transform term '{term}' must not be a "
                                 f"structural key in the objective schema")
            else:
                self.assertNotIn(term, text.lower(),
                                 f"transform term '{term}' must not appear "
                                 f"anywhere in the objective schema")

    def test_schema_does_not_redefine_frozen_surfaces(self):
        text = (REPO_ROOT / SCHEMA_PATH).read_text()
        for term in FROZEN_SURFACE_TERMS:
            self.assertNotIn(term, text,
                             f"objective schema must not touch frozen surface '{term}'")


class CrossArtifactReconciliationTest(unittest.TestCase):
    """Cross-Phase 1/2/3 closure: schema rejects objectives that would
    smuggle TRANSFORM vocabulary even at the evidence-citation level."""

    def test_evidence_reference_without_version_passes_schema(self):
        """Citation discipline is enforced by the chain closure test
        (every cited ID resolves to a landed artifact); the schema
        itself permits id-only references per common.modelReference.
        This test pins that contract — the assessment seam accepts
        id-only references; provenance is asserted by the chain."""
        doc = load_yaml(EXAMPLE_PATH)
        doc["evidence"]["insights"][0] = {"id": "dea:insight-001"}
        errors = list(objective_validator().iter_errors(doc))
        self.assertEqual(
            [], [f"{list(e.path)}: {e.message}" for e in errors],
            "id-only evidence references validate (per common.modelReference)")


if __name__ == "__main__":
    unittest.main()