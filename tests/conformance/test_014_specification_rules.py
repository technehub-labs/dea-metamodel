"""CR-8: specification conformance — inventory coverage, naming rules, quality gates
(§66), golden/negative model contract (§32-§33), and generated-artifact freshness."""
import json
import re
import subprocess
import sys

import yaml

from conftest import BASE

SPEC = BASE / "specification"
VALIDATOR = BASE / "tools" / "opendea_validate.py"

EXPECTED_INVALID = {
    "missing-id.yaml": "DEA-E004",
    "invalid-type.yaml": "DEA-E001",
    "invalid-relationship.yaml": "DEA-E002",
    "invalid-endpoint.yaml": "DEA-E006",
    "cardinality-error.yaml": "DEA-E003",
    "unauthorized-agent.yaml": "DEA-E009",
    "missing-owner.yaml": "DEA-E008",
    "invalid-lifecycle.yaml": "DEA-E004",
}


def _run_validator(path):
    r = subprocess.run([sys.executable, str(VALIDATOR), str(path), "--json"],
                       capture_output=True, text=True, cwd=BASE)
    return r.returncode, json.loads(r.stdout)


def test_inventory_covers_every_concept(entities, relationships):
    inv = yaml.safe_load((SPEC / "semantic-inventory.yaml").read_text())
    inv_e = {e["id"] for e in inv["entities"]}
    inv_r = {r["id"] for r in inv["relationships"]}
    assert inv_e == {e["id"] for e in entities}, "inventory out of sync — regenerate (generate_specification.py)"
    assert inv_r == {r["id"] for r in relationships}
    assert inv["counts"]["entities"] == len(entities)


def test_vocabulary_has_one_canonical_definition_per_concept(entities):
    voc = yaml.safe_load((SPEC / "vocabulary.yaml").read_text())
    ids = [c["id"] for c in voc["concepts"]]
    assert len(ids) == len(set(ids)), "CR-8 §5: duplicate canonical concepts"
    for c in voc["concepts"]:
        assert len(c.get("definition", "")) >= 30, f"§5: {c['id']} missing canonical definition"


def test_naming_conventions(entities, relationships):
    for e in entities:
        local = e["id"].split(":", 1)[1]
        assert re.match(r"^[A-Z][A-Za-z0-9]*$", local), f"§6: class name not PascalCase: {e['id']}"
    for r in relationships:
        local = r["id"].split(":", 1)[1]
        assert re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", local), f"§6: relationship id not kebab-case: {r['id']}"


def test_no_duplicate_canonical_names(entities):
    names = [e["name"] for e in entities]
    dupes = {n for n in names if names.count(n) > 1}
    assert not dupes, f"CR-8.2: duplicate canonical names: {dupes}"


def test_abstracts_are_not_instantiable_in_golden_models():
    # §9 guard: golden models never instantiate abstract anchors
    abstracts = {"Entity", "ArchitectureElement", "Behavior", "Service", "Information",
                 "Organization", "TemporalEvent", "TemporalState"}
    for f in sorted((BASE / "models" / "golden").glob("*.yaml")):
        doc = yaml.safe_load(f.read_text())
        for el in doc["elements"]:
            assert el["type"] not in abstracts, f"{f.name}: instantiates abstract {el['type']}"


def test_golden_models_pass():
    goldens = sorted((BASE / "models" / "golden").glob("*.yaml"))
    assert len(goldens) == 8, (
        "golden suite incomplete (§32, was 7, now 8 with CR-11AO basic-enterprise)")
    for f in goldens:
        code, report = _run_validator(f)
        assert code == 0, f"golden model {f.name} FAILED: {report['violations']}"


def test_negative_models_fail_for_expected_rule():
    invalids = sorted((BASE / "models" / "invalid").glob("*.yaml"))
    assert len(invalids) == len(EXPECTED_INVALID), "negative suite incomplete (§33)"
    for f in invalids:
        code, report = _run_validator(f)
        assert code == 1, f"negative model {f.name} unexpectedly PASSED"
        codes = {v["code"] for v in report["violations"]}
        assert EXPECTED_INVALID[f.name] in codes, \
            f"{f.name}: expected {EXPECTED_INVALID[f.name]}, got {codes}"


def test_envelope_schema_is_valid_json_schema():
    import jsonschema
    s = json.loads((BASE / "schemas" / "model-envelope.json").read_text())
    jsonschema.Draft7Validator.check_schema(s)


def test_specification_document_has_22_sections():
    doc = (SPEC / "OpenDEA-Semantic-Architecture-Specification.md").read_text()
    for n in range(1, 23):
        assert re.search(rf"^## {n}\. ", doc, re.M), f"spec missing section {n}"


def test_quality_gates(entities, relationships):
    # §66 machine-checkable gates
    assert (SPEC / "core-freeze.yaml").exists(), "gate: Core formally defined"
    assert (SPEC / "vocabulary.yaml").exists(), "gate: vocabulary"
    assert (BASE / "schemas" / "model-envelope.json").exists(), "gate: machine-readable schema"
    assert VALIDATOR.exists(), "gate: validation engine"
    assert (BASE / "mappings" / "archimate" / "mapping.yaml").exists(), "gate: external mapping"
    for r in relationships:
        assert r.get("cardinality"), f"gate: cardinality defined for {r['id']}"
        assert r.get("inverse"), f"gate: inverse defined for {r['id']}"


def test_visualization_profile_covers_overlay_dimensions():
    viz = yaml.safe_load((BASE / "visualization" / "profile" / "visualization.yaml").read_text())
    norm = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())
    dims = {d["id"] for d in norm["dimensions"]} - {"ecf-matrix"}
    assert dims <= set(viz["layout_hints"]["overlay_dimensions"]), \
        "visualization profile must cover every overlay dimension (§48)"


def test_archimate_mapping_targets_valid_entities(entities):
    ids = {e["id"] for e in entities}
    m = yaml.safe_load((BASE / "mappings" / "archimate" / "mapping.yaml").read_text())
    for entry in m["mappings"]:
        assert entry["opendea"] in ids, f"archimate mapping references unknown {entry['opendea']}"
        assert entry.get("note"), "§45: semantic differences must be documented"


def test_validator_report_shape():
    code, report = _run_validator(BASE / "models" / "invalid" / "unauthorized-agent.yaml")
    assert set(report) >= {"conformance", "model", "levels", "summary", "violations"}, "§28 report shape"
    v = report["violations"][0]
    assert set(v) >= {"rule", "code", "severity", "element", "message"}, "§28 violation shape"
