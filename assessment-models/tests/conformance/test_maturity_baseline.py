"""CR-AM-09 Phase 4 baseline locking & migration conformance tests.

Covers the Phase 4 contract (CR-AM-09 §12 Phase 4): the
MaturityScaleBaseline schema (immutable, benchmark-locked), the
historical-reproducibility discipline (content hash over the snapshot —
spec test 7), and the evolutionary migration of v1/v2-beta maturity
content into the scale structure (spec test 8 — mapping, not
re-authoring).
"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, RefResolver

REPO_ROOT = Path(__file__).resolve().parents[3]

BASELINE_SCHEMA_PATH = "assessment-models/schemas/maturity-scale-baseline.schema.json"
LEVEL_SCHEMA_PATH = "assessment-models/schemas/maturity-level.schema.json"
BASELINE_EXAMPLE_PATH = (
    "assessment-models/maturity/baseline-examples/"
    "proactive-operations-benchmark-2027.yaml"
)
SCALE_EXAMPLE_PATH = (
    "assessment-models/maturity/scale-examples/"
    "proactive-operations-alternate-naming.yaml"
)
BANDS_EXAMPLE_PATH = (
    "assessment-models/maturity/resolution-examples/"
    "proactive-operations-bands.yaml"
)
RULE_EXAMPLE_PATH = (
    "assessment-models/maturity/resolution-examples/"
    "proactive-operations-resolution.yaml"
)
EVAL_EXAMPLE_PATH = (
    "assessment-models/maturity/evaluation-examples/"
    "proactive-operations-evaluation.yaml"
)
MIGRATION_MAP_PATH = (
    "assessment-models/maturity/migration/v2-beta-to-scale-map.yaml"
)
V2_BETA_PATH = "assessment-models/maturity/maturity-bands-v2.yaml"
V1_LEGACY_MAP_PATH = "assessment-models/maturity/v2-to-v1-legacy-name-map.yaml"
# CR-AM-11 Phase 3 — the OpenDEA Enterprise Architecture reference instance.
OPENDEA_EA_BASELINE_PATH = (
    "assessment-models/maturity/baseline-examples/"
    "opendea-enterprise-architecture.yaml"
)
OPENDEA_EA_BASELINE_SCALE_PATH = (
    "assessment-models/maturity/scale-examples/"
    "opendea-enterprise-architecture.yaml"
)
OPENDEA_EA_BASELINE_EVAL_PATH = (
    "assessment-models/maturity/evaluation-examples/"
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


def canonical_snapshot_hash(snapshot) -> str:
    canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()


class BaselineSchemaTest(unittest.TestCase):
    """Baseline schema integrity (CR-AM-09 §8)."""

    def test_schema_parses_as_draft_2020_12(self):
        schema = load_json(BASELINE_SCHEMA_PATH)
        self.assertEqual(
            schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_required_fields_match_spec(self):
        schema = load_json(BASELINE_SCHEMA_PATH)
        for field in ("id", "version", "status", "scale", "locked_at",
                      "content_hash", "snapshot"):
            self.assertIn(field, schema["required"])

    def test_snapshot_carries_full_contract(self):
        schema = load_json(BASELINE_SCHEMA_PATH)
        snap = schema["properties"]["snapshot"]
        for field in ("levels", "progression", "band_set", "resolution_rule"):
            self.assertIn(field, snap["required"])

    def test_baseline_example_validates(self):
        doc = load_yaml(BASELINE_EXAMPLE_PATH)
        errors = list(_validator(BASELINE_SCHEMA_PATH).iter_errors(doc))
        self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors])

    def test_baseline_without_lock_is_refused(self):
        doc = load_yaml(BASELINE_EXAMPLE_PATH)
        del doc["locked_at"]
        errors = list(_validator(BASELINE_SCHEMA_PATH).iter_errors(doc))
        self.assertTrue(errors)

    def test_baseline_without_hash_is_refused(self):
        doc = load_yaml(BASELINE_EXAMPLE_PATH)
        del doc["content_hash"]
        errors = list(_validator(BASELINE_SCHEMA_PATH).iter_errors(doc))
        self.assertTrue(errors)


class HistoricalReproducibilityTest(unittest.TestCase):
    """Spec test 7 (CR-AM-09 §8/§35): given the benchmark baseline, the
    exact scale contract is reconstructable — content hash verifies."""

    def test_content_hash_recomputes_over_snapshot(self):
        """The reproducibility anchor: sha256 over the canonical JSON of
        the snapshot block must equal the declared content_hash. Any
        mutation of the snapshot invalidates the baseline."""
        doc = load_yaml(BASELINE_EXAMPLE_PATH)
        self.assertEqual(canonical_snapshot_hash(doc["snapshot"]),
                         doc["content_hash"])

    def test_snapshot_mutation_breaks_the_hash(self):
        doc = load_yaml(BASELINE_EXAMPLE_PATH)
        doc["snapshot"]["levels"][0]["definition"] = "tampered"
        self.assertNotEqual(canonical_snapshot_hash(doc["snapshot"]),
                            doc["content_hash"],
                            "a mutated snapshot must invalidate the hash")

    def test_snapshot_levels_match_the_locked_scale(self):
        """The snapshot levels are a faithful copy of the Phase 1 scale's
        levels (id + ordinal + name + definition)."""
        doc = load_yaml(BASELINE_EXAMPLE_PATH)
        scale = load_yaml(SCALE_EXAMPLE_PATH)
        snap_levels = {l["id"]: l for l in doc["snapshot"]["levels"]}
        scale_levels = {l["id"]: l for l in scale["levels"]}
        self.assertEqual(set(scale_levels), set(snap_levels))
        for lid in snap_levels:
            for field in ("ordinal", "name"):
                self.assertEqual(scale_levels[lid][field],
                                 snap_levels[lid][field])

    def test_snapshot_progression_matches_the_locked_scale(self):
        doc = load_yaml(BASELINE_EXAMPLE_PATH)
        scale = load_yaml(SCALE_EXAMPLE_PATH)
        self.assertEqual(scale["progression"]["topology"],
                         doc["snapshot"]["progression"]["topology"])
        self.assertEqual(scale["progression"]["function"],
                         doc["snapshot"]["progression"]["function"])

    def test_snapshot_references_resolve_to_landed_artifacts(self):
        """band_set / resolution_rule / evaluation_model references
        resolve to the landed Phase 2/3 examples (id + version)."""
        doc = load_yaml(BASELINE_EXAMPLE_PATH)
        bands = load_yaml(BANDS_EXAMPLE_PATH)
        rule = load_yaml(RULE_EXAMPLE_PATH)
        evaluation = load_yaml(EVAL_EXAMPLE_PATH)
        snap = doc["snapshot"]
        self.assertEqual((bands["id"], bands["version"]),
                         (snap["band_set"]["id"], snap["band_set"]["version"]))
        self.assertEqual((rule["id"], rule["version"]),
                         (snap["resolution_rule"]["id"],
                          snap["resolution_rule"]["version"]))
        self.assertEqual((evaluation["id"], evaluation["version"]),
                         (snap["evaluation_model"]["id"],
                          snap["evaluation_model"]["version"]))


class MigrationMappingTest(unittest.TestCase):
    """Spec test 8 (CR-AM-09 §11 constraint 6): v1/v2-beta content maps
    INTO the scale structure — evolutionary, never re-authored."""

    def test_every_v2_beta_band_maps_exactly_once(self):
        migration = load_yaml(MIGRATION_MAP_PATH)
        v2 = load_yaml(V2_BETA_PATH)
        v2_ids = [b["id"] for b in v2["bands"]]
        mapped = [m["source_band"] for m in migration["level_map"]]
        self.assertEqual(sorted(v2_ids), sorted(mapped),
                         "every v2-beta band must map exactly once")

    def test_target_levels_carry_verbatim_source_semantics(self):
        """The map must not re-author content: target definitions equal
        the v2-beta summaries verbatim."""
        migration = load_yaml(MIGRATION_MAP_PATH)
        v2 = load_yaml(V2_BETA_PATH)
        v2_by_id = {b["id"]: b for b in v2["bands"]}
        for entry in migration["level_map"]:
            source = v2_by_id[entry["source_band"]]
            self.assertEqual(source["name"], entry["target_level"]["name"])
            self.assertEqual(source["summary"],
                             entry["target_level"]["definition"],
                             f"{entry['source_band']}: definition must be "
                             "the v2-beta summary verbatim — migration maps, "
                             "it does not re-author")

    def test_legacy_v1_names_match_the_existing_alias_map(self):
        """The v1 legacy names in the migration map must agree with the
        existing v2-to-v1 legacy name map (no new aliases invented)."""
        migration = load_yaml(MIGRATION_MAP_PATH)
        v2 = load_yaml(V2_BETA_PATH)
        v2_by_id = {b["id"]: b for b in v2["bands"]}
        for entry in migration["level_map"]:
            self.assertEqual(v2_by_id[entry["source_band"]]["legacy_name"],
                             entry["legacy_v1_name"])

    def test_target_ordinals_strictly_ascending(self):
        migration = load_yaml(MIGRATION_MAP_PATH)
        ordinals = [m["target_level"]["ordinal"] for m in migration["level_map"]]
        self.assertEqual(sorted(ordinals), ordinals)
        self.assertEqual(len(set(ordinals)), len(ordinals))

    def test_target_scale_declares_linear_exponential_progression(self):
        """The v2-beta effort multipliers (1.0 → 6.0) are the
        superlinear-effort insight: linear topology, exponential
        function. The migration target scale declares exactly that."""
        migration = load_yaml(MIGRATION_MAP_PATH)
        prog = migration["target_scale"]["progression"]
        self.assertEqual("linear", prog["topology"])
        self.assertEqual("exponential", prog["function"])

    def test_source_ranges_preserved(self):
        migration = load_yaml(MIGRATION_MAP_PATH)
        v2 = load_yaml(V2_BETA_PATH)
        v2_by_id = {b["id"]: b for b in v2["bands"]}
        for entry in migration["level_map"]:
            self.assertEqual(v2_by_id[entry["source_band"]]["range"],
                             entry["source_range"])


class BaselineBoundaryGuardTest(unittest.TestCase):
    """Phase 4 boundaries: baseline schema extends maturity semantics
    without touching frozen CR-AM-06/07 comparison surfaces."""

    def test_frozen_surfaces_untouched(self):
        text = (REPO_ROOT / BASELINE_SCHEMA_PATH).read_text()
        for term in ("eligibility_criteria", "benchmark-status",
                     "standings", "percentile"):
            self.assertNotIn(term, text)


class OpenDEAEaReferenceBaselineTest(unittest.TestCase):
    """CR-AM-11 §6/§24 — the OpenDEA EA reference instance baseline must
    validate against the maturity-scale-baseline schema, lock a faithful
    snapshot of its scale's levels + progression, and resolve its
    evaluation_model reference to the matching evaluation example.
    content_hash reproducibility pins the snapshot."""

    def test_reference_baseline_validates(self):
        doc = load_yaml(OPENDEA_EA_BASELINE_PATH)
        errors = list(_validator(BASELINE_SCHEMA_PATH).iter_errors(doc))
        self.assertEqual(
            [], [f"{list(e.path)}: {e.message}" for e in errors],
            "opendea-ea baseline must validate against maturity-scale-baseline schema")

    def test_snapshot_levels_match_the_reference_scale(self):
        doc = load_yaml(OPENDEA_EA_BASELINE_PATH)
        scale = load_yaml(OPENDEA_EA_BASELINE_SCALE_PATH)
        snap_levels = {l["id"]: l for l in doc["snapshot"]["levels"]}
        scale_levels = {l["id"]: l for l in scale["levels"]}
        self.assertEqual(set(scale_levels), set(snap_levels))
        for lid in snap_levels:
            for field in ("ordinal", "name"):
                self.assertEqual(scale_levels[lid][field],
                                 snap_levels[lid][field])

    def test_snapshot_progression_matches_the_reference_scale(self):
        doc = load_yaml(OPENDEA_EA_BASELINE_PATH)
        scale = load_yaml(OPENDEA_EA_BASELINE_SCALE_PATH)
        self.assertEqual(scale["progression"]["topology"],
                         doc["snapshot"]["progression"]["topology"])
        self.assertEqual(scale["progression"]["function"],
                         doc["snapshot"]["progression"]["function"])

    def test_snapshot_evaluation_reference_resolves(self):
        doc = load_yaml(OPENDEA_EA_BASELINE_PATH)
        evaluation = load_yaml(OPENDEA_EA_BASELINE_EVAL_PATH)
        snap = doc["snapshot"]
        self.assertEqual((evaluation["id"], evaluation["version"]),
                         (snap["evaluation_model"]["id"],
                          snap["evaluation_model"]["version"]))

    def test_snapshot_band_set_resolves_to_v2_canonical(self):
        doc = load_yaml(OPENDEA_EA_BASELINE_PATH)
        snap = doc["snapshot"]
        # The reference instance pins the canonical v2 band instance
        # (maturation/v2 bands) per the maturity-v2 migration Phase 3.
        self.assertEqual("dea:maturity-bands-v2", snap["band_set"]["id"])
        self.assertEqual("1.0.0", snap["band_set"]["version"])


if __name__ == "__main__":
    unittest.main()
