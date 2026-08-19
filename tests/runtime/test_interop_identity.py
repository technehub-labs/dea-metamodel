"""CR-11 Phase 2 — identity reconciliation, conflicts and authority tests."""

import pytest

from runtime.interoperability import (ExternalIdentifier, ExternalSystem,
                                      InteropError, InteropRegistry)
from runtime.interoperability.identity import (AuthorityPolicy, ConflictStatus,
                                               ConflictValue, EntityResolution,
                                               ReconciliationState,
                                               ResolutionCandidate, TieBreaker)


@pytest.fixture()
def registry():
    reg = InteropRegistry()
    reg.register_system(ExternalSystem(
        id="system.servicenow", name="ServiceNow CMDB", type="CMDB"))
    reg.register_system(ExternalSystem(
        id="system.leanix", name="LeanIX", type="EA_REPOSITORY"))
    return reg


def test_exact_external_identifier_resolution(registry):
    """CR-11I/J: exact external-id correlation resolves without review."""
    registry.link_external_identifier(ExternalIdentifier(
        system="system.servicenow", identifier="CI-001234",
        entity="app.customer-platform"))

    resolution = registry.reconcile_external(
        "system.servicenow", "CI-001234")

    assert resolution.state == ReconciliationState.MATCHED
    assert resolution.entity == "app.customer-platform"
    assert resolution.score == 1.0
    assert resolution.method == "exact"
    assert resolution.review_required is False


def test_semantic_candidate_requires_review(registry):
    """CR-11K: below auto-match threshold, uncertain identity is queued."""
    resolution = registry.reconcile_external(
        "system.servicenow", "CI-009999",
        candidates=[ResolutionCandidate(
            entity="app.customer-platform", score=0.82,
            method="semantic+identifier", evidence=["name similarity"])])

    assert resolution.state == ReconciliationState.CANDIDATE
    assert resolution.entity is None
    assert resolution.review_required is True
    assert resolution.candidates[0].score == 0.82


def test_high_confidence_candidate_matches_without_merge(registry):
    """CR-11K: one clear candidate matches; external id stays external."""
    resolution = registry.reconcile_external(
        "system.leanix", "FS-987",
        candidates=[ResolutionCandidate(
            entity="app.customer-platform", score=0.97,
            method="semantic+identifier")])

    assert resolution.state == ReconciliationState.MATCHED
    assert resolution.entity == "app.customer-platform"
    assert resolution.identifier == "FS-987"
    assert resolution.review_required is False


def test_multiple_high_confidence_candidates_conflict(registry):
    """CR-11K/L: mutually exclusive high-confidence candidates never auto-resolve."""
    resolution = registry.reconcile_external(
        "system.servicenow", "CI-CONFLICT",
        candidates=[
            ResolutionCandidate(entity="app.one", score=0.98),
            ResolutionCandidate(entity="app.two", score=0.96),
        ])

    assert resolution.state == ReconciliationState.CONFLICTING
    assert resolution.entity is None
    assert resolution.review_required is True


def test_low_confidence_candidate_is_unmatched(registry):
    resolution = registry.reconcile_external(
        "system.servicenow", "CI-UNKNOWN",
        candidates=[ResolutionCandidate(entity="app.maybe", score=0.42)])

    assert resolution.state == ReconciliationState.UNMATCHED
    assert resolution.entity is None
    assert resolution.review_required is True


def test_source_disagreement_is_preserved_as_conflict(registry):
    """CR-11L: conflicting values are first-class knowledge, not log lines."""
    conflict = registry.record_conflict(
        "app.customer-platform", "lifecycle.state",
        [
            ConflictValue(source="system.servicenow", value="RETIRED",
                          observed_at="2026-08-19T00:00:00Z", confidence=0.99),
            ConflictValue(source="system.leanix", value="active",
                          observed_at="2026-08-18T00:00:00Z", confidence=0.75),
        ])

    assert conflict.status == ConflictStatus.OPEN
    assert conflict.entity == "app.customer-platform"
    assert conflict.property == "lifecycle.state"
    assert [(v.source, v.value) for v in conflict.values] == [
        ("system.servicenow", "RETIRED"),
        ("system.leanix", "active"),
    ]
    assert conflict.resolution is None


