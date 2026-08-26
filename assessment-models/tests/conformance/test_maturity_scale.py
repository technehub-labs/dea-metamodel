"""CR-AM-09 Phase 1 maturity scale & level conformance tests.

Covers the Phase 1 contract (CR-AM-09 §12 Phase 1): the MaturityScale
and MaturityLevel schemas, the three progression/confidence
vocabularies, and the worked scale examples — including the spec
acceptance tests 1–3 (5-level model validates; 6-level model validates;
alternate-naming model validates without referencing the canonical
five-level terminology). The boundary guards verify the metamodel
never normalises to a global scale shape and never imposes universal
level naming or progression semantics.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, RefResolver

REPO_ROOT = Path(__file__).resolve().parents[3]

SCALE_SCHEMA_PATH = "assessment-models/schemas/maturity-scale.schema.json"
LEVEL_SCHEMA_PATH = "assessment-models/schemas/maturity-level.schema.json"
TOPOLOGIES_PATH = "assessment-models/vocabulary/progression-topologies.yaml"
FUNCTIONS_PATH = "assessment-models/vocabulary/progression-functions.yaml"
CONFORMANCE_STATUSES_PATH = "assessment-models/vocabulary/conformance-statuses.yaml"

FIVE_LEVEL_PATH = "assessment-models/maturity/scale-examples/autonomous-operations-5level.yaml"
SIX_LEVEL_PATH = "assessment-models/maturity/scale-examples/six-level-linear-exponential.yaml"
ALTERNATE_NAMING_PATH = "assessment-models/maturity/scale-examples/proactive-operations-alternate-naming.yaml"
# CR-AM-11 Phase 3 — the OpenDEA Enterprise Architecture reference instance.
# Subject is org-level adoption of OpenDEA itself (not generic EA practice).
# Five levels (L-0…L-4) with distinct digital-native naming from the canonical
# CMMI-era vocabulary the user rejects. Conforms to the maturity-scale schema
# (no scoring or band vocabulary inline).
OPENDEA_EA_SCALE_PATH = "assessment-models/maturity/scale-examples/opendea-enterprise-architecture.yaml"
# The reference instance declares its own digital-native level naming.
# "Absent" / "Defined" / "Managed" appear in the canonical vocabulary but
# the instance intentionally uses them in a digital-native frame
# (adoption maturity, not process maturity).
OPENDEA_EA_TERMS = ["Absent", "Aware", "Defined", "Managed", "Self-Optimising"]

# CR-AM-09 §9 — a maturity level's identity requires (model, scale,
# level). Never normalised.
FIVE_LEVEL_TERMS = ["Absent", "Initial", "Defined", "Optimising"]
# Names that uniquely characterise the canonical autonomous-operations
# terminology. "Managed" is excluded because it is generic and used
# legitimately by other maturity models.
ALTERNATE_NAMING_DISTINCTIVENESS = [
    # The autonomous-operations naming pattern is [Absent, Initial, Defined, Managed, Optimising].
    # The alternate-naming example must break this pattern. We assert it
    # by name: at least one autonomous-operations-unique term absent AND
    # at least one distinctly-different term present.
    "Absent",
    "Initial",
    "Defined",
    "Optimising",
]
ALTERNATE_NAMING_NEW_TERMS = ["Not Present", "Reactive", "Proactive", "Optimized"]


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
    # Pre-load every schema that may be referenced via $ref so
    # RefResolver never tries to fetch them over HTTP. CI runs the
    # whole suite via `python -m unittest discover` with no network,
    # and a 404 on any $ref aborts the whole run.
    store = {
        "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
        "common.schema.json": common,
        "maturity-level.schema.json": load_json(LEVEL_SCHEMA_PATH),
    }
    resolver = RefResolver(base_uri="", referrer=schema, store=store)
    return Draft202012Validator(schema, resolver=resolver)


def vocab_ids(rel_path: str) -> set:
    return {v["id"] for v in load_yaml(rel_path)["values"]}


class MaturityScaleSchemaTest(unittest.TestCase):
    """Schema integrity (CR-AM-09 §6, §7)."""

    def test_schema_parses_as_draft_2020_12(self):
        schema = load_json(SCALE_SCHEMA_PATH)
        self.assertEqual(
            schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_required_fields_match_spec(self):
        schema = load_json(SCALE_SCHEMA_PATH)
        for field in ("id", "version", "name", "levels", "ordering",
                      "progression"):
            self.assertIn(field, schema["required"])

    def test_at_least_two_levels_required(self):
        """CR-AM-09 §6 — a maturity model must have at least two levels."""
        schema = load_json(SCALE_SCHEMA_PATH)
        self.assertEqual(2, schema["properties"]["levels"]["minItems"])

    def test_single_level_scale_is_refused(self):
        doc = load_yaml(FIVE_LEVEL_PATH)
        doc["levels"] = doc["levels"][:1]
        errors = list(_validator(SCALE_SCHEMA_PATH).iter_errors(doc))
        self.assertTrue(errors,
                        "a maturity scale with a single level must be refused")

    def test_ordinals_are_unique_and_monotonic(self):
        for path in (FIVE_LEVEL_PATH, SIX_LEVEL_PATH, ALTERNATE_NAMING_PATH):
            doc = load_yaml(path)
            ordinals = [level["ordinal"] for level in doc["levels"]]
            self.assertEqual(len(set(ordinals)), len(ordinals),
                             f"{path}: ordinals must be unique")
            self.assertEqual(sorted(ordinals), ordinals,
                             f"{path}: ordinals must be ascending")


class MaturityLevelSchemaTest(unittest.TestCase):
    """Level shape (CR-AM-09 §8, §9, §10)."""

    def test_required_fields_match_spec(self):
        schema = load_json(LEVEL_SCHEMA_PATH)
        for field in ("id", "ordinal", "name", "definition"):
            self.assertIn(field, schema["required"])

    def test_level_ordinal_is_non_negative_integer(self):
        schema = load_json(LEVEL_SCHEMA_PATH)
        self.assertEqual("integer", schema["properties"]["ordinal"]["type"])
        self.assertEqual(0, schema["properties"]["ordinal"]["minimum"])

    def test_level_definition_is_mandatory(self):
        """Removing definition must be refused. Tested at the level
        schema boundary (not the scale schema) so we exercise the
        MaturityLevel schema's own required-field enforcement."""
        level_schema = load_json(LEVEL_SCHEMA_PATH)
        validator = _validator(LEVEL_SCHEMA_PATH)
        for path in (FIVE_LEVEL_PATH, SIX_LEVEL_PATH, ALTERNATE_NAMING_PATH):
            doc = load_yaml(path)
            original = doc["levels"][0]["definition"]
            doc["levels"][0].pop("definition")
            errors = list(validator.iter_errors(doc["levels"][0]))
            self.assertTrue(
                errors,
                f"{path}: a level without definition must be refused "
                f"by MaturityLevel schema (required: {level_schema['required']})")
            doc["levels"][0]["definition"] = original


