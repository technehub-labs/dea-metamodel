"""CR-4 section 30: ontology conformance rules O001-O009."""
import json

import yaml

from conftest import BASE


def _core():
    return yaml.safe_load((BASE / "metamodel" / "core" / "core.yaml").read_text())["ontology"]


def _profiles():
    profs = {}
    for p in sorted((BASE / "metamodel" / "profiles").glob("*/profile.yaml")):
        doc = yaml.safe_load(p.read_text())["profile"]
        profs[doc["id"]] = doc
    return profs


def test_o001_core_entities_have_definitions(entities):
    core_ids = set(_core()["entities"])
    core_ents = [e for e in entities if e["id"] in core_ids]
    assert len(core_ents) == len(core_ids), "core.yaml references unregistered entities"
    for e in core_ents:
        assert len(e.get("definition", "")) >= 30, f"O001: {e['id']} definition missing/trivial"


def test_o002_profiles_do_not_redefine_core(entities):
    # structural enforcement: profiles reference core entities by id and carry no
    # definitions of their own for them (profile.yaml files contain id lists only)
    for pid, prof in _profiles().items():
        for e in prof.get("entities", []):
            assert isinstance(e, str) and e.startswith("dea:"), f"O002: {pid} inline entity definition"


def test_o003_profiles_declare_dependencies():
    for pid, prof in _profiles().items():
        deps = prof.get("depends_on")
        assert deps and "dea:core" in deps, f"O003: {pid} missing dea:core dependency"


def test_o004_no_circular_profile_dependencies():
    profs = _profiles()
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {pid: WHITE for pid in profs}

    def visit(pid, path):
        color[pid] = GRAY
        for dep in profs[pid].get("depends_on", []):
            if dep == "dea:core":
                continue
            if dep not in profs:
                raise AssertionError(f"O003: {pid} depends on unknown profile {dep}")
            if color[dep] == GRAY:
                raise AssertionError(f"O004: circular dependency {' -> '.join(path + [dep])}")
            if color[dep] == WHITE:
                visit(dep, path + [dep])
        color[pid] = BLACK

    for pid in profs:
        if color[pid] == WHITE:
            visit(pid, [pid])


def test_o005_no_orphan_core_entities(entities, relationships):
    core_ids = set(_core()["entities"])
    connected = set()
    for r in relationships:
        connected |= set(r["source"]["types"]) | set(r["target"]["types"])
    orphans = core_ids - connected
    assert not orphans, f"O005: orphan core entities: {orphans}"


def test_o006_no_orphan_profile_entities(entities, relationships):
    connected = set()
    for r in relationships:
        connected |= set(r["source"]["types"]) | set(r["target"]["types"])
    orphans = []
    for e in entities:
        if e["membership"]["kind"] == "profile" and e["id"] not in connected:
            orphans.append(e["id"])
    assert not orphans, f"O006: profile entities not connected to the graph: {orphans}"


def test_o007_relationship_endpoints_registered(relationships, entity_ids):
    for r in relationships:
        for t in r["source"]["types"] + r["target"]["types"]:
            assert t in entity_ids, f"O007: {r['id']} endpoint {t} unregistered"


def test_o008_classification_cannot_alter_identity(entities):
    for e in entities:
        assert e["id"].startswith("dea:") and " " not in e["id"]
        # membership is metadata, never identity
        assert set(e["membership"].keys()) == {"kind", "profile"}


def test_o009_no_view_constructs_in_ontology(entities, relationships):
    for e in entities:
        assert not any(k in e for k in ("color", "style", "x", "y", "position")), \
            f"O009: view construct on {e['id']}"
    for r in relationships:
        assert "style" not in r, f"O009: style on {r['id']}"


def test_core_grammar_resolves_to_registry(relationships):
    reg_ids = {r["id"] for r in relationships}
    for g in _core()["relationship_grammar"]:
        assert g in reg_ids, f"core grammar {g} not in canonical registry"


def test_every_entity_has_membership(entities):
    for e in entities:
        m = e.get("membership")
        assert m and m["kind"] in {"core", "profile"}, f"{e['id']}: no core/profile membership"
        if m["kind"] == "profile":
            assert m["profile"] in _profiles(), f"{e['id']}: unknown profile {m['profile']}"
