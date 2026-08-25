"""CR-AM-09 Phase 3 scoring bands & level resolution conformance tests.

Covers the Phase 3 contract (CR-AM-09 §12 Phase 3): the
progress-scoring-band and level-resolution-rule schemas, the three band
families (numeric / non-numeric / multi-dimensional), the resolution
strategy vocabulary, and the worked proactive-operations band set +
resolution rule — including spec test 5 (a raw score never
automatically represents accumulated maturity: bands gate on mandatory
criteria and evidence, resolution walks highest-conformant-level).
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, RefResolver

REPO_ROOT = Path(__file__).resolve().parents[3]

BAND_SCHEMA_PATH = "assessment-models/schemas/progress-scoring-band.schema.json"
RULE_SCHEMA_PATH = "assessment-models/schemas/level-resolution-rule.schema.json"
LEVEL_SCHEMA_PATH = "assessment-models/schemas/maturity-level.schema.json"
STRATEGIES_PATH = "assessment-models/vocabulary/level-resolution-strategies.yaml"

BANDS_EXAMPLE_PATH = (
    "assessment-models/maturity/resolution-examples/"
    "proactive-operations-bands.yaml"
)
RULE_EXAMPLE_PATH = (
    "assessment-models/maturity/resolution-examples/"
    "proactive-operations-resolution.yaml"
)
SCALE_EXAMPLE_PATH = (
    "assessment-models/maturity/scale-examples/"
    "proactive-operations-alternate-naming.yaml"
)
EVAL_EXAMPLE_PATH = (
    "assessment-models/maturity/evaluation-examples/"
    "proactive-operations-evaluation.yaml"
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


class BandSchemaTest(unittest.TestCase):
    """Band schema integrity + worked example (CR-AM-09 §7)."""

    def test_schema_parses_as_draft_2020_12(self):
        schema = load_json(BAND_SCHEMA_PATH)
        self.assertEqual(
            schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_three_families_supported(self):
        schema = load_json(BAND_SCHEMA_PATH)
        family_enum = schema["properties"]["bands"]["items"]["properties"]["family"]["enum"]
        self.assertEqual(["numeric", "non-numeric", "multi-dimensional"],
                         family_enum)

    def test_bands_example_validates(self):
        doc = load_yaml(BANDS_EXAMPLE_PATH)
        errors = list(_validator(BAND_SCHEMA_PATH).iter_errors(doc))
        self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors])

    def test_band_without_level_is_refused(self):
        doc = load_yaml(BANDS_EXAMPLE_PATH)
        del doc["bands"][0]["level"]
        errors = list(_validator(BAND_SCHEMA_PATH).iter_errors(doc))
        self.assertTrue(errors)

    def test_single_band_set_is_refused(self):
        """A band set must cover at least two levels."""
        doc = load_yaml(BANDS_EXAMPLE_PATH)
        doc["bands"] = doc["bands"][:1]
        errors = list(_validator(BAND_SCHEMA_PATH).iter_errors(doc))
        self.assertTrue(errors)


class RuleSchemaTest(unittest.TestCase):
    """Resolution rule schema integrity + worked example."""

    def test_schema_parses_as_draft_2020_12(self):
        schema = load_json(RULE_SCHEMA_PATH)
        self.assertEqual(
            schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_rule_example_validates(self):
        doc = load_yaml(RULE_EXAMPLE_PATH)
        errors = list(_validator(RULE_SCHEMA_PATH).iter_errors(doc))
        self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors])

    def test_strategy_vocabulary_parity(self):
        schema = load_json(RULE_SCHEMA_PATH)
        self.assertEqual(
            set(schema["properties"]["strategy"]["enum"]),
            vocab_ids(STRATEGIES_PATH))

    def test_highest_conformant_level_is_expressible(self):
        """CR-AM-09 §7: highest-conformant-level resolution must be
        expressible — and is the worked example's strategy."""
        self.assertIn("highest-conformant-level", vocab_ids(STRATEGIES_PATH))
        doc = load_yaml(RULE_EXAMPLE_PATH)
        self.assertEqual("highest-conformant-level", doc["strategy"])

    def test_rule_without_logic_is_refused(self):
        doc = load_yaml(RULE_EXAMPLE_PATH)
        del doc["logic"]
        errors = list(_validator(RULE_SCHEMA_PATH).iter_errors(doc))
        self.assertTrue(errors)


