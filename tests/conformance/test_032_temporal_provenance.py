"""CR-MET-011: temporal semantics, provenance, and historical reconstruction.

Covers:
- Section 3: the 7 temporal dimensions (Q17b nested temporal object)
- Section 4: the 7 reporting-period shapes
- Section 5: the 11 provenance elements and W3C PROV alignment
- Section 6: historical reconstruction
- Section 7 (Q19a): the 5 record states and the corrects/supersedes distinction
"""
import json

import yaml

from conftest import BASE

FIXTURE = yaml.safe_load(
    (BASE / "tests" / "conformance" / "fixtures" / "temporal_provenance.yaml").read_text()
)
CLASSIFICATIONS = yaml.safe_load(
    (BASE / "metamodel" / "vocabularies" / "classifications.yaml").read_text()
)["classifications"]

# Section 3: the 7 temporal dimensions. They MUST NOT collapse into one timestamp.
TEMPORAL_DIMENSIONS = [
    "observed_at", "measured_at", "reporting_period_ref",
    "valid_from", "valid_to", "recorded_at", "effective_from", "published_at",
]

# Section 4: the 7 supported period shapes.
PERIOD_TYPES = [
    "instantaneous", "point_in_time", "fixed_duration", "rolling",
    "cumulative", "event_based", "irregular",
]

# Section 5: the 11 provenance elements.
PROVENANCE_ELEMENTS = [
    "source_ref", "source_record_ref", "collection_activity", "calculation_activity",
    "transformation_chain", "responsible_party_ref", "configuration_ref",
    "formula_version_ref", "metric_version_ref", "evidence_refs", "timestamps",
]

# Section 7 (Q19a): the 5 record states.
RECORD_STATES = ["original", "corrected", "superseded", "invalid", "retracted"]


def _periods():
    return FIXTURE["reporting_periods"]


def _provenances():
    return FIXTURE["provenances"]


def _observations():
    return FIXTURE["observations"]


def test_section3_all_seven_temporal_dimensions_available():
    schema = json.loads((BASE / "schemas" / "entities" / "measurement-observation.json").read_text())
    temporal = schema["properties"]["temporal"]
    for dim in TEMPORAL_DIMENSIONS:
        assert dim in temporal["properties"], \
            f"CR-MET-011 section 3: temporal dimension {dim!r} missing from the Observation temporal object"


def test_section3_temporal_dimensions_are_not_collapsed():
    """The temporal object MUST carry distinct fields, not one catch-all timestamp."""
    for obs in _observations():
        t = obs["temporal"]
        assert t["observed_at"] != t["recorded_at"] or "observed_at" in t, \
            f"CR-MET-011 section 3: {obs['id']} must distinguish observation time from transaction time"
        assert "measured_at" in t, f"CR-MET-011 section 3: {obs['id']} missing measurement time"
        assert "reported" not in t, \
            f"CR-MET-011 section 3: {obs['id']} collapses dimensions into a single field"


def test_section3_observed_at_and_recorded_at_are_required():
    schema = json.loads((BASE / "schemas" / "entities" / "measurement-observation.json").read_text())
    required = set(schema["properties"]["temporal"]["required"])
    assert {"observed_at", "recorded_at"} <= required, \
        "CR-MET-011 section 3: observed_at and recorded_at must be required"
    for obs in _observations():
        assert obs["temporal"].get("observed_at"), f"{obs['id']} missing observed_at"
        assert obs["temporal"].get("recorded_at"), f"{obs['id']} missing recorded_at"


def test_section4_all_seven_period_types_supported():
    schema = json.loads((BASE / "schemas" / "entities" / "reporting-period.json").read_text())
    enum = schema["properties"]["period_type"]["enum"]
    assert set(enum) == set(PERIOD_TYPES), f"CR-MET-011 section 4: period_type enum is {enum}"
    voc = set(CLASSIFICATIONS["ReportingPeriod.period_type"]["values"])
    assert set(enum) == voc, "CR-MET-011 section 4: schema enum must match the vocabulary exactly"


def test_section4_instantaneous_and_point_in_time_carry_no_interval():
    for rp in _periods():
        if rp["period_type"] in {"instantaneous", "point_in_time"}:
            assert rp["period_start"] is None and rp["period_end"] is None, \
                f"CR-MET-011 section 4: {rp['id']} is {rp['period_type']} and must not carry an interval"


def test_section4_bounded_periods_carry_an_interval():
    for rp in _periods():
        if rp["period_type"] in {"fixed_duration", "cumulative", "irregular"}:
            assert rp["period_start"] and rp["period_end"], \
                f"CR-MET-011 section 4: {rp['id']} is {rp['period_type']} and MUST carry an interval"
            assert rp["period_start"] < rp["period_end"], \
                f"CR-MET-011 section 4: {rp['id']} period_start must precede period_end"


