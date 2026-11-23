"""CR-AM-13 structural validation tests for maturity-touchpoints.schema.json.

Reproducible schema-validation evidence for CR-AM-13 acceptance criteria
AC-02 (paired peer-mirroring fields) and AC-03 (reciprocity vocabulary),
per the CR's §8 test requirements. Offline-only: the schema is loaded from
the repository; no network or sibling-repo access.

Boundary note (CR-AM-13-R04): the final test documents that structural
validity is not semantic validity — a record referencing a nonexistent peer
touchpoint passes local validation and remains unresolved until ecosystem-
level validation (Assessment-Models/assessment-ci, not yet implemented)
runs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "assessment-models"
    / "schemas"
    / "maturity-touchpoints.schema.json"
)


@pytest.fixture(scope="module")
def validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate(validator: Draft202012Validator, manifest: dict) -> list[str]:
    return [e.message for e in validator.iter_errors(manifest)]


def manifest_with(touchpoint: dict) -> dict:
    return {
        "id": "dea:touchpoints-test-model-v1",
        "repo_id": "maturity-model-test",
        "version": "0.1.0",
        "status": "draft",
        "touchpoints": [touchpoint],
    }


# ---------------------------------------------------------------------------
# Positive cases (CR-AM-13 §8)
# ---------------------------------------------------------------------------


def test_record_without_mirroring_is_valid(validator):
    """A touchpoint record without a peer-mirroring relationship remains valid."""
    manifest = manifest_with(
        {
            "id": "tp-test-x-peer",
            "peer_asset": "dea:maturity-peer",
            "peer_repo": "maturity-model-peer",
            "direction": "feeds",
            "mapping_type": "feeds",
            "reciprocity": "mirrors-tp-peer-x-test",
        }
    )
    assert validate(validator, manifest) == []


def test_record_with_paired_mirroring_is_valid(validator):
    """A record declaring both mirrors and peer_touchpoint_id is structurally valid."""
    manifest = manifest_with(
        {
            "id": "tp-test-x-peer",
            "peer_asset": "dea:maturity-peer",
            "peer_repo": "maturity-model-peer",
            "direction": "consumes",
            "mapping_type": "consumes",
            "mirrors": "tp-peer-x-test",
            "peer_touchpoint_id": "tp-peer-x-test",
            "reciprocity": "mirrors-tp-peer-x-test",
        }
    )
    assert validate(validator, manifest) == []


def test_mirrors_convention_reciprocity_is_accepted(validator):
    """A record using the established mirrors-* reciprocity declaration is accepted."""
    manifest = manifest_with(
        {
            "id": "tp-test-x-peer",
            "peer_asset": "dea:maturity-peer",
            "peer_repo": "maturity-model-peer",
            "direction": "feeds",
            "mapping_type": "feeds",
            "reciprocity": "mirrors-tp-ops-x-test",
        }
    )
    assert validate(validator, manifest) == []


def test_full_realistic_manifest_is_valid(validator):
    """A full manifest — handshake, summary, overlap resolution, criteria mapping,
    mirror record fields — validates structurally (operations-style shape)."""
    manifest = {
        "id": "dea:touchpoints-test-model-v1",
        "repo_id": "maturity-model-test",
        "version": "0.3.0",
        "status": "draft",
        "metamodel_version": "1.0.0",
        "description": "Test manifest.",
        "handshakes": [
            {
                "id": "hs-scoring",
                "kind": "scored-by",
                "contract": {"id": "maturity-scale-contract", "version": "1.0"},
                "asset": {
                    "id": "dea:maturity-bands-v2",
                    "organization": "technehub-labs",
                    "repository": "dea-metamodel",
                    "reference": "v1.0.0",
                },
            }
        ],
        "touchpoints": [
            {
                "id": "tp-test-x-peer",
                "peer_asset": "dea:maturity-peer",
                "peer_repo": "maturity-model-peer",
                "peer_contract_version": "^1.0",
                "direction": "feeds",
                "mapping_type": "feeds",
                "summary": "Evidence feeds the peer.",
                "overlap_resolution": "Boundary doctrine.",
                "criteria_mapping": [
                    {"ours": "TST-D01-SD01-C01", "theirs": "PR-D1-C01", "note": "shared evidence"},
                    {"ours": "TST-D02-SD01-C01", "theirs": "pending-peer-register"},
                ],
                "mirrors": "tp-peer-x-test",
                "peer_touchpoint_id": "tp-peer-x-test",
                "reciprocity": "mirrors-tp-peer-x-test",
                "peer_status": "peer-remap-pending",
            }
        ],
    }
    assert validate(validator, manifest) == []


# ---------------------------------------------------------------------------
# Negative cases (CR-AM-13 §8, CR-AM-13-R02, CR-AM-13-R03)
# ---------------------------------------------------------------------------


def test_mirrors_without_peer_touchpoint_id_is_rejected(validator):
    """A record declaring mirrors without peer_touchpoint_id is rejected."""
    manifest = manifest_with(
        {
            "id": "tp-test-x-peer",
            "peer_asset": "dea:maturity-peer",
            "peer_repo": "maturity-model-peer",
            "direction": "feeds",
            "mapping_type": "feeds",
            "mirrors": "tp-peer-x-test",
            "reciprocity": "mirrors-tp-peer-x-test",
        }
    )
    errors = validate(validator, manifest)
    assert any("peer_touchpoint_id" in e for e in errors)


def test_peer_touchpoint_id_without_mirrors_is_rejected(validator):
    """A record declaring peer_touchpoint_id without mirrors is rejected."""
    manifest = manifest_with(
        {
            "id": "tp-test-x-peer",
            "peer_asset": "dea:maturity-peer",
            "peer_repo": "maturity-model-peer",
            "direction": "feeds",
            "mapping_type": "feeds",
            "peer_touchpoint_id": "tp-peer-x-test",
            "reciprocity": "mirrors-tp-peer-x-test",
        }
    )
    errors = validate(validator, manifest)
    assert any("mirrors" in e for e in errors)


def test_empty_string_mirroring_fields_are_rejected(validator):
    """Empty strings do not constitute a resolvable paired declaration."""
    manifest = manifest_with(
        {
            "id": "tp-test-x-peer",
            "peer_asset": "dea:maturity-peer",
            "peer_repo": "maturity-model-peer",
            "direction": "feeds",
            "mapping_type": "feeds",
            "mirrors": "",
            "peer_touchpoint_id": "",
            "reciprocity": "mirrors-tp-peer-x-test",
        }
    )
    errors = validate(validator, manifest)
    assert len(errors) >= 2  # minLength violated on both fields


def test_retired_required_reciprocity_is_rejected(validator):
    """The bare `required` placeholder is retired (CR-AM-13-R03 vocabulary
    transition) and must fail structural validation."""
    manifest = manifest_with(
        {
            "id": "tp-test-x-peer",
            "peer_asset": "dea:maturity-peer",
            "peer_repo": "maturity-model-peer",
            "direction": "feeds",
            "mapping_type": "feeds",
            "reciprocity": "required",
        }
    )
    errors = validate(validator, manifest)
    assert any("does not match" in e for e in errors)


def test_arbitrary_reciprocity_is_rejected(validator):
    """A record using an invalid reciprocity declaration is rejected."""
    manifest = manifest_with(
        {
            "id": "tp-test-x-peer",
            "peer_asset": "dea:maturity-peer",
            "peer_repo": "maturity-model-peer",
            "direction": "feeds",
            "mapping_type": "feeds",
            "reciprocity": "some-day-maybe",
        }
    )
    assert validate(validator, manifest) != []


def test_malformed_criteria_mapping_is_rejected(validator):
    """A criterion mapping missing `theirs` is rejected."""
    manifest = manifest_with(
        {
            "id": "tp-test-x-peer",
            "peer_asset": "dea:maturity-peer",
            "peer_repo": "maturity-model-peer",
            "direction": "feeds",
            "mapping_type": "feeds",
            "criteria_mapping": [{"ours": "TST-D01-SD01-C01"}],
            "reciprocity": "mirrors-tp-peer-x-test",
        }
    )
    errors = validate(validator, manifest)
    assert any("theirs" in e for e in errors)


def test_unknown_touchpoint_property_is_rejected(validator):
    """Unknown fields fail closed (additionalProperties: false)."""
    manifest = manifest_with(
        {
            "id": "tp-test-x-peer",
            "peer_asset": "dea:maturity-peer",
            "peer_repo": "maturity-model-peer",
            "direction": "feeds",
            "mapping_type": "feeds",
            "reciprocity": "mirrors-tp-peer-x-test",
            "extra_field": "not in the contract",
        }
    )
    errors = validate(validator, manifest)
    assert any("extra_field" in e for e in errors)


def test_invalid_direction_enum_is_rejected(validator):
    """A record with invalid field types or values is rejected."""
    manifest = manifest_with(
        {
            "id": "tp-test-x-peer",
            "peer_asset": "dea:maturity-peer",
            "peer_repo": "maturity-model-peer",
            "direction": "sympathizes",
            "mapping_type": "feeds",
            "reciprocity": "mirrors-tp-peer-x-test",
        }
    )
    assert validate(validator, manifest) != []


# ---------------------------------------------------------------------------
# Validation boundary case (CR-AM-13 §8, CR-AM-13-R04)
# ---------------------------------------------------------------------------


def test_structurally_valid_record_with_unresolvable_peer_passes_locally(validator):
    """Structurally valid != semantically valid: a record referencing a
    nonexistent peer touchpoint passes LOCAL structural validation.

    This is the documented boundary: reciprocity (existence of and
    consistency with the referenced peer record) is ecosystem-level
    semantic validation owned by Assessment-Models/assessment-ci, which is
    not yet implemented. Such a record is conformant here but remains
    semantically unresolved.
    """
    manifest = manifest_with(
        {
            "id": "tp-test-x-nonexistent-peer",
            "peer_asset": "dea:maturity-does-not-exist",
            "peer_repo": "maturity-model-does-not-exist",
            "direction": "feeds",
            "mapping_type": "feeds",
            "mirrors": "tp-nonexistent-peer-x-test",
            "peer_touchpoint_id": "tp-nonexistent-peer-x-test",
            "reciprocity": "mirrors-tp-nonexistent-peer-x-test",
        }
    )
    # Structural validation passes — it MUST NOT be read as reciprocity proof.
    assert validate(validator, manifest) == []
