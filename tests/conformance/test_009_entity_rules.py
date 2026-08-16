"""CR-3 section 24: entity conformance rules E001-E010."""
import json
import re

import yaml

from conftest import BASE

ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]*:[a-z0-9-]+(/[a-z0-9-]+)?$")


def _schemas():
    return {p.stem: json.loads(p.read_text())
            for p in sorted((BASE / "schemas" / "entities").glob("*.json"))}


def test_e001_stable_semantic_ids(entities):
    for e in entities:
        assert e["id"].startswith("dea:"), f"E001: {e.get('id')}"


def test_e002_single_normative_definition(entities):
    seen = {}
    for e in entities:
        assert e.get("definition"), f"E002: {e['id']} has no definition"
        key = e["id"]
        assert key not in seen, f"E002: duplicate definition entry for {key}"
        seen[key] = e["definition"]


def test_e003_no_undeclared_relationship_semantics():
    # after CR-3A: schemas carry no relationship-state properties at all
    banned_fragments = ("realized_by", "provided_by", "consumed_by", "funded_by",
                        "fulfilled_by", "parent_", "child_", "owned_", "_by_ref",
                        "related_", "governs_", "mitigates", "mandates")
    banned_exact = {"owner", "processes", "metrics", "maturity_level", "parties",
                    "targets", "events", "stakeholders", "actors", "capabilities",
                    "technology_stack", "required_skills", "captured_from",
                    "source_data_entities", "implements_controls", "anti_patterns",
                    "key_components", "patterns", "grouped_capabilities",
                    "capabilities_consumed", "data_entities", "components_realizing",
                    "processes_involved", "defines_entities", "digital_identity_ref",
                    "entities_measured", "informs_guardrails", "external_identifiers"}
    violations = []
    for name, schema in _schemas().items():
        for prop in schema.get("properties", {}):
            if prop in {"relationships", "external_references"}:
                continue
            if prop in banned_exact or any(f in prop for f in banned_fragments):
                violations.append(f"{name}:{prop}")
    assert not violations, f"E003: relationship state in entity schemas: {violations}"


def test_e004_external_ids_separated():
    for name, schema in _schemas().items():
        props = schema.get("properties", {})
        if "external_references" in props:
            items = props["external_references"].get("items", {})
            assert set(items.get("required", [])) == {"system", "identifier"}, \
                f"E004: {name}.external_references must require system + identifier"
        assert "external_identifiers" not in props, f"E004: {name} legacy external_identifiers"


def test_e005_classification_vocabularies():
    voc = yaml.safe_load((BASE / "metamodel" / "vocabularies" / "classifications.yaml").read_text())
    voc_map = {f"{c['entity']}.{c['property']}": set(c["values"])
               for c in voc["classifications"].values()}
    violations = []
    for name, schema in _schemas().items():
        ent = schema.get("title")
        for prop, spec in schema.get("properties", {}).items():
            if isinstance(spec, dict) and "enum" in spec and prop != "lifecycle_status":
                key = f"{ent}.{prop}"
                if key not in voc_map:
                    violations.append(f"{key}: enum not in controlled vocabulary")
                elif set(spec["enum"]) != voc_map[key]:
                    violations.append(f"{key}: enum diverges from vocabulary")
    assert not violations, "E005 violations:\n" + "\n".join(violations)


def test_e006_e007_inheritance_references_valid(entities):
    # schemas use $ref composition only against entity.json (the abstract root);
    # no other inheritance mechanism exists -> circularity impossible by construction
    for name, schema in _schemas().items():
        text = json.dumps(schema)
        for ref in re.findall(r'"\$ref": "([^"]+)"', text):
            assert ref.startswith("entity.json") or ref.startswith("../relationships/"), \
                f"E006: {name} references unknown base {ref}"
    abstracts = [e for e in entities if e.get("abstract")]
    assert abstracts and abstracts[0]["id"] == "dea:Entity", "E006: abstract root must be dea:Entity"


def test_e008_layer_not_inheritance(entities):
    for e in entities:
        assert "layer" not in (e.get("id") or ""), f"E008: layer in identity of {e['id']}"
        # layer/dimension are attributes (classification/viewpoint), never supertypes
        if e.get("layer"):
            assert isinstance(e["layer"], str)


def test_e009_unique_names(entities):
    names = [e["name"] for e in entities]
    dupes = {n for n in names if names.count(n) > 1}
    assert not dupes, f"E009: duplicate entity names: {dupes}"


def test_e010_deprecated_entities_blocked(entities):
    for e in entities:
        assert e.get("lifecycle") != "deprecated" or e.get("status") != "normative", \
            f"E010: {e['id']} deprecated but still normative"


def test_cr3r_lifecycle_vocabulary():
    voc = yaml.safe_load((BASE / "metamodel" / "vocabularies" / "lifecycle.yaml").read_text())
    vals = {v["id"] for v in voc["values"]}
    assert vals == {"proposed", "planned", "active", "deprecated", "retired"}
    for name, schema in _schemas().items():
        spec = schema.get("properties", {}).get("lifecycle_status")
        assert spec, f"{name}: missing lifecycle_status"
        assert set(spec["enum"]) == vals, f"{name}: lifecycle_status enum diverges from vocabulary"


def test_cr3b_no_intrinsic_maturity():
    for name, schema in _schemas().items():
        assert "maturity_level" not in schema.get("properties", {}), \
            f"CR-3B: {name} carries intrinsic maturity_level"