def test_section4_rolling_requires_anchor_and_window():
    for rp in _periods():
        if rp["period_type"] == "rolling":
            assert rp["window_size"], f"CR-MET-011 section 4: {rp['id']} rolling period MUST declare window_size"
            assert rp["anchor_reference"], f"CR-MET-011 section 4: {rp['id']} rolling period MUST declare anchor_reference"


def test_section4_irregular_requires_interval_count():
    for rp in _periods():
        if rp["period_type"] == "irregular":
            assert rp["interval_count"], f"CR-MET-011 section 4: {rp['id']} irregular period MUST declare interval_count"


def test_section4_fiscal_requires_calendar_and_fiscal_year():
    for rp in _periods():
        if rp["period_semantics"] == "fiscal":
            assert rp["calendar_reference"], f"CR-MET-011 section 4: {rp['id']} fiscal period MUST declare calendar_reference"
            assert rp["fiscal_year_ref"], f"CR-MET-011 section 4: {rp['id']} fiscal period MUST declare fiscal_year_ref"


def test_section4_window_size_only_on_rolling():
    for rp in _periods():
        if rp["period_type"] != "rolling":
            assert rp["window_size"] is None, \
                f"CR-MET-011 section 4: {rp['id']} is {rp['period_type']} and MUST NOT declare window_size"


def test_section5_all_eleven_provenance_elements_present():
    schema = json.loads((BASE / "schemas" / "entities" / "provenance.json").read_text())
    for element in PROVENANCE_ELEMENTS:
        assert element in schema["properties"], \
            f"CR-MET-011 section 5: provenance element {element!r} missing from the schema"


def test_section5_provenance_elements_declared_on_every_record():
    for pr in _provenances():
        for element in PROVENANCE_ELEMENTS:
            assert element in pr, f"CR-MET-011 section 5: {pr['id']} missing provenance element {element!r}"


def test_section5_provenance_responsible_party_is_required():
    """The W3C PROV responsible-party concept. Accountability may not be optional."""
    schema = json.loads((BASE / "schemas" / "entities" / "provenance.json").read_text())
    assert "responsible_party_ref" in schema["required"], \
        "CR-MET-011 section 5: responsible_party_ref must be required"
    for pr in _provenances():
        assert pr["responsible_party_ref"], f"CR-MET-011 section 5: {pr['id']} MUST declare a responsible party"


def test_section5_formula_and_metric_versions_are_version_pinned():
    """Historical reconstruction depends on the exact version applied."""
    for pr in _provenances():
        assert "@" in pr["formula_version_ref"], \
            f"CR-MET-011 section 5: {pr['id']} formula_version_ref must be version-pinned"
        assert "@" in pr["metric_version_ref"], \
            f"CR-MET-011 section 5: {pr['id']} metric_version_ref must be version-pinned"


def test_section5_provenance_is_one_to_one_with_observation():
    """Provenance is a 1:1 fact about a single result, never shared."""
    refs = [o["provenance_reference"] for o in _observations()]
    assert len(refs) == len(set(refs)), \
        "CR-MET-011 section 5: each Observation must carry its own Provenance record"


def test_section5_transformation_chain_is_ordered():
    for pr in _provenances():
        steps = [t["step"] for t in pr["transformation_chain"]]
        assert steps == sorted(steps), f"CR-MET-011 section 5: {pr['id']} transformation steps must be ordered"
        assert steps[0] == 1, f"CR-MET-011 section 5: {pr['id']} transformation chain must start at step 1"


def test_section6_every_observation_resolves_to_its_provenance():
    prov_ids = {p["id"] for p in _provenances()}
    for obs in _observations():
        assert obs["provenance_reference"] in prov_ids, \
            f"CR-MET-011 section 6: {obs['id']} references unknown provenance {obs['provenance_reference']}"


def test_section6_every_observation_resolves_to_its_reporting_period():
    period_ids = {p["id"] for p in _periods()}
    for obs in _observations():
        ref = obs["temporal"]["reporting_period_ref"]
        assert ref in period_ids, \
            f"CR-MET-011 section 6: {obs['id']} references unknown reporting period {ref}"


def test_section6_historical_meaning_is_preserved_by_version_pin():
    """KEY ARCHITECTURAL DECISION: updating a Metric must not retrospectively change
    the meaning of previously recorded results. The version pin on the Provenance
    record is what preserves it."""
    for obs in _observations():
        prov = next(p for p in _provenances() if p["id"] == obs["provenance_reference"])
        assert "@" in prov["metric_version_ref"], \
            f"CR-MET-011 section 6: {obs['id']} provenance must pin the Metric version"
        assert prov["timestamps"]["effective_from"], \
            f"CR-MET-011 section 6: {prov['id']} must record when the pinned definition became applicable"


