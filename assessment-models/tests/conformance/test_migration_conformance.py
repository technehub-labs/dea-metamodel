"""
CR-AM-03 §18 migration conformance test — verifies semantic equivalence
between the legacy instrument and the canonical AssessmentModel for each
of the 4 migrated domains.

AC-AM03-04: All four migrations demonstrate preservation of existing
scoring semantics.
"""
import unittest
import hashlib
import json
import yaml
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]  # tests/conformance => repo root
ASSESSMENTS = REPO_ROOT / "assessment-models" / "migrations"

DOMAINS = ["technology", "modernization", "operations", "services-delivery"]


def _domain_legacy_path(domain):
    """Resolve the legacy path for tests. The CR-AM-03 migration manifest
    records the source; we read it to find the actual file."""
    m = REPO_ROOT / "assessment-models" / "migrations" / domain / "migration-manifest.yaml"
    with open(m) as fh:
        source = yaml.safe_load(fh)["migration"]["source"]
    src = source["path"] if isinstance(source, dict) else source
    if src.startswith("http"):
        return None
    return REPO_ROOT / src


def _load_legacy(domain):
    """Open the legacy YAML for a domain, or skip the test if it's external."""
    p = _domain_legacy_path(domain)
    if p is None:
        # The test author chose to skip an external legacy source.
        import unittest as _u
        _u.TestCase().skipTest(f"legacy source is external (URL) for {domain}; cannot read locally")
    with open(p) as fh:
        return yaml.safe_load(fh)


def _domain_canonical_path(domain):
    return ASSESSMENTS / domain / "canonical-assessment-model.yaml"


def _domain_conformance_path(domain):
    return ASSESSMENTS / domain / "conformance-report.yaml"


def _dimension_count(legacy_doc):
    return len(legacy_doc["dimensions"])


def _question_count(legacy_doc):
    return sum(len(d["questions"]) for d in legacy_doc["dimensions"])


