"""CR-AM-09 Phase 2 progression & native evaluation conformance tests.

Covers the Phase 2 contract (CR-AM-09 §12 Phase 2): the
MaturityEvaluationModel schema (native scoring domains incl. 0–10,
never normalized), the scoring mechanism/domain vocabularies,
CriterionLevelExpectation, and the worked non-linear example — including
spec tests 4 (native 0–10 validates without normalization) and 6
(topology ≠ function deepened at the evaluation level).
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, RefResolver

REPO_ROOT = Path(__file__).resolve().parents[3]

EVAL_SCHEMA_PATH = "assessment-models/schemas/maturity-evaluation-model.schema.json"
SCALE_SCHEMA_PATH = "assessment-models/schemas/maturity-scale.schema.json"
LEVEL_SCHEMA_PATH = "assessment-models/schemas/maturity-level.schema.json"
MECHANISMS_PATH = "assessment-models/vocabulary/scoring-mechanisms.yaml"
DOMAINS_PATH = "assessment-models/vocabulary/scoring-domain-kinds.yaml"
EVAL_EXAMPLE_PATH = (
    "assessment-models/maturity/evaluation-examples/"
    "proactive-operations-evaluation.yaml"
)
SCALE_EXAMPLE_PATH = (
    "assessment-models/maturity/scale-examples/"
    "proactive-operations-alternate-naming.yaml"
)
FIVE_LEVEL_SCALE_PATH = (
    "assessment-models/maturity/scale-examples/"
    "autonomous-operations-5level.yaml"
)
# CR-AM-11 Phase 3 — the OpenDEA Enterprise Architecture reference instance.
OPENDEA_EA_EVAL_PATH = (
    "assessment-models/maturity/evaluation-examples/"
    "opendea-enterprise-architecture.yaml"
)
OPENDEA_EA_EVAL_SCALE_PATH = (
    "assessment-models/maturity/scale-examples/"
    "opendea-enterprise-architecture.yaml"
)
OPENDEA_EA_BASELINE_PATH = (
    "assessment-models/maturity/baseline-examples/"
    "opendea-enterprise-architecture.yaml"
)


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
    # Offline CI (unittest discover, no network): pre-load every schema
    # that may be referenced via $ref into the RefResolver store.
    store = {
        "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
        "common.schema.json": common,
        "maturity-level.schema.json": load_json(LEVEL_SCHEMA_PATH),
    }
    resolver = RefResolver(base_uri="", referrer=schema, store=store)
    return Draft202012Validator(schema, resolver=resolver)


def vocab_ids(rel_path: str) -> set:
    return {v["id"] for v in load_yaml(rel_path)["values"]}


class MaturityEvaluationSchemaTest(unittest.TestCase):
    """Schema integrity (CR-AM-09 §6)."""

    def test_schema_parses_as_draft_2020_12(self):
        schema = load_json(EVAL_SCHEMA_PATH)
        self.assertEqual(
            schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_required_fields_match_spec(self):
        schema = load_json(EVAL_SCHEMA_PATH)
        for field in ("id", "version", "name", "scale", "scoring", "criteria"):
            self.assertIn(field, schema["required"])

    def test_scoring_requires_mechanism_and_domain(self):
        doc = load_yaml(EVAL_EXAMPLE_PATH)
        del doc["scoring"]["mechanism"]
        errors = list(_validator(EVAL_SCHEMA_PATH).iter_errors(doc))
        self.assertTrue(errors)

    def test_scale_reference_is_mandatory(self):
        """The evaluation model must declare the scale it feeds."""
        doc = load_yaml(EVAL_EXAMPLE_PATH)
        del doc["scale"]
        errors = list(_validator(EVAL_SCHEMA_PATH).iter_errors(doc))
        self.assertTrue(errors)

    def test_criterion_without_level_expectations_is_refused(self):
        doc = load_yaml(EVAL_EXAMPLE_PATH)
        del doc["criteria"][0]["level_expectations"]
        errors = list(_validator(EVAL_SCHEMA_PATH).iter_errors(doc))
        self.assertTrue(errors,
                        "a criterion without level expectations is not canonical "
                        "(CR-AM-09 §4: maturity is behavior, not merely a score)")

    def test_unknown_top_level_keys_are_refused(self):
        doc = load_yaml(EVAL_EXAMPLE_PATH)
        doc["normalized_score"] = 58  # normalization vocabulary refused
        errors = list(_validator(EVAL_SCHEMA_PATH).iter_errors(doc))
        self.assertTrue(errors, "additionalProperties: false must refuse "
                                "normalization vocabulary")


class ScoringVocabularyTest(unittest.TestCase):
    """Mechanism + domain vocabulary parity."""

    def test_mechanisms_parity(self):
        schema = load_json(EVAL_SCHEMA_PATH)
        self.assertEqual(
            set(schema["properties"]["scoring"]["properties"]["mechanism"]["enum"]),
            vocab_ids(MECHANISMS_PATH))

    def test_domain_kinds_parity(self):
        schema = load_json(EVAL_SCHEMA_PATH)
        self.assertEqual(
            set(schema["properties"]["scoring"]["properties"]["domain"]
                ["properties"]["kind"]["enum"]),
            vocab_ids(DOMAINS_PATH))

    def test_all_native_domains_present(self):
        """CR-AM-09 §6 — the domain vocabulary covers every declared
        native scoring form incl. 0–10 and rubric."""
        expected = {"numeric-0-100", "numeric-0-5", "numeric-0-10",
                    "percentage", "weighted-index", "categorical",
                    "boolean-conformance", "multi-dimensional-vector",
                    "rubric", "custom"}
        self.assertEqual(expected, vocab_ids(DOMAINS_PATH))


class WorkedEvaluationValidationTest(unittest.TestCase):
    """Spec test 4 — native 0–10 scoring domain validates without
    normalization (CR-AM-09 §35 test 4)."""

    def test_native_0_to_10_model_validates(self):
        doc = load_yaml(EVAL_EXAMPLE_PATH)
        errors = list(_validator(EVAL_SCHEMA_PATH).iter_errors(doc))
        self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors])

    def test_native_domain_is_0_to_10_not_normalized(self):
        doc = load_yaml(EVAL_EXAMPLE_PATH)
        domain = doc["scoring"]["domain"]
        self.assertEqual("numeric-0-10", domain["kind"])
        self.assertEqual(0, domain["minimum"])
        self.assertEqual(10, domain["maximum"])

    def test_evaluation_references_the_phase1_scale(self):
        doc = load_yaml(EVAL_EXAMPLE_PATH)
        scale = load_yaml(SCALE_EXAMPLE_PATH)
        self.assertEqual(scale["id"], doc["scale"]["id"])
        self.assertEqual(scale["version"], doc["scale"]["version"])

    def test_opendea_ea_reference_evaluation_validates(self):
        """CR-AM-11 §6/§24 — the OpenDEA EA reference instance evaluation
        model must validate against maturity-evaluation-model schema and
        reference its own scale (id+version). Native 0-100 weighted-mean
        scoring with six criteria; per-level expectations cover L-0..L-4."""
        doc = load_yaml(OPENDEA_EA_EVAL_PATH)
        errors = list(_validator(EVAL_SCHEMA_PATH).iter_errors(doc))
        self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors],
                         "opendea-ea evaluation must validate")
        scale = load_yaml(OPENDEA_EA_EVAL_SCALE_PATH)
        self.assertEqual(scale["id"], doc["scale"]["id"])
        self.assertEqual(scale["version"], doc["scale"]["version"])
        # Weighted native 0-100 domain
        domain = doc["scoring"]["domain"]
        self.assertEqual("numeric-0-100", domain["kind"])
        self.assertEqual(0, domain["minimum"])
        self.assertEqual(100, domain["maximum"])
        # Six criteria each carrying per-level expectations for all five levels
        scale_level_ids = {l["id"] for l in scale["levels"]}
        self.assertGreaterEqual(len(doc["criteria"]), 6)
        for c in doc["criteria"]:
            level_ids = {e["level"] for e in c["level_expectations"]}
            self.assertEqual(scale_level_ids, level_ids,
                             f"criterion {c['id']} must cover every scale level")


class CriterionLevelExpectationTest(unittest.TestCase):
    """CriterionLevelExpectation (CR-AM-09 §4): expectations reference
    level ids that resolve within the declared scale."""

    def test_expectation_level_ids_resolve_within_scale(self):
        doc = load_yaml(EVAL_EXAMPLE_PATH)
        scale = load_yaml(SCALE_EXAMPLE_PATH)
        scale_level_ids = {level["id"] for level in scale["levels"]}
        for criterion in doc["criteria"]:
            for expectation in criterion["level_expectations"]:
                self.assertIn(expectation["level"], scale_level_ids,
                              f"criterion {criterion['id']}: level "
                              f"{expectation['level']} must exist in the "
                              f"referenced scale")

    def test_mandatory_criterion_declared(self):
        doc = load_yaml(EVAL_EXAMPLE_PATH)
        mandatory = [c for c in doc["criteria"] if c.get("mandatory")]
        self.assertTrue(mandatory, "the worked example declares a "
                                   "mandatory gate criterion")

    def test_expectations_demonstrate_progression(self):
        """Each criterion's expectations span multiple levels — maturity
        is progressive behavior change (CR-AM-09 §4)."""
        doc = load_yaml(EVAL_EXAMPLE_PATH)
        for criterion in doc["criteria"]:
            self.assertGreaterEqual(
                len(criterion["level_expectations"]), 3,
                f"criterion {criterion['id']} must carry expectations "
                "across at least three levels")

    def test_evidence_requirements_present(self):
        doc = load_yaml(EVAL_EXAMPLE_PATH)
        for criterion in doc["criteria"]:
            self.assertTrue(criterion.get("evidence_requirements"),
                            f"criterion {criterion['id']} must declare "
                            "evidence requirements")


class TopologyFunctionDeepenedTest(unittest.TestCase):
    """Spec test 6 deepened (CR-AM-09 §5/§35): topology ≠ function at
    the evaluation level — the evaluation model's scale carries linear
    topology with exponential function; the evaluation layer imposes
    no coupling."""

    def test_evaluation_scale_combines_linear_topology_with_exponential_function(self):
        scale = load_yaml(SCALE_EXAMPLE_PATH)
        self.assertEqual("linear", scale["progression"]["topology"])
        self.assertEqual("exponential", scale["progression"]["function"])

    def test_evaluation_schema_has_no_topology_or_function_fields(self):
        """Evaluation does not redefine progression — progression lives
        on the scale (Phase 1). The evaluation schema must not carry
        topology/function vocabulary."""
        text = (REPO_ROOT / EVAL_SCHEMA_PATH).read_text().lower()
        self.assertNotIn('"topology"', text)
        self.assertNotIn('"function"', text)

    def test_no_assumed_equal_unit_distance(self):
        """CR-AM-09 Phase 2 conformance: native scores never imply equal
        distance between levels. The evaluation schema declares no
        per-level point budget; criterion scores are model-native.
        Structural-key check (quoted): the word 'normalized' legitimately
        appears in descriptive prose; it must never be a schema key."""
        text = (REPO_ROOT / EVAL_SCHEMA_PATH).read_text().lower()
        for forbidden in ("points_per_level", "level_score", "normalized"):
            self.assertNotIn(f'"{forbidden}"', text,
                             f"'{forbidden}' must never be a structural key")


class EvaluationBoundaryGuardTest(unittest.TestCase):
    """Phase 2 boundaries: evaluation never implies level attribution
    (Phase 3 owns resolution); frozen surfaces untouched."""

    def test_schema_carries_no_resolution_vocabulary(self):
        text = (REPO_ROOT / EVAL_SCHEMA_PATH).read_text().lower()
        for forbidden in ("level_resolution_rule", "resolution_rule",
                          "scoring_band", "progress_scoring_band"):
            self.assertNotIn(forbidden, text,
                             f"evaluation schema must not pre-empt Phase 3: "
                             f"'{forbidden}'")

    def test_schema_carries_no_transform_vocabulary(self):
        text = (REPO_ROOT / EVAL_SCHEMA_PATH).read_text().lower()
        for term in ("project", "initiative", "investment", "roadmap"):
            self.assertNotIn(f'"{term}"', text,
                             f"evaluation schema must not contain '{term}' "
                             "(TRANSFORM vocabulary)")

    def test_frozen_surfaces_untouched(self):
        text = (REPO_ROOT / EVAL_SCHEMA_PATH).read_text()
        for term in ("eligibility_criteria", "benchmark-status", "standings"):
            self.assertNotIn(term, text)


if __name__ == "__main__":
    unittest.main()