class SpecTestFiveTest(unittest.TestCase):
    """Spec test 5 (CR-AM-09 §35): a raw score never automatically
    represents accumulated maturity."""

    def test_high_bands_gate_on_mandatory_criteria(self):
        """The L3 and L4 bands carry mandatory_criteria — a score in
        range is necessary, never sufficient."""
        doc = load_yaml(BANDS_EXAMPLE_PATH)
        high = {b["level"]: b for b in doc["bands"]
                if b["level"] in ("L3", "L4")}
        self.assertEqual({"L3", "L4"}, set(high))
        for band in high.values():
            self.assertIn("mandatory_criteria", band,
                          f"{band['level']} band must gate on mandatory criteria")

    def test_l4_band_gates_on_evidence(self):
        doc = load_yaml(BANDS_EXAMPLE_PATH)
        l4 = next(b for b in doc["bands"] if b["level"] == "L4")
        self.assertIn("evidence_requirements", l4,
                      "the top band must gate on evidence requirements")

    def test_mandatory_criteria_resolve_in_evaluation_model(self):
        """Cross-artifact: the band's mandatory criterion ids exist in
        the Phase 2 evaluation model that feeds this scale."""
        bands = load_yaml(BANDS_EXAMPLE_PATH)
        evaluation = load_yaml(EVAL_EXAMPLE_PATH)
        criterion_ids = {c["id"] for c in evaluation["criteria"]}
        for band in bands["bands"]:
            for criterion in band.get("mandatory_criteria", []):
                self.assertIn(criterion, criterion_ids,
                              f"band {band['id']} cites unknown criterion "
                              f"{criterion}")

    def test_rule_consumes_exactly_the_declared_inputs(self):
        """The resolution rule's consumes == the evaluation model's
        level_resolution_inputs (canonical flow, CR-AM-09 §7)."""
        rule = load_yaml(RULE_EXAMPLE_PATH)
        evaluation = load_yaml(EVAL_EXAMPLE_PATH)
        self.assertEqual(set(evaluation["level_resolution_inputs"]),
                         set(rule["consumes"]))

    def test_rule_logic_states_the_walk(self):
        rule = load_yaml(RULE_EXAMPLE_PATH)
        logic = rule["logic"]
        for fragment in ("ascending", "mandatory_criteria",
                         "evidence_requirements", "highest"):
            self.assertIn(fragment, logic,
                          "highest-conformant-level walk must be stated")


class BandScaleConsistencyTest(unittest.TestCase):
    """Bands resolve to levels of the declared scale."""

    def test_band_levels_resolve_within_scale(self):
        bands = load_yaml(BANDS_EXAMPLE_PATH)
        scale = load_yaml(SCALE_EXAMPLE_PATH)
        self.assertEqual(scale["id"], bands["scale"]["id"])
        scale_level_ids = {level["id"] for level in scale["levels"]}
        for band in bands["bands"]:
            self.assertIn(band["level"], scale_level_ids,
                          f"band {band['id']} resolves to unknown level "
                          f"{band['level']}")

    def test_every_scale_level_has_a_band(self):
        bands = load_yaml(BANDS_EXAMPLE_PATH)
        scale = load_yaml(SCALE_EXAMPLE_PATH)
        banded = {b["level"] for b in bands["bands"]}
        scaled = {level["id"] for level in scale["levels"]}
        self.assertEqual(scaled, banded,
                         "the band set must cover every scale level")

    def test_numeric_bands_cover_the_native_domain(self):
        """Bands over the 0–10 native domain: contiguous, ordered,
        cover [0, 10] respecting inclusivity boundaries."""
        bands = load_yaml(BANDS_EXAMPLE_PATH)
        evaluation = load_yaml(EVAL_EXAMPLE_PATH)
        domain = evaluation["scoring"]["domain"]
        self.assertEqual("numeric-0-10", domain["kind"])
        numeric = [b for b in bands["bands"] if b["family"] == "numeric"]
        numeric.sort(key=lambda b: b["numeric"]["minimum"])
        self.assertEqual(domain["minimum"], numeric[0]["numeric"]["minimum"])
        self.assertEqual(domain["maximum"], numeric[-1]["numeric"]["maximum"])
        for prev, nxt in zip(numeric, numeric[1:]):
            self.assertEqual(prev["numeric"]["maximum"],
                             nxt["numeric"]["minimum"],
                             "bands must be contiguous over the domain")
            # Boundary ownership must be unambiguous.
            self.assertNotEqual(prev["numeric"]["max_inclusive"],
                                nxt["numeric"]["min_inclusive"],
                                "adjacent bands must not both include the boundary")


class ResolutionBoundaryGuardTest(unittest.TestCase):
    """Phase 3 boundaries: no Phase 4 baseline vocabulary; frozen
    surfaces untouched; TRANSFORM keys refused."""

    def test_schemas_carry_no_baseline_vocabulary(self):
        for schema_path in (BAND_SCHEMA_PATH, RULE_SCHEMA_PATH):
            text = (REPO_ROOT / schema_path).read_text().lower()
            for forbidden in ('"baseline"', '"maturity_scale_baseline"',
                              '"locked_at"', '"benchmark_lock"'):
                self.assertNotIn(forbidden, text,
                                 f"{schema_path} must not pre-empt Phase 4: "
                                 f"{forbidden}")

    def test_schemas_carry_no_transform_vocabulary(self):
        for schema_path in (BAND_SCHEMA_PATH, RULE_SCHEMA_PATH):
            text = (REPO_ROOT / schema_path).read_text().lower()
            for term in ('"project"', '"initiative"', '"investment"',
                         '"roadmap"'):
                self.assertNotIn(term, text)

    def test_frozen_surfaces_untouched(self):
        for schema_path in (BAND_SCHEMA_PATH, RULE_SCHEMA_PATH):
            text = (REPO_ROOT / schema_path).read_text()
            for term in ("eligibility_criteria", "benchmark-status",
                         "standings"):
                self.assertNotIn(term, text)


if __name__ == "__main__":
    unittest.main()
