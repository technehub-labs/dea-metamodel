"""CR-6 section 36: temporal integrity rules T001-T010 (metamodel-level subset).

Instance-level rules (interval ordering, contradictory states, supersession
consistency, cycle detection) are enforced at validation time; this module
enforces the metamodel-level guarantees.
"""
import json
import re

import yaml

from conftest import BASE

PROFILES = BASE / "metamodel" / "profiles"
LIFECYCLE = PROFILES / "lifecycle"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _constraints():
    doc = yaml.safe_load((LIFECYCLE / "constraints.yaml").read_text())
    return {c["id"]: c for c in doc["constraints"]}


def _lifecycle_entity_ids():
    prof = yaml.safe_load((LIFECYCLE / "profile.yaml").read_text())["profile"]
    return set(prof["entities"])


def _schema(name):
    return json.loads((BASE / "schemas" / "entities" / name).read_text())


def test_t_rule_ids_complete():
    ids = set(_constraints())
    expected = {f"T{n:03d}" for n in range(1, 11)}
    assert ids == expected, f"missing T-rules: {expected - ids}"


def test_t_rules_have_text_and_enforcement():
    for cid, c in _constraints().items():
        assert len(c.get("rule", "")) >= 20, f"{cid}: rule text missing/trivial"
        assert c.get("enforcement"), f"{cid}: enforcement route not declared"


def test_t001_interval_schema_declares_bounds():
    s = _schema("temporal-interval.json")["properties"]
    assert "valid_from" in s and "valid_to" in s, "T001: TemporalInterval must declare valid_from/valid_to"


def test_t002_reactivation_transition_declared():
    lc = yaml.safe_load((LIFECYCLE / "lifecycle.yaml").read_text())
    reactivations = [t for t in lc["transitions"]["generic"] if t.get("kind") == "reactivation"]
    assert reactivations, "T002: no reactivation transition declared (retired -> active would be impossible)"
    lt = _schema("lifecycle-transition.json")["properties"]
    assert "reactivation" in lt, "T002: LifecycleTransition must carry the reactivation flag"


def test_t003_current_state_excludes_future():
    st = yaml.safe_load((LIFECYCLE / "states.yaml").read_text())
    excludes = set(st["states"]["current"]["excludes"])
    assert {"proposed", "planned", "target", "scenario"} <= excludes, \
        "T003: current state must exclude planned/proposed/target/scenario elements"


def test_t004_relationship_instances_are_temporal():
    ri = json.loads((BASE / "schemas" / "relationships" / "relationship-instance.json").read_text())
    props = ri["properties"]
    assert "valid_from" in props and "valid_to" in props, "T004: relationship instances need temporal bounds"
    assert "status" in props, "CR-6 §22: relationship instances need lifecycle status"


def test_t005_in_state_relationship_exists(relationships):
    rel = next(r for r in relationships if r["id"] == "dea:in-state")
    assert rel["temporal"] is True, "T005/§17: in-state must be temporal so history is preserved"
    assert "dea:LifecycleState" in rel["target"]["types"]


def test_t006_current_and_target_are_distinct(entities):
    ids = {e["id"] for e in entities}
    assert "dea:CurrentState" in ids and "dea:TargetState" in ids
    st = yaml.safe_load((LIFECYCLE / "states.yaml").read_text())
    assert st["states"]["target"]["entity"] == "dea:TargetState"
    assert "Target ≠ Current" in st["states"]["target"]["rule"] or "Target ≠" in st["states"]["target"]["rule"]


def test_t007_scenario_isolation(relationships):
    contains = next(r for r in relationships if r["id"] == "dea:contains")
    assert "dea:Scenario" in contains["source"]["types"], "T007: scenarios contain their elements"
    st = yaml.safe_load((LIFECYCLE / "states.yaml").read_text())
    assert "never enter CurrentState" in st["states"]["scenario"]["rule"]


def test_t008_version_ordering_acyclic(relationships):
    prec = next(r for r in relationships if r["id"] == "dea:precedes")
    assert prec["source"]["types"] == ["dea:Version"] and prec["target"]["types"] == ["dea:Version"]
    assert prec["symmetric"] is False and prec["transitive"] is False
    assert "acyclic" in _constraints()["T008"]["rule"]


def test_t009_version_distinct_from_supersession(relationships):
    by_id = {r["id"] for r in relationships}
    assert {"dea:version-of", "dea:supersedes", "dea:precedes"} <= by_id, \
        "T009/§20: version-of and superseded-by must remain distinct relationships"


def test_t010_snapshot_revision_semantics():
    s = _schema("architecture-snapshot.json")["properties"]
    assert "approved" in s and "revision_of" in s, \
        "T010: snapshots need approved flag + explicit revision semantics"


def test_lifecycle_entities_membership(entities):
    for e in entities:
        if e["id"] in _lifecycle_entity_ids():
            m = e.get("membership", {})
            assert m.get("kind") == "profile" and m.get("profile") == "dea:lifecycle", \
                f"{e['id']}: membership must be profile/dea:lifecycle"


def test_lifecycle_dimension_registered(normative):
    dims = {d["id"] for d in normative["dimensions"]}
    assert "temporal-dimension" in dims
    for e in normative["entities"]:
        if e["id"] in _lifecycle_entity_ids() and not e.get("abstract"):
            assert e.get("dimension") == "temporal-dimension", \
                f"{e['id']}: lifecycle entities live in the temporal-dimension overlay"


def test_lifecycle_profile_dependencies():
    prof = yaml.safe_load((LIFECYCLE / "profile.yaml").read_text())["profile"]
    deps = prof["depends_on"]
    assert "dea:core" in deps and "dea:assessment" in deps, \
        "lifecycle profile depends on core + assessment (CR-6 §39 integration)"


def test_assessment_can_reference_states(entities, relationships):
    # CR-6 §39: AssessmentResult -> ArchitectureState via dea:assesses (target dea:Entity covers it)
    ids = {e["id"] for e in entities}
    assert "dea:ArchitectureState" in ids
    assesses = next(r for r in relationships if r["id"] == "dea:assesses")
    assert "dea:Entity" in assesses["target"]["types"], \
        "assesses must target dea:Entity so results can anchor to architecture states"


def test_change_semantics_wired(relationships):
    # CR-6 §15/§34: Change introduces/removes/modifies/replaces, realizes target state, depends on Change
    rels = {r["id"]: r for r in relationships}
    for rid in ("dea:introduces", "dea:removes", "dea:modifies"):
        assert "dea:Change" in rels[rid]["source"]["types"], f"{rid}: Change must be a source"
    assert "dea:Change" in rels["dea:replaces"]["source"]["types"]
    assert "dea:ArchitectureState" in rels["dea:realizes"]["target"]["types"], "Change realizes TargetState (§15)"
    assert "dea:Change" in rels["dea:depends-on"]["source"]["types"]
    assert "dea:Change" in rels["dea:depends-on"]["target"]["types"], "Change depends on Change (§34)"
    assert "dea:Change" in rels["dea:enables"]["target"]["types"], "Change enables Change (§34)"