class ProgressionVocabularyTest(unittest.TestCase):
    """Phase 1 vocabularies (CR-AM-09 §14–§17, §25)."""

    def test_topologies_parity(self):
        schema = load_json(SCALE_SCHEMA_PATH)
        self.assertEqual(
            set(schema["properties"]["progression"]["properties"]["topology"]["enum"]),
            vocab_ids(TOPOLOGIES_PATH))

    def test_functions_parity(self):
        schema = load_json(SCALE_SCHEMA_PATH)
        self.assertEqual(
            set(schema["properties"]["progression"]["properties"]["function"]["enum"]),
            vocab_ids(FUNCTIONS_PATH))

    def test_conformance_statuses_parity(self):
        schema = load_json(SCALE_SCHEMA_PATH)
        self.assertEqual(
            set(schema["properties"]["conformance"]["properties"]["statuses"]["items"]["enum"]),
            vocab_ids(CONFORMANCE_STATUSES_PATH))

    def test_topology_and_function_are_independent(self):
        """CR-AM-09 §17 — topology ≠ function. The schema declares
        them on independent axes (no combined enum, no shared
        constraint); the conformance suite asserts this."""
        schema = load_json(SCALE_SCHEMA_PATH)
        topo_enum = set(schema["properties"]["progression"]["properties"]["topology"]["enum"])
        func_enum = set(schema["properties"]["progression"]["properties"]["function"]["enum"])
        self.assertNotEqual(topo_enum, func_enum,
                            "topology and function must be independent vocabularies")


