"""CR-9.1 model loader tests — the golden/negative contract extended to runtime.

- All 7 golden models (CR-8 §31-32) MUST load, preserving canonical entities
  and relationships verbatim (CR-9 DoD).
- All 8 negative models MUST be refused, and the graph MUST remain empty —
  validation happens before any mutation (CR-9K), and loads are atomic
  (CR-9BP).
"""
import pytest
import yaml

from conftest import BASE
from runtime.graph import InMemoryGraphStore
from runtime.model import ModelLoadError, load_model

GOLDEN = sorted((BASE / "models" / "golden").glob("*.yaml"))
INVALID = sorted((BASE / "models" / "invalid").glob("*.yaml"))

assert len(GOLDEN) == 7, "CR-8 §32 golden suite drifted"
assert len(INVALID) == 8, "CR-8 §33 negative suite drifted"


@pytest.mark.parametrize("path", GOLDEN, ids=[p.name for p in GOLDEN])
def test_golden_models_load(path):
    store = InMemoryGraphStore()
    report = load_model(path, store)
    doc = yaml.safe_load(path.read_text())
    expected_nodes = len(doc["elements"])
    expected_edges = sum(len(el.get("relationships", [])) for el in doc["elements"])
    assert report.nodes_loaded == expected_nodes
    assert report.edges_loaded == expected_edges
    assert store.stats() == {"nodes": expected_nodes, "edges": expected_edges}
    assert report.model_id == doc["model"]["id"]
    assert report.spec_version == "1.0.0"


@pytest.mark.parametrize("path", INVALID, ids=[p.name for p in INVALID])
def test_invalid_models_are_refused(path):
    store = InMemoryGraphStore()
    with pytest.raises(ModelLoadError) as exc:
        load_model(path, store)
    assert exc.value.report["conformance"]["status"] == "failed"
    assert exc.value.report["summary"]["errors"] > 0
    assert store.stats() == {"nodes": 0, "edges": 0}  # nothing partially loaded


def test_loaded_entities_preserve_envelope_fields():
    """Canonical entities/relationships preserved verbatim (CR-9 DoD)."""
    store = InMemoryGraphStore()
    load_model(BASE / "models" / "golden" / "enterprise.yaml", store)
    doc = yaml.safe_load((BASE / "models" / "golden" / "enterprise.yaml").read_text())
    for el in doc["elements"]:
        node = store.get_entity(el["id"])
        assert node.type == el["type"] and node.name == el["name"]
        for rel in el.get("relationships", []):
            edges = [e for e in store.edges_of(el["id"], direction="out")
                     if e.type == rel["type"] and e.target == rel["target"]]
            assert edges, f"{el['id']} -[{rel['type']}]-> {rel['target']} lost in load"


def test_load_report_is_a_receipt():
    store = InMemoryGraphStore()
    report = load_model(BASE / "models" / "golden" / "minimal-valid.yaml", store)
    d = report.as_dict()
    assert d["model"]["id"] == "example.minimal"
    assert d["loaded"] == {"nodes": 2, "edges": 1}
    assert set(d["conformance"].values()) == {"pass"}
