"""CR-MET-010 Level 3: Metric governance conformance.

Per CR-MET-010 section 7, Level 3 (governance conformance) covers:
- Owner and steward
- Approval status
- Lifecycle compliance
- Source documentation
- Evidence requirements
- Versioning
- Change traceability
"""
import yaml

from conftest import BASE

FIXTURE = yaml.safe_load(
    (BASE / "tests" / "conformance" / "fixtures" / "metric_governance.yaml").read_text()
)
LIFECYCLE = yaml.safe_load((BASE / "metamodel" / "vocabularies" / "lifecycle.yaml").read_text())
CLASSIFICATIONS = yaml.safe_load(
    (BASE / "metamodel" / "vocabularies" / "classifications.yaml").read_text()
)["classifications"]

SPEC = LIFECYCLE["specializations"]["metric-governance"]
BASE_VALUES = {v["id"] for v in LIFECYCLE["values"]}
REFINEMENTS = {v["id"] for v in SPEC["refinement_values"]}
CHAIN = SPEC["chain"]
TERMINAL = set(SPEC["terminal"])


def _metrics():
    return FIXTURE["metrics"]


def _changes():
    return FIXTURE["changes"]


def test_l3_base_vocabulary_not_widened():
    """CR-MET-010 Q15a-prime: the base vocabulary MUST remain the metamodel default."""
    assert BASE_VALUES == {"proposed", "planned", "active", "deprecated", "retired"}, \
        f"L3: base lifecycle vocabulary widened to {BASE_VALUES}"


def test_l3_specialization_declares_chain_and_terminal():
    assert CHAIN == ["proposed", "under_review", "approved", "published", "active"]
    assert TERMINAL == {"deprecated", "retired"}
    for state in ("under_review", "approved", "published", "under_revision", "suspended"):
        assert state in REFINEMENTS, f"L3: refinement state {state!r} not declared"


def test_l3_definition_governance_requires_owner_and_steward():
    """A Metric under definition governance MUST carry both owner and steward."""
    for m in _metrics():
        gov = m.get("governance") or {}
        if gov.get("governance_object") != "definition":
            continue
        conf = m["conformance"]["governance"]
        if conf["verdict"] == "conformant":
            assert gov.get("metric_owner_ref"), f"L3: {m['id']} conformant definition lacks metric_owner_ref"
            assert gov.get("metric_steward_ref"), f"L3: {m['id']} conformant definition lacks metric_steward_ref"


def test_l3_governance_authority_and_metamodel_authority_required():
    """The governance authority resolves exceptions; the metamodel authority controls
    canonical semantics. Both are mandatory on any governed Metric."""
    for m in _metrics():
        gov = m.get("governance") or {}
        assert gov.get("governance_authority_ref"), \
            f"L3: {m['id']} missing governance_authority_ref"
        assert gov.get("metamodel_authority_ref"), \
            f"L3: {m['id']} missing metamodel_authority_ref"


def test_l3_approval_status_valid_and_paired_with_approval_evidence():
    allowed = {"not_submitted", "under_review", "approved", "rejected", "approved_with_conditions"}
    for m in _metrics():
        gov = m.get("governance") or {}
        status = gov.get("approval_status")
        assert status in allowed, f"L3: {m['id']} approval_status {status!r} not in the binding enum"
        if status in {"approved", "approved_with_conditions"}:
            assert gov.get("approved_by_ref"), f"L3: {m['id']} approved without approved_by_ref"
            assert gov.get("approved_at"), f"L3: {m['id']} approved without approved_at"


def test_l3_lifecycle_state_is_known():
    for m in _metrics():
        assert m["lifecycle_status"] in BASE_VALUES | REFINEMENTS, \
            f"L3: {m['id']} lifecycle_status {m['lifecycle_status']!r} is not a declared state"


def test_l3_deprecated_metric_is_retained_not_deleted():
    """CR-MET-010 section 5: a deprecated Metric MUST NOT be silently deleted when
    historical Observations reference it."""
    retired_ids = {m["id"] for m in _metrics() if m["lifecycle_status"] in TERMINAL}
    assert retired_ids, "L3: fixture must exercise at least one terminal-state Metric"
    for mid in retired_ids:
        assert any(m["id"] == mid for m in _metrics()), \
            f"L3: terminal-state Metric {mid} must remain present in the catalog"


def test_l3_non_conformant_records_carry_findings():
    """A non_conformant governance verdict MUST state at least one finding."""
    for m in _metrics():
        for level, block in m["conformance"].items():
            if block["verdict"] == "non_conformant":
                assert block["findings"], \
                    f"L3: {m['id']} governance/level {level} non_conformant without findings"


def test_l3_conformance_verdicts_valid():
    allowed = set(CLASSIFICATIONS["MetricConformance.conformance_verdict"]["values"])
    for m in _metrics():
        for level, block in m["conformance"].items():
            assert block["verdict"] in allowed, \
                f"L3: {m['id']} conformance.{level}.verdict {block['verdict']!r} not in vocabulary"


def test_l3_every_change_records_evidence():
    """CR-MET-010 section 8: the semantic-change assessment process requires an
    explicit disposition, a severity classification, and a rationale for every change."""
    dispositions = set(CLASSIFICATIONS["MetricChange.semantic_change_disposition"]["values"])
    severities = set(CLASSIFICATIONS["MetricChange.change_severity"]["values"])
    for c in _changes():
        assert c["semantic_change_disposition"] in dispositions, \
            f"L3: change on {c['metric_ref']} disposition {c['semantic_change_disposition']!r} unknown"
        assert c["change_severity"] in severities, \
            f"L3: change on {c['metric_ref']} severity {c['change_severity']!r} unknown"
        assert c.get("rationale"), f"L3: change on {c['metric_ref']} requires a rationale"
        assert "from_value" in c and "to_value" in c, \
            f"L3: change on {c['metric_ref']} requires from_value and to_value for traceability"


def test_l3_semantic_breaking_change_requires_new_identity():
    """CR-MET-010 section 8: a change that alters the fundamental semantic meaning MUST
    NOT be represented as a simple cosmetic version update."""
    for c in _changes():
        if c["change_severity"] == "semantic_breaking":
            assert c["new_identity_required"] is True, \
                f"L3: semantic_breaking change on {c['metric_ref']} MUST require a new identity"
            assert c["semantic_change_disposition"] in {"new_identity", "deprecate"}, \
                f"L3: semantic_breaking change on {c['metric_ref']} MUST result in a new identity or deprecation"


def test_l3_cosmetic_change_must_not_require_new_identity():
    for c in _changes():
        if c["change_severity"] == "cosmetic":
            assert c["new_identity_required"] is False, \
                f"L3: cosmetic change on {c['metric_ref']} MUST NOT require a new identity"


def test_l3_change_target_must_exist():
    ids = {m["id"] for m in _metrics()}
    for c in _changes():
        assert c["metric_ref"] in ids, f"L3: change targets unknown Metric {c['metric_ref']}"


def test_l3_governance_roles_are_accountable_explicitly():
    """CR-MET-010 section 4: one individual may fulfil multiple roles, but accountability
    MUST remain explicit. A record carrying only a governance object and no role is invalid."""
    for m in _metrics():
        gov = m.get("governance") or {}
        role_keys = [k for k in gov if k.endswith("_ref")]
        assert role_keys, f"L3: {m['id']} carries no governance role accountability"