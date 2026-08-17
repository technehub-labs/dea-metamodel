"""CR-5 section 36: assessment conformance rules A001-A013 (metamodel-level subset).

Instance-level rules (A001/A002/A003/A006/A010/A013) are enforced by the JSON
schemas at validation time; this module enforces the metamodel-level guarantees.
"""
import json
import re

import yaml

from conftest import BASE

PROFILES = BASE / "metamodel" / "profiles"
ASSESSMENT = PROFILES / "assessment"
DMM = PROFILES / "dmm"

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _constraints():
    doc = yaml.safe_load((ASSESSMENT / "assessment-constraints.yaml").read_text())
    return {c["id"]: c for c in doc["constraints"]}


def _assessment_entity_ids():
    prof = yaml.safe_load((ASSESSMENT / "profile.yaml").read_text())["profile"]
    return set(prof["entities"])


def _assessment_schema_files():
    # derive schema paths from the normative artifacts block
    norm = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())
    files = set()
    for e in norm["entities"]:
        if e["id"] in _assessment_entity_ids():
            files.add(str(e["artifacts"]["json_schema"]).split("entities/")[1])
    return files


def test_a_rule_ids_complete():
    ids = set(_constraints())
    expected = {f"A{n:03d}" for n in range(1, 14)}
    assert ids == expected, f"missing A-rules: {expected - ids}"


def test_a_rules_have_text_and_enforcement():
    for cid, c in _constraints().items():
        assert len(c.get("rule", "")) >= 20, f"{cid}: rule text missing/trivial"
        assert c.get("enforcement"), f"{cid}: enforcement route not declared"


def test_a004_scores_use_declared_scale(entities):
    ids = {e["id"] for e in entities}
    assert "dea:Scale" in ids and "dea:Score" in ids
    score_schema = json.loads((BASE / "schemas" / "entities" / "score.json").read_text())
    assert "scale_ref" in score_schema["properties"], "A004: Score must reference a declared Scale"


def test_a005_maturity_levels_belong_to_model(entities):
    ids = {e["id"] for e in entities}
    assert {"dea:MaturityModel", "dea:MaturityLevel"} <= ids
    lvl = json.loads((BASE / "schemas" / "entities" / "maturity-level.json").read_text())
    assert "model_ref" in lvl["properties"], "A005: MaturityLevel must reference its MaturityModel"
    model = yaml.safe_load((DMM / "maturity.yaml").read_text())["maturity_model"]
    assert model["levels"], "A005: DMM maturity model declares no levels"
    for l in model["levels"]:
        assert l["kind"] == "dea:MaturityLevel", "A005: levels must live inside the MaturityModel document"


def test_a007_assessment_is_separate_profile_layer(entities):
    core_ids = set(yaml.safe_load((BASE / "metamodel" / "core" / "core.yaml").read_text())["ontology"]["entities"])
    overlap = core_ids & _assessment_entity_ids()
    assert not overlap, f"A007: assessment vocabulary leaked into Core: {overlap}"


def test_a008_no_intrinsic_maturity_or_score():
    # A008 targets assessment semantics smuggled onto architectural entities
    # (CR-5 §2: capability.maturity = 3 is the anti-pattern). A property that is a
    # registered controlled classification (E005/O008 — e.g. ArchitecturePattern.
    # maturity as emerging/canonical adoption status) is classification, not an
    # intrinsic assessment attribute, and is explicitly out of A008 scope.
    voc = yaml.safe_load((BASE / "metamodel" / "vocabularies" / "classifications.yaml").read_text())
    classified = {f"{c['entity']}.{c['property']}" for c in voc["classifications"].values()}
    assessment_schemas = _assessment_schema_files()
    offenders = []
    for p in sorted((BASE / "schemas" / "entities").glob("*.json")):
        if p.name in assessment_schemas or p.name == "entity.json":
            continue
        schema = json.loads(p.read_text())
        ent = schema.get("title")
        for prop in schema.get("properties", {}):
            looks_intrinsic = prop == "score" or prop.startswith("maturity") or prop.startswith("target_maturity")
            if looks_intrinsic and f"{ent}.{prop}" not in classified:
                offenders.append(f"{p.name}:{prop}")
    assert not offenders, f"A008: intrinsic maturity/score on architectural entities: {offenders}"


def test_a009_aggregation_rules_declared(entities):
    ids = {e["id"] for e in entities}
    assert "dea:AggregationRule" in ids, "A009: AggregationRule entity missing"
    scoring = yaml.safe_load((DMM / "scoring.yaml").read_text())
    kinds = scoring["supported_rule_kinds"]["aggregation"]
    assert kinds and "weighted-average" in kinds, "A009: DMM profile must declare aggregation rule kinds"


def test_a011_benchmarks_are_not_results(entities, relationships):
    ids = {e["id"] for e in entities}
    assert {"dea:Benchmark", "dea:BenchmarkReference"} <= ids
    # benchmarks must not be attainable/producible as results: no relationship
    # may target a Benchmark type except derives-from feeding BenchmarkReference
    for r in relationships:
        for t in r["target"]["types"]:
            if t in ("dea:Benchmark", "dea:BenchmarkPopulation", "dea:BenchmarkReference"):
                assert r["id"] in ("dea:derives-from", "dea:benchmarked-against"), \
                    f"A011: {r['id']} treats a benchmark as a result-like target"


def test_a012_framework_versioned_independently(canonical_version):
    dmm = yaml.safe_load((DMM / "dmm.yaml").read_text())["framework"]
    v = dmm["framework_version"]
    assert SEMVER.match(v), f"A012: DMM framework_version {v!r} not semver"
    assert v != canonical_version, "A012: framework version must be governed independently of the metamodel"


def test_assessment_entities_membership(entities):
    for e in entities:
        if e["id"] in _assessment_entity_ids():
            m = e.get("membership", {})
            assert m.get("kind") == "profile" and m.get("profile") == "dea:assessment", \
                f"{e['id']}: membership must be profile/dea:assessment"


def test_dmm_mappings_resolve(entities):
    ids = {e["id"] for e in entities}
    mappings = yaml.safe_load((DMM / "mappings.yaml").read_text())["mappings"]
    dims = {d["id"] for d in yaml.safe_load((DMM / "dimensions.yaml").read_text())["dimensions"]}
    assert {m["dimension"] for m in mappings} == dims, "every DMM dimension must be mapped"
    for m in mappings:
        for t in m["assesses"]:
            assert t in ids, f"mapping {m['dimension']} -> {t}: not a registered entity"


def test_dmm_profile_defines_no_entities():
    prof = yaml.safe_load((DMM / "profile.yaml").read_text())["profile"]
    assert prof["entities"] == [], "DMM profile reuses dea:assessment vocabulary; it defines no entity types (CR-5 §32)"