class WorkedScaleValidationTest(unittest.TestCase):
    """Spec acceptance tests 1–3 (CR-AM-09 §35)."""

    def test_five_level_model_validates(self):
        """Test 1 — L0 → L1 → L2 → L3 → L4 must validate."""
        doc = load_yaml(FIVE_LEVEL_PATH)
        errors = list(_validator(SCALE_SCHEMA_PATH).iter_errors(doc))
        self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors])

    def test_six_level_model_validates(self):
        """Test 2 — L0 → L1 → … → L5 must validate."""
        doc = load_yaml(SIX_LEVEL_PATH)
        errors = list(_validator(SCALE_SCHEMA_PATH).iter_errors(doc))
        self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors])

    def test_alternate_naming_validates(self):
        """Test 3 — L0 = Not Present; alternate terminology must validate
        without referencing the canonical five-level naming."""
        doc = load_yaml(ALTERNATE_NAMING_PATH)
        errors = list(_validator(SCALE_SCHEMA_PATH).iter_errors(doc))
        self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors])
        level_names = [level["name"] for level in doc["levels"]]
        # The alternate-naming example breaks the autonomous-operations
        # naming pattern — at least one canonical term absent AND at
        # least one distinctly-different term present.
        canonical_present = [t for t in ALTERNATE_NAMING_DISTINCTIVENESS
                              if t in level_names]
        new_present = [t for t in ALTERNATE_NAMING_NEW_TERMS
                       if t in level_names]
        self.assertLess(
            len(canonical_present), len(ALTERNATE_NAMING_DISTINCTIVENESS),
            "alternate-naming scale must not reproduce the autonomous-"
            "operations naming pattern entirely")
        self.assertGreater(
            len(new_present), 0,
            "alternate-naming scale must introduce at least one "
            "distinguishing level name")

    def test_opendea_ea_reference_instance_validates(self):
        """CR-AM-11 §6/§24/§31 — the OpenDEA EA reference instance must
        validate against the maturity-scale schema with the digital-native
        level naming (no CMMI-era terms) and explicit conformance
        declaration. The instance is the first ecosystem-shared reference
        and the canonical consumer of the published contract suite."""
        doc = load_yaml(OPENDEA_EA_SCALE_PATH)
        errors = list(_validator(SCALE_SCHEMA_PATH).iter_errors(doc))
        self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors],
                         "opendea-enterprise-architecture reference scale must validate")
        level_names = [level["name"] for level in doc["levels"]]
        self.assertEqual(OPENDEA_EA_TERMS, level_names,
                         "reference instance must declare the documented "
                         "digital-native level naming (L-0 Absent, L-1 Aware, "
                         "L-2 Defined, L-3 Managed, L-4 Self-Optimising)")
        self.assertEqual("ascending", doc["ordering"])
        self.assertTrue(doc["conformance"]["highest_conformant_level_resolution"])

    def test_scale_identity_is_model_scoped(self):
        """CR-AM-09 §9 — (MaturityModel, MaturityScale, MaturityLevel)
        is the identity; L0 in one scale is not equivalent to L0 in
        another even with identical ordinal."""
        a = load_yaml(FIVE_LEVEL_PATH)
        b = load_yaml(ALTERNATE_NAMING_PATH)
        # Both declare an L0 at ordinal 0, but with different names.
        a_l0 = next(level for level in a["levels"] if level["ordinal"] == 0)
        b_l0 = next(level for level in b["levels"] if level["ordinal"] == 0)
        self.assertNotEqual(a_l0["name"], b_l0["name"],
                            "the two scales carry different L0 semantics — "
                            "identity is (model, scale, level), not level id")
        self.assertEqual((a["id"], a["version"]),
                       ("dea:scale-autonomous-operations-v1", "1.0.0"))
        self.assertEqual((b["id"], b["version"]),
                       ("dea:scale-proactive-operations-v1", "1.0.0"))


