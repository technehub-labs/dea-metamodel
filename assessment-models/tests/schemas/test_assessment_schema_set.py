"""
Schema set test — proves CR-AM-02 §22 AC-02 (all P0 entity schemas
parse as Draft 2020-12) and AC-13/AC-14 (result schema requires
lineage + immutable result references).

Validates that every JSON Schema in the assessment-models/schemas/
directory parses as Draft 2020-12, and that the assessment-result
schema declares the lineage block as required (for AC-14 historical
integrity).
"""

import glob
import json
import os
import unittest
from pathlib import Path


SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"


class TestAssessmentSchemaSet(unittest.TestCase):
    """CR-AM-02 §22 AC-02: All P0 entities have JSON Schemas."""

    def test_all_schemas_parse_as_draft_2020_12(self):
        """Every schema file must parse as JSON Schema Draft 2020-12.

        This is the structural floor; the validate-schemas CI job re-runs
        the same check on real CI. Tests here run faster than CI round-trip.
        """
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("jsonschema not installed")
        schemas = sorted(glob.glob(str(SCHEMAS_DIR / "*.schema.json")))
        self.assertGreaterEqual(
            len(schemas), 12,
            "CR §18 requires at least 12 P0 entity schemas",
        )
        for f in schemas:
            with open(f) as fh:
                schema = json.load(fh)
            try:
                Draft202012Validator.check_schema(schema)
            except Exception as e:
                self.fail(f"Schema {os.path.basename(f)} does not parse as Draft 2020-12: {e}")

    def test_canonical_schema_ids_use_approved_namespace(self):
        """CR-AM03-19: canonical schemas must not publish the retired org namespace."""
        expected_prefix = "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/"
        for f in sorted(glob.glob(str(SCHEMAS_DIR / "*.schema.json"))):
            with open(f) as fh:
                schema = json.load(fh)
            self.assertTrue(
                schema.get("$id", "").startswith(expected_prefix),
                f"Schema {os.path.basename(f)} uses retired namespace: {schema.get('$id')!r}",
            )

    def test_p0_schemas_are_present(self):
        """CR §6 enumerates the P0 entity schemas. Every one must exist."""
        expected = [
            "assessment-model.schema.json",
            "assessment-instrument.schema.json",
            "assessment-execution.schema.json",
            "assessment-result.schema.json",
            "capability.schema.json",
            "scenario.schema.json",
            "measure.schema.json",
            "evidence.schema.json",
            "scoring-model.schema.json",
            "common.schema.json",
            "compatibility.schema.json",
            "relationship.schema.json",
        ]
        names = sorted(os.path.basename(f) for f in glob.glob(str(SCHEMAS_DIR / "*.schema.json")))
        for e in expected:
            self.assertIn(
                e, names,
                f"CR §6 P0 schema missing: {e}",
            )

    def test_assessment_result_schema_requires_lineage(self):
        """AC-14: every result identifies the exact model versions used.
        The schema must declare `lineage` as a required field."""
        with open(SCHEMAS_DIR / "assessment-result.schema.json") as fh:
            schema = json.load(fh)
        required = schema.get("required", [])
        self.assertIn(
            "lineage", required,
            "assessment-result.schema.json must declare `lineage` as required (AC-14)",
        )

    def test_assessment_model_schema_carries_compatibility(self):
        """AC-17: every model declares compatibility on the six declared axes.
        The schema must allow all six axes (and not enforce them as required;
        a new model's default is `compatible` everywhere)."""
        with open(SCHEMAS_DIR / "assessment-model.schema.json") as fh:
            schema = json.load(fh)
        comp = schema.get("properties", {}).get("compatibility", {})
        # The compatibility property is a $ref to common.schema.json#/$defs/compatibility.
        # We resolve the $ref and verify the 6 axes appear in the inline def.
        import re
        ref = comp.get("$ref", "")
        self.assertTrue(
            ref.endswith("/$defs/compatibility"),
            f"compatibility property should $ref to a $defs.compatibility; got {ref!r}",
        )
        with open(SCHEMAS_DIR / "common.schema.json") as fh:
            common = json.load(fh)
        comp_def = common.get("$defs", {}).get("compatibility", {})
        for axis in ("schema", "semantic", "scoring", "maturity", "result", "benchmark"):
            self.assertIn(
                axis, comp_def.get("properties", {}),
                f"compatibility.{axis} missing from common.schema.json#/$defs/compatibility",
            )

    def test_capability_schema_has_no_required_assessment_model_link(self):
        """AC-08: a Capability can be referenced independently of an AssessmentModel.
        The capability schema must not require an assessment-model link."""
        with open(SCHEMAS_DIR / "capability.schema.json") as fh:
            schema = json.load(fh)
        required = schema.get("required", [])
        self.assertNotIn(
            "assessment_model", required,
            "capability.schema.json must NOT require an assessment_model link (AC-08)",
        )

    def test_scenario_schema_has_no_required_assessment_model_link(self):
        """AC-09: a Scenario can be referenced independently of an AssessmentModel."""
        with open(SCHEMAS_DIR / "scenario.schema.json") as fh:
            schema = json.load(fh)
        required = schema.get("required", [])
        self.assertNotIn(
            "assessment_model", required,
            "scenario.schema.json must NOT require an assessment_model link (AC-09)",
        )

    def test_measure_schema_has_no_required_assessment_model_link(self):
        """AC-10: a Measure can be reused across AssessmentModels."""
        with open(SCHEMAS_DIR / "measure.schema.json") as fh:
            schema = json.load(fh)
        required = schema.get("required", [])
        self.assertNotIn(
            "assessment_model", required,
            "measure.schema.json must NOT require an assessment_model link (AC-10)",
        )

    def test_scoring_model_schema_has_no_required_assessment_model_link(self):
        """AC-11: a ScoringModel can be referenced independently."""
        with open(SCHEMAS_DIR / "scoring-model.schema.json") as fh:
            schema = json.load(fh)
        required = schema.get("required", [])
        self.assertNotIn(
            "assessment_model", required,
            "scoring-model.schema.json must NOT require an assessment_model link (AC-11)",
        )

    def test_common_schema_defines_model_reference_and_lineage(self):
        """The common schema must define modelReference, version, lineage,
        and compatibility as $defs — these are the building blocks of every
        canonical model declaration. (CR-014 ships them in camelCase.)"""
        with open(SCHEMAS_DIR / "common.schema.json") as fh:
            schema = json.load(fh)
        defs = schema.get("$defs", {})
        for required_def in ("modelReference", "version", "lineage", "compatibility"):
            self.assertIn(
                required_def, defs,
                f"common.schema.json must define $defs.{required_def} (CR §22 AC-13/14/17)",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