class TestMigrationConformance(unittest.TestCase):
    """CR-AM-03 §18: each migration preserves existing semantics."""

    def test_legacy_paths_referenced_by_manifest(self):
        """AC-AM03-02: the manifest references a valid legacy source for each
        domain. The legacy is either a vendored local path or an external
        URL (the archived Assessment-Models org per-domain repo)."""
        for d in DOMAINS:
            manifest = REPO_ROOT / "assessment-models" / "migrations" / d / "migration-manifest.yaml"
            assert manifest.exists(), f"manifest missing for {d}"
            with open(manifest) as fh:
                m = yaml.safe_load(fh)
            source = m["migration"]["source"]
            src = source["path"] if isinstance(source, dict) else source
            # Local path: must exist. URL: just present (don't fetch).
            if src.startswith("http"):
                pass
            else:
                p = REPO_ROOT / src
                assert p.exists(), f"legacy path missing for {d}: {p} (referenced by manifest)"

    def test_legacy_instruments_validate_against_legacy_schema(self):
        """AC-AM03-02/04: every source instrument remains valid under v1."""
        import json
        from jsonschema import Draft202012Validator
        with open(REPO_ROOT / "assessment-models" / "migrations" / "v1-instrument" / "legacy-instrument.schema.json") as fh:
            legacy_schema = json.load(fh)
        validator = Draft202012Validator(legacy_schema)
        for d in DOMAINS:
            with open(_domain_legacy_path(d)) as fh:
                legacy = yaml.safe_load(fh)
            errs = list(validator.iter_errors(legacy))
            assert not errs, f"{d}: legacy instrument is invalid: {errs[0].message if errs else 'unknown'}"

    def _legacy_legacy_path(self, domain):
        """Resolve the legacy path: local file if vendored, else vendored
        into the migrations tree at generator time (only the Technology
        migration ships a vendored legacy copy)."""
        m = REPO_ROOT / "assessment-models" / "migrations" / domain / "migration-manifest.yaml"
        with open(m) as fh:
            source = yaml.safe_load(fh)["migration"]["source"]
        src = source["path"] if isinstance(source, dict) else source
        if src.startswith("http"):
            return None  # external; tests don't need to fetch
        return REPO_ROOT / src

    def test_canonical_paths_exist(self):
        for d in DOMAINS:
            p = _domain_canonical_path(d)
            assert p.exists(), f"canonical path missing for {d}: {p}"

    def test_conformance_reports_exist(self):
        for d in DOMAINS:
            p = _domain_conformance_path(d)
            assert p.exists(), f"conformance report missing for {d}: {p}"

    def test_execution_examples_validate_against_schema(self):
        """AC-AM03-11: every migration has a conformant completed execution."""
        try:
            from jsonschema import Draft202012Validator, RefResolver
            import json
        except ImportError:
            import unittest
            raise unittest.SkipTest("jsonschema not installed")
        with open(REPO_ROOT / "assessment-models" / "schemas" / "common.schema.json") as fh:
            common = json.load(fh)
        with open(REPO_ROOT / "assessment-models" / "schemas" / "assessment-execution.schema.json") as fh:
            execution_schema = json.load(fh)
        store = {
            "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
            "common.schema.json": common,
        }
        resolver = RefResolver(base_uri="", referrer=execution_schema, store=store)
        validator = Draft202012Validator(execution_schema, resolver=resolver)
        for d in DOMAINS:
            p = REPO_ROOT / "assessment-models" / "examples" / "executions" / f"{d}-execution.yaml"
            with open(p) as fh:
                doc = yaml.safe_load(fh)
            errs = list(validator.iter_errors(doc))
            assert not errs, f"{d}: execution does not validate: {errs[0].message if errs else 'unknown'}"
            assert doc.get("status") == "completed", f"{d}: completed execution required"

    def test_migration_manifests_expose_audit_metadata(self):
        """CR-AM03-03: manifests identify source, target, version, assessment, and compatibility."""
        required_axes = {"schema", "semantic", "scoring", "maturity", "result", "benchmark"}
        for d in DOMAINS:
            p = REPO_ROOT / "assessment-models" / "migrations" / d / "migration-manifest.yaml"
            with open(p) as fh:
                manifest = yaml.safe_load(fh)
            migration = manifest["migration"]
            source = migration["source"]
            target = migration["target"]
            assert source["type"] == "legacy-instrument"
            assert target["type"] == "assessment-model"
            assert migration["migration_version"]
            assert migration["semantic_equivalence"]["status"] in {
                "CONFORMANT", "CONFORMANT-WITH-NOTES", "NON-CONFORMANT"
            }
            assert required_axes <= set(migration["compatibility"])

    def test_vendored_legacy_instruments_are_byte_identical(self):
        """AC-AM03-02: the source copy is unchanged and locally resolvable."""
        for d in DOMAINS:
            p = REPO_ROOT / "assessment-models" / "migrations" / d / "legacy-instrument.yaml"
            assert p.exists(), f"{d}: vendored legacy instrument missing"
            manifest = yaml.safe_load((p.parent / "migration-manifest.yaml").read_text())
            assert hashlib.sha256(p.read_bytes()).hexdigest() == manifest["migration"]["source"]["sha256"]

    def test_dimension_count_preserved(self):
        """AC-AM03-04: dimension count is preserved."""
        for d in DOMAINS:
            legacy = _load_legacy(d)
            with open(_domain_canonical_path(d)) as fh:
                canonical = yaml.safe_load(fh)
            assert _dimension_count(legacy) == len(canonical["dimensions"]), (
                f"{d}: legacy dim count {_dimension_count(legacy)} != canonical {len(canonical['dimensions'])}"
            )

    def test_question_count_preserved(self):
        """AC-AM03-04: question count is preserved."""
        for d in DOMAINS:
            legacy = _load_legacy(d)
            with open(_domain_canonical_path(d)) as fh:
                canonical = yaml.safe_load(fh)
            assert _question_count(legacy) == sum(
                len(dim.get("questions", [])) for dim in canonical["dimensions"]
            ), f"{d}: question count mismatch"

    def test_scoring_scale_preserved(self):
        """AC-AM03-04: legacy 4-point scale [0,1,2,3] -> canonical scoring_model ref."""
        for d in DOMAINS:
            legacy = _load_legacy(d)
            with open(_domain_canonical_path(d)) as fh:
                canonical = yaml.safe_load(fh)
            sm = canonical.get("scoring_model")
            assert sm is not None, f"{d}: canonical missing scoring_model"
            assert sm["id"] == "dea:scoring-four-point", (
                f"{d}: scoring_model.id should be dea:scoring-four-point, got {sm['id']!r}"
            )
            # Verify every legacy question has [0,1,2,3]
            for dim in legacy["dimensions"]:
                for q in dim["questions"]:
                    assert q["scoring"] == [0, 1, 2, 3], f"{d}/{q['id']}: scoring array not [0,1,2,3]"

    def test_dimension_weights_preserved(self):
        """AC-AM03-04: dimension weights are preserved verbatim on the canonical side."""
        for d in DOMAINS:
            legacy = _load_legacy(d)
            with open(_domain_canonical_path(d)) as fh:
                canonical = yaml.safe_load(fh)
            for i, dim in enumerate(legacy["dimensions"]):
                cdim = canonical["dimensions"][i]
                assert dim.get("weight") == cdim.get("weight"), (
                    f"{d}/{dim['id']}: weight drift legacy={dim.get('weight')} canonical={cdim.get('weight')}"
                )

    def test_maturity_target_preserved(self):
        """AC-AM03-04: legacy maturity_target.id appears in canonical maturity_models[].id."""
        for d in DOMAINS:
            legacy = _load_legacy(d)
            with open(_domain_canonical_path(d)) as fh:
                canonical = yaml.safe_load(fh)
            legacy_mid = legacy["maturity_target"]
            canonical_mids = [m["id"] for m in canonical.get("maturity_models", [])]
            # legacy_mid is `dea-maturity-<domain>`; canonical is `dea:maturity-<domain>`
            expected = legacy_mid.replace("dea-", "dea:")
            assert expected in canonical_mids, f"{d}: legacy maturity_target {legacy_mid!r} (expected {expected!r}) not in {canonical_mids}"

    def test_description_preserved(self):
        """AC-AM03-04: description string round-trips identically (modulo whitespace)."""
        for d in DOMAINS:
            legacy = _load_legacy(d)
            with open(_domain_canonical_path(d)) as fh:
                canonical = yaml.safe_load(fh)
            assert (legacy["description"] or "") == (canonical["description"] or ""), (
                f"{d}: description drift"
            )

    def test_question_text_and_evidence_preserved(self):
        """AC-AM03-04/18: all question text and evidence remain auditable."""
        for d in DOMAINS:
            legacy = _load_legacy(d)
            with open(_domain_canonical_path(d)) as fh:
                canonical = yaml.safe_load(fh)
            legacy_questions = [q for dim in legacy["dimensions"] for q in dim["questions"]]
            canonical_metadata = canonical.get("metadata", {})
            assert [q["text"] for q in legacy_questions] == [q["text"] for q in [
                q for dim in canonical_metadata.get("legacy_dimensions", []) for q in dim["questions"]
            ]]
            assert [evidence for q in legacy_questions for evidence in q.get("evidence", [])] == [
                evidence for dim in canonical_metadata.get("legacy_dimensions", []) for q in dim["questions"] for evidence in q.get("evidence", [])
            ]

    def test_conformance_levels_known(self):
        """Each conformance report declares a known level."""
        valid = {"CONFORMANT", "CONFORMANT-WITH-NOTES", "NON-CONFORMANT"}
        for d in DOMAINS:
            with open(_domain_conformance_path(d)) as fh:
                rep = yaml.safe_load(fh)
            level = rep["conformance"]["level"]
            assert level in valid, f"{d}: invalid level {level!r}"

    def test_canonical_assessments_validate_against_schema(self):
        """Each canonical AssessmentModel validates against assessment-model.schema.json."""
        try:
            from jsonschema import Draft202012Validator, RefResolver
            import json
        except ImportError:
            import unittest
            raise unittest.SkipTest("jsonschema not installed")
        with open(REPO_ROOT / "assessment-models" / "schemas" / "common.schema.json") as fh:
            common = json.load(fh)
        with open(REPO_ROOT / "assessment-models" / "schemas" / "assessment-model.schema.json") as fh:
            am = json.load(fh)
        store = {
            "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
            "common.schema.json": common,
        }
        for d in DOMAINS:
            with open(_domain_canonical_path(d)) as fh:
                doc = yaml.safe_load(fh)
            resolver = RefResolver(base_uri="", referrer=am, store=store)
            v = Draft202012Validator(am, resolver=resolver)
            errs = list(v.iter_errors(doc))
            assert not errs, f"{d}: canonical projection does not validate: {errs[0].message}"

    def test_result_examples_validate_against_schema(self):
        """Each result example validates against assessment-result.schema.json."""
        try:
            from jsonschema import Draft202012Validator, RefResolver
            import json
        except ImportError:
            import unittest
            raise unittest.SkipTest("jsonschema not installed")
        with open(REPO_ROOT / "assessment-models" / "schemas" / "common.schema.json") as fh:
            common = json.load(fh)
        with open(REPO_ROOT / "assessment-models" / "schemas" / "assessment-result.schema.json") as fh:
            ar = json.load(fh)
        store = {
            "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
            "common.schema.json": common,
        }
        for d in DOMAINS:
            p = REPO_ROOT / "assessment-models" / "examples" / f"{d}-result.yaml"
            if not p.exists():
                continue  # technology-result not part of this CR
            with open(p) as fh:
                doc = yaml.safe_load(fh)
            # CR-AM-04 results carry the new required fields
            # (determinations, maturity_interpretation, evidence, aggregation_model).
            # CR-AM-03-era result examples remain valid but skip the strict
            # validation here; their reproduction contract is verified by
            # assessment-models/tests/conformance/test_result_operations.py
            # via the canonical runtime service.
            if "determinations" not in doc:
                continue
            resolver = RefResolver(base_uri="", referrer=ar, store=store)
            v = Draft202012Validator(ar, resolver=resolver)
            errs = list(v.iter_errors(doc))
            assert not errs, f"{d}: result does not validate: {errs[0].message}"


if __name__ == "__main__":
    import unittest
    unittest.main(verbosity=2)
