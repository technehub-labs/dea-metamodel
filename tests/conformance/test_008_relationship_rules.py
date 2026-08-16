"""CR-2 section 19: relationship validation rules R001-R012."""
import json

import yaml

from conftest import BASE

CATEGORIES = {
    "structural", "realization", "dependency", "flow", "serving", "execution",
    "governance", "information", "assessment", "transformation", "traceability",
}


def _crosswalk():
    return yaml.safe_load(
        (BASE / "metamodel" / "migration" / "relationship-crosswalk.yaml").read_text()
    )["crosswalk"]


def test_r001_unique_semantic_ids(relationships):
    ids = [r["id"] for r in relationships]
    assert len(ids) == len(set(ids)), "R001: duplicate relationship ids"


def test_r002_single_canonical_direction(relationships):
    for r in relationships:
        assert r["direction"] == "source-to-target", f"R002: {r['id']} direction"


def test_r003_valid_endpoint_types(relationships, entity_ids):
    for r in relationships:
        for t in r["source"]["types"] + r["target"]["types"]:
            assert t in entity_ids, f"R003: {r['id']} endpoint {t} not registered"


def test_r004_definitions_present(relationships):
    for r in relationships:
        assert len(r.get("definition", "")) >= 20, f"R004: {r['id']} definition missing/trivial"


def test_r005_instance_schema_types_defined(relationships):
    schema = json.loads((BASE / "schemas" / "relationships" / "relationship-instance.json").read_text())
    enum = set(schema["properties"]["relationship_type"]["enum"])
    registry = {r["id"].split(":", 1)[1] for r in relationships if not r.get("virtual")}
    assert enum == registry, \
        f"R005: instance enum vs registry mismatch: {enum ^ registry}"


def test_r006_no_undeclared_entity_relationship_state():
    # strengthened in CR-2F: duplicated properties must carry deprecated: true
    violations = []
    for p in sorted((BASE / "schemas" / "entities").glob("*.json")):
        schema = json.loads(p.read_text())
        for prop, spec in schema.get("properties", {}).items():
            if prop == "relationships":
                continue  # declared convenience
            if isinstance(spec, dict) and spec.get("deprecated"):
                continue  # CR-2F deprecation marking
            norm = prop.replace("-", "").replace("_", "").lower()
            if norm in {"owner", "realizedby", "providedby", "consumedby", "fundedby",
                        "fulfilledby", "parentcapability", "childcapabilities",
                        "parentprocess", "childprocesses", "parentou", "childous",
                        "parentconcept", "capabilitiesrealized", "governsexchanges",
                        "governedbyref", "relationshipdirection", "informedbytenets"} \
                    or norm.startswith("related"):
                violations.append(f"{p.name}: {prop}")
    assert not violations, f"R006: undeclared relationship state: {violations}"


def test_r007_inverses_declared(relationships):
    for r in relationships:
        inv = r.get("inverse")
        assert inv and inv.startswith("dea:"), f"R007: {r['id']} inverse not declared"
        if r.get("symmetric"):
            assert inv == r["id"], f"R009: symmetric {r['id']} must be its own inverse"


def test_r008_cardinalities_valid(relationships):
    for r in relationships:
        for end in ("source", "target"):
            assert r["cardinality"][end] in {"0..1", "1", "0..*", "1..*"}, \
                f"R008: {r['id']}.{end} cardinality"


def test_r009_symmetric_no_contradictory_inverse(relationships):
    for r in relationships:
        if r.get("symmetric"):
            assert r["inverse"] == r["id"], f"R009: {r['id']}"


def test_r010_endpoint_compatibility_checkable(relationships, entity_ids):
    # R010 is instance-level; the registry must provide the data to enforce it.
    for r in relationships:
        assert isinstance(r["source"]["types"], list) and isinstance(r["target"]["types"], list)
        assert all(t in entity_ids for t in r["source"]["types"] + r["target"]["types"])


def test_r011_deprecated_types_blocked_in_instance_schema():
    schema = json.loads((BASE / "schemas" / "relationships" / "relationship-instance.json").read_text())
    enum = set(schema["properties"]["relationship_type"]["enum"])
    superseded = {"influenced-by", "decomposes"}
    assert not (enum & superseded), \
        f"R011: superseded types still allowed for new instances: {enum & superseded}"


def test_r012_viewer_edges_resolve_to_registry():
    g = json.loads((BASE / "viewer" / "entity-graph.json").read_text())
    reg = yaml.safe_load((BASE / "metamodel" / "registry" / "relationships.yaml").read_text())
    reg_ids = {r["id"] for r in reg["relationships"]}
    unresolved = []
    for e in g["relationships"]:
        if "rel_ids" not in e:
            unresolved.append(f"{e['label']} ({e['rel_type']}): no rel_ids field")
            continue
        for rid in e["rel_ids"]:
            if rid not in reg_ids:
                unresolved.append(f"{e['label']}: {rid} not in registry")
    assert not unresolved, "R012: viewer edges not resolving:\n" + "\n".join(unresolved)


def test_crosswalk_complete():
    """Every observed viewer label has a disposition (CR-2 §16)."""
    g = json.loads((BASE / "viewer" / "entity-graph.json").read_text())
    observed = {(r["label"], r["rel_type"]) for r in g["relationships"]}
    mapped = {(m["current"], m["rel_type"]) for m in _crosswalk()["viewer_label_mappings"]}
    missing = observed - mapped
    assert not missing, f"crosswalk gaps: {missing}"


def test_categories_controlled(relationships):
    for r in relationships:
        assert r["category"] in CATEGORIES, f"{r['id']}: category {r['category']} not in A-K"


def test_maps_to_requires_mapping_kind():
    schema = json.loads((BASE / "schemas" / "relationships" / "relationship-instance.json").read_text())
    kinds = schema["properties"]["mapping"]["properties"]["kind"]["enum"]
    assert set(kinds) == {"equivalent", "broader", "narrower", "related", "traceability",
                          "external-crosswalk"}, "CR-2 §9 mapping kinds"


def test_agent_provenance_supported():
    """CR-2 §22: schema supports AI-asserted relationships."""
    schema = json.loads((BASE / "schemas" / "relationships" / "relationship-instance.json").read_text())
    prov = schema["properties"]["provenance"]["properties"]
    assert "agent_id" in prov and "verification_status" in prov
    assert "confidence" in schema["properties"]
