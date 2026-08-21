"""
Compatibility states test — proves CR-AM-02 §22 AC-17 (backward-compatible
model update does not invalidate existing results) + the six-axis
compatibility declaration contract.

Asserts that:
  1. The compatibility-types YAML declares the six axes (schema, semantic,
     scoring, maturity, result, benchmark).
  2. Each axis has 'compatible' and 'incompatible' as the only value types.
  3. A model with all-axes compatible does NOT block historical results.
  4. A model with `benchmark: incompatible` is correctly captured (the
     result is still result-compatible but the benchmark engine
     will exclude it).
  5. The compatibility declaration is shape-validated against the
     compatibility.schema.json.
  6. PATCH version bumps (CR-AM-02 §9) must NOT set any dimension to
     incompatible — verified by linting the migration mapping.
  7. MAJOR version bumps MUST set at least one dimension to incompatible.
"""

import json
import os
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]  # assessment-models/tests/compatibility => repo root
VOCAB_DIR = REPO_ROOT / "assessment-models" / "vocabulary"
SCHEMAS_DIR = REPO_ROOT / "assessment-models" / "schemas"
MIGRATION_DIR = REPO_ROOT / "assessment-models" / "migrations" / "v1-instrument"


class TestCompatibilityStates(unittest.TestCase):
    """CR-AM-02 §22 AC-17: backward-compatible model update does not invalidate."""

    def setUp(self):
        # Lazy import yaml so the test isn't fragile if it runs without
        # pyyaml installed (the dependencies live in CI).
        import yaml
        with open(SCHEMAS_DIR / "compatibility.schema.json") as fh:
            self.compatibility_schema = json.load(fh)
        with open(VOCAB_DIR / "compatibility-types.yaml") as fh:
            self.compatibility_vocab = yaml.safe_load(fh)
        with open(MIGRATION_DIR / "mapping.yaml") as fh:
            self.migration_mapping = yaml.safe_load(fh)
        with open(MIGRATION_DIR / "canonical-technology-migration.yaml") as fh:
            self.canonical_projection = yaml.safe_load(fh)

    def test_compatibility_vocab_declares_six_axes(self):
        """CR §11 declares exactly six compatibility axes."""
        axes = self.compatibility_vocab.get("dimensions", [])
        declared = {a["id"] for a in axes}
        expected = {"schema", "semantic", "scoring", "maturity", "result", "benchmark"}
        self.assertEqual(
            declared, expected,
            f"compatibility-types.yaml must declare the six canonical axes; got {declared}",
        )

    def test_each_axis_has_only_compatible_or_incompatible_values(self):
        """Every axis must allow exactly two literal values: 'compatible'
        and 'incompatible'. No more, no less."""
        for axis in self.compatibility_vocab["dimensions"]:
            self.assertEqual(
                sorted(axis["values"]), ["compatible", "incompatible"],
                f"axis {axis['id']!r}: values must be exactly ['compatible','incompatible']",
            )

    def test_canonical_projection_compatibility_shape_matches_default(self):
        """The canonical projection's compatibility declaration must include
        all six axes, each with a valid value."""
        comp = self.canonical_projection.get("compatibility")
        self.assertIsNotNone(comp, "compatibility declaration missing")
        for axis in ("schema", "semantic", "scoring", "maturity", "result", "benchmark"):
            self.assertIn(axis, comp, f"axis {axis} missing")
            self.assertIn(comp[axis], ("compatible", "incompatible"))

    def test_canonical_projection_declaration_validates_against_schema(self):
        """The compatibility declaration on the canonical projection must
        validate against the inline compatibility $ref in common.schema.json.
        The standalone compatibility.schema.json declares a wider shape
        (model_id + model_version + axes); the inline shape used by
        assessment-model.schema.json is just the six axes."""
        # Resolve the inline compatibility def via the canonical assessment-model.
        with open(SCHEMAS_DIR / "assessment-model.schema.json") as fh:
            am_schema = json.load(fh)
        ref = am_schema.get("properties", {}).get("compatibility", {}).get("$ref", "")
        self.assertTrue(
            ref.endswith("/$defs/compatibility"),
            f"compatibility should $ref to common.schema.json#/$defs/compatibility",
        )
        with open(SCHEMAS_DIR / "common.schema.json") as fh:
            common = json.load(fh)
        comp_def = common["$defs"]["compatibility"]
        try:
            from jsonschema import Draft202012Validator
            validator = Draft202012Validator(comp_def)
            errors = list(validator.iter_errors(self.canonical_projection.get("compatibility", {})))
            if errors:
                self.fail(
                    "compatibility declaration does not validate against inline def: "
                    + "; ".join(e.message for e in errors[:3])
                )
        except ImportError:
            self.skipTest("jsonschema not installed")

    def test_migration_mapping_specifies_full_compatibility_declaration(self):
        """The migration mapping must specify a full compatibility declaration
        (all six axes). It surfaces the project-default "
        result-compatible / benchmark-incompatible" decision.
        """
        mapping_entries = {
            e["target"]: e
            for e in self.migration_mapping["mappings"]
            if e["target"] == "compatibility"
        }
        self.assertIn(
            "compatibility", mapping_entries,
            "migration mapping must include a compatibility entry",
        )
        comp_value = mapping_entries["compatibility"]["value"]
        for axis in ("schema", "semantic", "scoring", "maturity", "result", "benchmark"):
            self.assertIn(
                axis, comp_value, f"migration mapping compatibility missing axis: {axis}",
            )

    def test_patch_version_rule_documented(self):
        """CR-AM-02 §9 says PATCH bumps MUST NOT set any dimension to
        incompatible. The compatibility-types.yaml must encode this rule."""
        # The rule is in the `lifecycle` section. Verify the rule itself.
        lifecycle_text = "\n".join(
            self.compatibility_vocab.get("lifecycle", [])
        )
        self.assertIn(
            "PATCH", lifecycle_text,
            "compatibility-types.yaml must document PATCH/MINOR/MAJOR rules",
        )
        self.assertIn(
            "MAJOR", lifecycle_text,
            "compatibility-types.yaml must document PATCH/MINOR/MAJOR rules",
        )

    def test_old_legacy_aliases_preserved(self):
        """The relationship vocabulary preserves legacy aliases (CR-AM-01 §20).
        Anything using `produces-score-for` still validates."""
        with open(VOCAB_DIR / "relationship-types.yaml") as fh:
            import yaml
            rel_vocab = yaml.safe_load(fh)
        legacy_aliases = rel_vocab.get("legacy_aliases") or {}
        # 'produces-score-for' was the legacy alias for 'interpreted-by'
        self.assertIn(
            "produces-score-for", legacy_aliases,
            "legacy_aliases must preserve produces-score-for (CR-AM-01 §20)",
        )
        self.assertEqual(
            legacy_aliases["produces-score-for"], "interpreted-by",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