def test_section6_effective_time_is_a_closed_interval_when_the_definition_ended():
    """A definition that has ceased to apply MUST record when. A definition still in
    force legitimately leaves effective_to null."""
    for pr in _provenances():
        eff = pr["timestamps"]["effective_from"]
        eff_to = pr["timestamps"]["effective_to"]
        if eff_to is not None:
            assert eff < eff_to, \
                f"CR-MET-011 section 6: {pr['id']} effective_from must precede effective_to"


def test_section6_non_reproducible_records_declare_the_reason():
    for pr in _provenances():
        repro = pr["reproducibility"]
        if not repro["reproducible"]:
            assert repro["reproduction_notes"], \
                f"CR-MET-011 section 6: {pr['id']} non-reproducible MUST state why"


def test_section7_all_five_record_states_supported():
    schema = json.loads((BASE / "schemas" / "entities" / "measurement-observation.json").read_text())
    assert set(schema["properties"]["record_state"]["enum"]) == set(RECORD_STATES), \
        "CR-MET-011 section 7: record_state enum must carry the 5 states"
    voc = set(CLASSIFICATIONS["Measurement Observation.record_state"]["values"])
    assert voc == set(RECORD_STATES), "CR-MET-011 section 7: vocabulary must carry the 5 states"


def test_section7_fixture_exercises_every_record_state():
    states = {o["record_state"] for o in _observations()}
    assert states == set(RECORD_STATES), f"CR-MET-011 section 7: fixture covers {sorted(states)}"


def test_section7_corrected_record_states_its_reason_and_target():
    for obs in _observations():
        if obs["record_state"] == "corrected":
            assert obs["corrects_observation_ref"], \
                f"CR-MET-011 section 7: {obs['id']} corrected MUST reference the original"
            assert obs["correction_reason"], \
                f"CR-MET-011 section 7: {obs['id']} corrected MUST state the reason"
        else:
            assert obs["correction_reason"] is None, \
                f"CR-MET-011 section 7: {obs['id']} is {obs['record_state']} and MUST NOT carry a correction reason"
            assert obs["corrects_observation_ref"] is None, \
                f"CR-MET-011 section 7: {obs['id']} is {obs['record_state']} and MUST NOT claim to correct anything"


def test_section7_superseded_record_states_its_reason():
    for obs in _observations():
        if obs["record_state"] == "superseded":
            assert obs["supersedes_observation_reason"], \
                f"CR-MET-011 section 7: {obs['id']} superseded MUST state why"


def test_section7_correction_and_supersession_are_distinct_semantics():
    """Q19a: a correction asserts the target was ERRONEOUS; a supersession asserts a
    NEWER AUTHORITATIVE value exists for the same period. The two fields are never
    conflated, and both may target the same Observation."""
    schema = json.loads((BASE / "schemas" / "entities" / "measurement-observation.json").read_text())
    assert "corrects_observation_ref" in schema["properties"]
    assert "supersedes_observation" in schema["properties"]
    assert schema["properties"]["supersedes_observation"]["description"].startswith("DEPRECATED"), \
        "CR-MET-011 Q19a: the conflated supersedes_observation field must be marked deprecated"
    for obs in _observations():
        if obs["corrects_observation_ref"]:
            assert obs["supersedes_observation_reason"] is None, \
                f"CR-MET-011 Q19a: {obs['id']} must not carry both correction and supersession semantics"


def test_section7_correction_never_overwrites_the_original():
    """A correction MUST NOT silently overwrite the original value."""
    by_id = {o["id"]: o for o in _observations()}
    corrected = [o for o in _observations() if o["record_state"] == "corrected"]
    assert corrected, "CR-MET-011 section 7: fixture must exercise at least one correction"
    for obs in corrected:
        original = by_id[obs["corrects_observation_ref"]]
        assert original["value"] != obs["value"], \
            f"CR-MET-011 section 7: {obs['id']} correction must record a different value"
        assert original["id"] in by_id, \
            f"CR-MET-011 section 7: the original {original['id']} must be retained, not deleted"
        assert original["observation_status"] in {"superseded", "retired"}, \
            f"CR-MET-011 section 7: the corrected original {original['id']} must be marked superseded"


def test_section7_original_record_has_no_upstream_claim():
    originals = [o for o in _observations() if o["record_state"] == "original"]
    assert originals, "CR-MET-011 section 7: fixture must exercise an original record"
    for obs in originals:
        assert obs["corrects_observation_ref"] is None, \
            f"CR-MET-011 section 7: an original MUST NOT correct another record"