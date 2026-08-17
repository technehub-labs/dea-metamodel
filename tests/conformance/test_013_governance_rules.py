"""CR-7 section 62: governance & agentic conformance rules G001-G016
(metamodel-level subset)."""
import json

import yaml

from conftest import BASE

PROFILES = BASE / "metamodel" / "profiles"
GOV = PROFILES / "governance"
AGT = PROFILES / "agentic"


def _constraints():
    doc = yaml.safe_load((GOV / "constraints.yaml").read_text())
    return {c["id"]: c for c in doc["constraints"]}


def _rels(relationships):
    return {r["id"]: r for r in relationships}


def _schema(name):
    return json.loads((BASE / "schemas" / "entities" / name).read_text())


def _profile_entities(path):
    prof = yaml.safe_load((path / "profile.yaml").read_text())["profile"]
    return set(prof["entities"])


def test_g_rule_ids_complete():
    ids = set(_constraints())
    expected = {f"G{n:03d}" for n in range(1, 17)}
    assert ids == expected, f"missing G-rules: {expected - ids}"


def test_g_rules_have_text_and_enforcement():
    for cid, c in _constraints().items():
        assert len(c.get("rule", "")) >= 20, f"{cid}: rule text missing/trivial"
        assert c.get("enforcement"), f"{cid}: enforcement route not declared"


def test_g001_decision_authority(relationships):
    rels = _rels(relationships)
    assert "authority_ref" in _schema("decision.json")["properties"], "G001: Decision needs authority_ref"
    assert "dea:Agent" in rels["dea:makes"]["source"]["types"], "G001/§65: agents make decisions via dea:makes"
    assert "dea:Decision" in rels["dea:authorized-by"]["source"]["types"]


def test_g002_decision_evidence(relationships):
    rels = _rels(relationships)
    ib = rels["dea:informed-by"]
    assert "dea:Decision" in ib["source"]["types"] and "dea:Evidence" in ib["target"]["types"]
    assert "rationale" in _schema("decision.json")["properties"], "G002: Decision needs rationale"


def test_g003_decision_change_separation(entities, relationships):
    ids = {e["id"] for e in entities}
    assert "dea:Decision" in ids and "dea:Change" in ids
    auth = _rels(relationships)["dea:authorizes"]
    assert "dea:Decision" in auth["source"]["types"] and "dea:Change" in auth["target"]["types"], \
        "G003: Decision authorizes Change — they must not be conflated"


def test_g004_policy_applicability():
    assert "applicability" in _schema("policy.json")["properties"], "G004: Policy needs applicability"


def test_g005_delegation_scope_and_validity():
    props = _schema("delegation.json")["properties"]
    for f in ("scope", "valid_from", "valid_to", "delegator_ref", "delegate_ref", "authority_ref"):
        assert f in props, f"G005: Delegation missing {f}"


def test_g006_agent_authority(relationships):
    ab = _rels(relationships)["dea:authorized-by"]
    assert "dea:Agent" in ab["source"]["types"]
    assert {"dea:Authority", "dea:Delegation"} <= set(ab["target"]["types"])


def test_g007_agent_ownership(relationships):
    owns = _rels(relationships)["dea:owns"]
    assert "dea:Agent" in owns["target"]["types"], "G007: agents must be ownable"
    assert "owner_ref" in _schema("agent.json")["properties"]


def test_g008_agent_policy(relationships):
    cb = _rels(relationships)["dea:constrained-by"]
    assert "dea:Agent" in cb["source"]["types"]
    assert "dea:Policy" in cb["target"]["types"], "G008: agents must reference governance policies"


def test_g009_tool_permission(entities, relationships):
    ids = {e["id"] for e in entities}
    assert "dea:ToolPermission" in ids
    perms = _rels(relationships)["dea:permits"]
    assert "dea:ToolPermission" in perms["source"]["types"] and "dea:Tool" in perms["target"]["types"]


def test_g010_autonomous_action_within_authority(relationships):
    ab = _rels(relationships)["dea:authorized-by"]
    assert "dea:Action" in ab["source"]["types"], "G010: autonomous actions must be within delegated authority"


