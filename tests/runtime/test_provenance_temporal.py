"""CR-9B/CR-9E/CR-9F — provenance, temporal state and graph semantics retention."""
from runtime.graph import Edge, InMemoryGraphStore, Node
from runtime.model import load_model

from conftest import BASE


def test_assertion_provenance_retained():
    """CR-9B: what is claimed stays distinct from what is — never collapsed."""
    store = InMemoryGraphStore()
    load_model(BASE / "models" / "golden" / "dmm.yaml", store)
    # dmm.yaml carries assertion/source metadata per CR-8 §40-43
    import yaml
    doc = yaml.safe_load((BASE / "models" / "golden" / "dmm.yaml").read_text())
    for el in doc["elements"]:
        node = store.get_entity(el["id"])
        if el.get("assertion"):
            assert node.assertion == el["assertion"]
        if el.get("source"):
            assert node.source == el["source"]


def test_edge_temporal_fields_retained():
    store = InMemoryGraphStore()
    store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
    store.create_entity(Node(id="svc.a", type="BusinessService", name="S"))
    store.create_relationship(Edge(type="supports", source="svc.a", target="cap.a",
                                   valid_from="2026-01-01T00:00:00Z",
                                   valid_to="2027-01-01T00:00:00Z",
                                   status="active"))
    e = store.edges_of("svc.a")[0]
    assert e.valid_from == "2026-01-01T00:00:00Z"
    assert e.valid_to == "2027-01-01T00:00:00Z"


def test_what_is_true_now():
    """CR-9F: temporal queries — now vs past vs future."""
    store = InMemoryGraphStore()
    store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
    store.create_entity(Node(id="svc.old", type="BusinessService", name="Old"))
    store.create_entity(Node(id="svc.new", type="BusinessService", name="New"))
    store.create_entity(Node(id="svc.future", type="BusinessService", name="Future"))
    store.create_relationship(Edge(type="supports", source="svc.old", target="cap.a",
                                   valid_from="2024-01-01T00:00:00Z",
                                   valid_to="2025-12-31T00:00:00Z", status="active"))
    store.create_relationship(Edge(type="supports", source="svc.new", target="cap.a",
                                   valid_from="2026-01-01T00:00:00Z", status="active"))
    store.create_relationship(Edge(type="supports", source="svc.future", target="cap.a",
                                   valid_from="2027-01-01T00:00:00Z", status="active"))

    def supporters(at):
        return {n.id for n in store.neighbors("cap.a", direction="in", at=at)}

    assert supporters("2024-06-01T00:00:00Z") == {"svc.old"}      # last year
    assert supporters("2026-06-01T00:00:00Z") == {"svc.new"}      # now
    assert supporters("2027-06-01T00:00:00Z") == {"svc.new", "svc.future"}  # next year


def test_planned_edge_is_never_current():
    """CR-6 §22: a planned edge must never be read as a current edge."""
    store = InMemoryGraphStore()
    store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
    store.create_entity(Node(id="svc.planned", type="BusinessService", name="Planned"))
    store.create_relationship(Edge(type="supports", source="svc.planned",
                                   target="cap.a", status="planned"))
    assert store.neighbors("cap.a", direction="in") == []


def test_derived_edge_keeps_provenance():
    """CR-9P/CR-9T seed: derived edges must declare what they derived from."""
    store = InMemoryGraphStore()
    store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
    store.create_entity(Node(id="obj.a", type="BusinessObjective", name="O"))
    store.create_relationship(Edge(
        type="supports", source="cap.a", target="obj.a",
        provenance={"derived_from": ["assertion.1", "assertion.2"],
                    "derivation_rule": "DEA-INF-007"}))
    e = store.edges_of("cap.a")[0]
    assert e.provenance["derivation_rule"] == "DEA-INF-007"
    assert e.provenance["derived_from"] == ["assertion.1", "assertion.2"]