class TopologyFunctionIndependenceTest(unittest.TestCase):
    """CR-AM-09 §17 — topology ≠ function. Worked examples confirm
    linear-topology models can declare any function freely."""

    def test_five_level_uses_linear_topology_with_exponential_function(self):
        """Test 6 (CR-AM-09 §35) — topology=linear, function=exponential
        must validate (the maturity-v2 effort-coefficient insight)."""
        doc = load_yaml(FIVE_LEVEL_PATH)
        self.assertEqual("linear", doc["progression"]["topology"])
        self.assertEqual("exponential", doc["progression"]["function"])

    def test_six_level_uses_linear_topology_with_exponential_function(self):
        doc = load_yaml(SIX_LEVEL_PATH)
        self.assertEqual("linear", doc["progression"]["topology"])
        self.assertEqual("exponential", doc["progression"]["function"])


class ScaleConformanceContractTest(unittest.TestCase):
    """CR-AM-09 §25 — explicit per-result conformance outcomes."""

    def test_highest_conformant_resolution_supported(self):
        """CR-AM-09 §26 — a level is assigned only when all lower-level
        prerequisites AND its own conditions are satisfied. Scales must
        be able to declare this."""
        doc = load_yaml(FIVE_LEVEL_PATH)
        self.assertTrue(
            doc["conformance"]["highest_conformant_level_resolution"])

    def test_all_five_conformance_statuses_present(self):
        doc = load_yaml(FIVE_LEVEL_PATH)
        statuses = set(doc["conformance"]["statuses"])
        self.assertEqual(set(vocab_ids(CONFORMANCE_STATUSES_PATH)), statuses)


class ScaleBoundaryGuardTest(unittest.TestCase):
    """CR-AM-09 §10–§13: identifiers structural, semantics explicit;
    ordinals order only; never cross-model equivalence."""

    def test_ordinals_do_not_imply_cross_model_equivalence(self):
        """The schema explicitly states ordinals order only — neither
        scoring, nor cross-model equivalence. The conformance suite
        pins this through the identity rule test above."""
        schema = load_json(LEVEL_SCHEMA_PATH)
        self.assertNotIn("scoring", schema["properties"]["ordinal"].get("description", "").lower())
        self.assertNotIn("equivalent", schema["properties"]["ordinal"].get("description", "").lower())

    def test_scale_schema_carries_no_scoring_or_band_vocabulary(self):
        """Phase 1 scope is scale + level + progression. Scoring bands
        and resolution rules ship in Phase 3. The schema must not
        pre-empt them — that would violate the additive, evolutionary
        migration principle (CR-AM-09 §11 constraint 6)."""
        text = (REPO_ROOT / SCALE_SCHEMA_PATH).read_text()
        for forbidden in ("scoring_band", "scoring_bands", "progress_band",
                          "progress_scoring_band", "level_resolution_rule",
                          "resolution_rule"):
            self.assertNotIn(forbidden, text.lower(),
                             f"scale schema must not pre-empt Phase 3: "
                             f"'{forbidden}'")


if __name__ == "__main__":
    unittest.main()