def test_g011_escalation(entities, relationships):
    ids = {e["id"] for e in entities}
    assert "dea:Escalation" in ids
    esc = _rels(relationships)["dea:escalates-to"]
    assert {"dea:Action", "dea:Agent"} <= set(esc["source"]["types"])


def test_g012_risk_controls(entities, relationships):
    ids = {e["id"] for e in entities}
    assert {"dea:Risk", "dea:Control"} <= ids
    mit = _rels(relationships)["dea:mitigates"]
    assert "dea:Control" in mit["source"]["types"] and "dea:Risk" in mit["target"]["types"]
    assert "materiality" in _schema("action.json")["properties"], "G012/§41: materiality drives control strictness"


def test_g013_agent_lifecycle():
    agent_doc = yaml.safe_load((AGT / "agent.yaml").read_text())
    states = agent_doc["lifecycle"]["states"]
    assert {"designed", "approved", "active", "retired"} <= set(states), \
        "G013/§53: agent lifecycle must be declared (reusing CR-6)"


def test_g014_skill_validity(relationships):
    rels = _rels(relationships)
    assert "dea:Agent" in rels["dea:has-skill"]["source"]["types"]
    assert "dea:AgentSkill" in rels["dea:permits"]["target"]["types"], \
        "G014: skill invocation bounded by permits/prohibits"


def test_g015_scenario_isolation_applies_to_agents(relationships):
    contains = _rels(relationships)["dea:contains"]
    assert "dea:Scenario" in contains["source"]["types"], \
        "G015: hypothetical agents live inside scenario containment (CR-6 T007)"


def test_g016_accountability(relationships):
    af = _rels(relationships)["dea:accountable-for"]
    assert {"dea:Decision", "dea:Action"} <= set(af["target"]["types"]), \
        "G016: material automated decisions need an accountable party"


def test_cr7_profiles_structure(entities):
    ids = {e["id"]: e for e in entities}
    for path, pid in ((GOV, "dea:governance"), (AGT, "dea:agentic")):
        for eid in _profile_entities(path):
            m = ids[eid].get("membership", {})
            assert m.get("kind") == "profile" and m.get("profile") == pid, \
                f"{eid}: membership must be profile/{pid}"
            assert ids[eid].get("dimension") == "ai-automation-governance"


def test_agentic_profile_dependencies():
    prof = yaml.safe_load((AGT / "profile.yaml").read_text())["profile"]
    deps = prof["depends_on"]
    assert {"dea:core", "dea:governance", "dea:assessment", "dea:lifecycle"} <= set(deps)


def test_agent_reuses_core_semantics(relationships):
    # §65: no AgentDecision/AgentAction/AgentOutcome duplicates
    rels = _rels(relationships)
    assert "dea:Agent" in rels["dea:makes"]["source"]["types"], "Agent Decision = Decision + made-by Agent"
    assert "dea:Agent" in rels["dea:performed-by"]["target"]["types"], "Agent Action = Action + performed-by Agent"
    assert "dea:AgenticSystem" in rels["dea:results-in"]["source"]["types"], "Agent Outcome = Outcome + results-in AgenticSystem"


def test_agent_specializes_actor(entities, relationships):
    spec = _rels(relationships)["dea:specializes"]
    assert "dea:Agent" in spec["source"]["types"] and "dea:Actor" in spec["target"]["types"], \
        "§27: Agent is an enterprise Actor"
    ids = {e["id"] for e in entities}
    assert "dea:AgentDecision" not in ids and "dea:AgentAction" not in ids and "dea:AgentKnowledge" not in ids, \
        "§26/§65: agent-specific duplicates of core concepts are forbidden"


def test_constraint_strength():
    props = _schema("constraint.json")["properties"]
    assert props.get("strength", {}).get("enum") == ["hard", "soft", "preference", "guideline"], \
        "§10: constraint strength must be explicit"


def test_decision_confidence_and_uncertainty():
    props = _schema("decision.json")["properties"]
    assert "confidence" in props and "uncertainty" in props and "assumptions" in props, \
        "§17: decisions carry confidence, uncertainty and assumptions"