def test_agreeing_sources_do_not_create_conflict(registry):
    conflict = registry.record_conflict(
        "app.customer-platform", "vendor",
        [ConflictValue(source="system.servicenow", value="legacy-vendor"),
         ConflictValue(source="system.leanix", value="legacy-vendor")])
    assert conflict is None


def _authority_policy():
    return AuthorityPolicy(
        id="policy.application-authority",
        scope="ApplicationComponent",
        weights={
            ("system.servicenow", "lifecycle.state"): 0.95,
            ("system.leanix", "lifecycle.state"): 0.60,
            ("system.leanix", "classification"): 0.90,
        },
        tie_breaker=TieBreaker.HIGHEST,
        owner="ea-governance")


def test_authority_is_property_specific():
    """CR-11M: source authority varies by property, never global."""
    policy = _authority_policy()

    assert policy.weight_for("system.servicenow", "lifecycle.state") == 0.95
    assert policy.weight_for("system.leanix", "lifecycle.state") == 0.60
    assert policy.weight_for("system.leanix", "classification") == 0.90
    assert policy.weight_for("system.servicenow", "classification") == 0.0


def test_authority_policy_resolves_conflict_but_preserves_losing_value(registry):
    """CR-11L/M/N: authority chooses a value; the disagreement remains recorded."""
    policy = registry.register_authority_policy(_authority_policy())
    conflict = registry.record_conflict(
        "app.customer-platform", "lifecycle.state",
        [ConflictValue(source="system.servicenow", value="RETIRED",
                       observed_at="2026-08-19T00:00:00Z"),
         ConflictValue(source="system.leanix", value="active",
                       observed_at="2026-08-18T00:00:00Z")])

    resolved = registry.resolve_conflict(
        conflict.id, policy.id, resolved_by="ea-governance")

    assert resolved.status == ConflictStatus.RESOLVED
    assert resolved.resolution["value"] == "RETIRED"
    assert resolved.resolution["source"] == "system.servicenow"
    assert resolved.resolution["policy"] == policy.id
    assert len(resolved.values) == 2  # losing value preserved


def test_undeclared_authority_refuses_to_choose(registry):
    """CR-11R: undefined authority is a correctness failure, not a guess."""
    policy = registry.register_authority_policy(_authority_policy())
    values = [ConflictValue(source="system.servicenow", value="team-a"),
              ConflictValue(source="system.leanix", value="team-b")]

    with pytest.raises(InteropError, match="no authority"):
        policy.authoritative_value("ownership.owner", values)


def test_merged_resolution_requires_explicit_approval():
    """CR-11L: never silently merge uncertain identities."""
    with pytest.raises(InteropError, match="MERGED"):
        EntityResolution(
            id="resolution.bad", system="system.servicenow",
            identifier="CI-BAD", state=ReconciliationState.MERGED,
            entity="app.customer-platform")


def test_phase2_identity_symbols_are_exported():
    from runtime.interoperability import (AuthorityPolicy as ExportedPolicy,
                                          EntityResolution as ExportedResolution,
                                          KnowledgeConflict as ExportedConflict)
    assert ExportedPolicy is AuthorityPolicy
    assert ExportedResolution is EntityResolution
    assert ExportedConflict.__name__ == "KnowledgeConflict"


def test_approve_candidate_links_identifier_without_adopting_it(registry):
    """Human approval converts a candidate into an auditable merge + external link."""
    resolution = registry.reconcile_external(
        "system.servicenow", "CI-009999",
        candidates=[ResolutionCandidate(
            entity="app.customer-platform", score=0.82,
            method="semantic+identifier")])

    merged = registry.approve_resolution(
        resolution.id, entity="app.customer-platform",
        approved_by="ea-governance")

    assert merged.state == ReconciliationState.MERGED
    assert merged.approved_by == "ea-governance"
    assert merged.review_required is False
    assert registry.resolve("system.servicenow", "CI-009999") == "app.customer-platform"
