"""
CR-AM-03 §15 portfolio test — verifies all 4 migrated assessments are
discoverable through the assessment-portfolio.yaml index.

AC-AM03-15: All migrated AssessmentModels are discoverable through the
Assessment Portfolio.
"""
import unittest
import yaml
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]  # tests/portfolio => repo root
PORTFOLIO = REPO_ROOT / "assessment-models" / "catalog" / "assessment-portfolio.yaml"
MIGRATIONS = REPO_ROOT / "assessment-models" / "migrations"

REQUIRED_DOMAINS = {"technology", "modernization", "operations", "services-delivery"}

class TestAssessmentPortfolio(unittest.TestCase):
    """CR-AM-03 §7: Assessment Portfolio is the authoritative discovery point."""

    def test_portfolio_file_exists(self):
        assert PORTFOLIO.exists(), f"portfolio missing: {PORTFOLIO}"

    def test_portfolio_lists_all_four_domains(self):
        with open(PORTFOLIO) as fh:
            doc = yaml.safe_load(fh)
        items = doc["portfolio"]["assessments"]
        ids = {a["id"] for a in items}
        for d in REQUIRED_DOMAINS:
            assert f"dea:assessment-{d}" in ids, f"portfolio missing domain {d}: {ids}"

    def test_portfolio_vendored_sources_exist(self):
        """AC-AM03-02: portfolio references local, byte-verifiable source files."""
        with open(PORTFOLIO) as fh:
            doc = yaml.safe_load(fh)
        for a in doc["portfolio"]["assessments"]:
            p = REPO_ROOT / a["legacy_source"]
            assert p.exists(), f"legacy_source does not exist: {a['legacy_source']}"

    def test_each_assessment_has_required_metadata(self):
        """AC-AM03-15: each assessment has capabilities, scenarios, measures,
        scoring_model, maturity_models, legacy_source, canonical_source, migration_status."""
        with open(PORTFOLIO) as fh:
            doc = yaml.safe_load(fh)
        required = {
            "id", "name", "version", "lifecycle_status", "domain",
            "capabilities", "scenarios", "measures", "scoring_model",
            "maturity_models", "legacy_source", "canonical_source", "migration_status",
        }
        for a in doc["portfolio"]["assessments"]:
            missing = required - set(a.keys())
            assert not missing, f"assessment {a['id']} missing keys: {missing}"

    def test_canonical_source_path_resolves(self):
        """Each canonical_source must be a path that exists in the repo."""
        with open(PORTFOLIO) as fh:
            doc = yaml.safe_load(fh)
        for a in doc["portfolio"]["assessments"]:
            p = REPO_ROOT / a["canonical_source"]
            assert p.exists(), f"canonical_source does not exist: {a['canonical_source']}"

    def test_migration_status_is_known(self):
        """Migration status must be one of: CONFORMANT, CONFORMANT-WITH-NOTES, NON-CONFORMANT."""
        with open(PORTFOLIO) as fh:
            doc = yaml.safe_load(fh)
        valid = {"CONFORMANT", "CONFORMANT-WITH-NOTES", "NON-CONFORMANT"}
        for a in doc["portfolio"]["assessments"]:
            assert a["migration_status"] in valid, f"{a['id']}: invalid migration_status {a['migration_status']!r}"

    def test_portfolio_references_versioned_models(self):
        """CR-AM-03 §6.4: portfolio references carry exact versions."""
        with open(PORTFOLIO) as fh:
            doc = yaml.safe_load(fh)
        for a in doc["portfolio"]["assessments"]:
            for field in ("capabilities", "scenarios", "measures", "maturity_models"):
                for ref in a[field]:
                    assert ":1.0.0" in ref, f"{a['id']}: unversioned {field} ref {ref}"
            assert a["scoring_model"].endswith(":1.0.0")

    def test_portfolio_references_resolve_from_catalogue(self):
        """CR-AM03-05..10: portfolio references resolve against the reference catalogue."""
        catalogue = yaml.safe_load((REPO_ROOT / "assessment-models/catalog/reference-catalog.yaml").read_text())
        available = {(r["kind"], r["id"], r["version"]) for r in catalogue["catalogue"]["references"]}
        portfolio = yaml.safe_load(PORTFOLIO.read_text())
        for a in portfolio["portfolio"]["assessments"]:
            for field, kind in (("capabilities", "capability"), ("scenarios", "scenario"), ("measures", "measure"), ("maturity_models", "maturity-model")):
                for ref in a[field]:
                    id_, version = ref.rsplit(":", 1)
                    assert (kind, id_, version) in available, f"{a['id']}: unresolved {kind} reference {ref}"
            ref = a["scoring_model"]
            id_, version = ref.rsplit(":", 1)
            assert ("scoring-model", id_, version) in available, f"{a['id']}: unresolved scoring model {ref}"


if __name__ == "__main__":
    import unittest
    unittest.main(verbosity=2)
