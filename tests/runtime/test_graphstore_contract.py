"""CR-9CL seed — vendor-independent GraphStore contract suite.

Every GraphStore implementation (in-memory today; Neo4j/Neptune/ArangoDB/
PostgreSQL/RDF tomorrow) MUST pass these tests. To conform a new store, import
GraphStoreContract and subclass with a fixture returning the implementation::

    class TestNeo4jContract(GraphStoreContract):
        @pytest.fixture()
        def store(self): return Neo4jGraphStore(...)

The contract encodes CR-9D (implementation independence), CR-9E (first-class
edges with metadata), CR-9BP (transactions) and referential integrity.
"""
import pytest

from runtime.graph import (CanonicalIdError, DuplicateEntityError, Edge,
                           EntityNotFoundError, GraphStore, Node,
                           ReferentialIntegrityError)


class GraphStoreContract:
    """Reusable contract: define a `store` fixture in the subclass."""

    # ---- entity CRUD ----
    def test_create_and_get_entity(self, store: GraphStore):
        store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
        node = store.get_entity("cap.a")
        assert node.id == "cap.a" and node.type == "BusinessCapability"

    def test_duplicate_entity_rejected(self, store: GraphStore):
        store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
        with pytest.raises(DuplicateEntityError):
            store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A2"))

    def test_canonical_id_enforced(self, store: GraphStore):
        with pytest.raises(CanonicalIdError):
            Node(id="Customer Service", type="BusinessCapability", name="CS")
        with pytest.raises(CanonicalIdError):
            Node(id="Cap.X", type="BusinessCapability", name="CS")

    def test_get_missing_entity_raises(self, store: GraphStore):
        with pytest.raises(EntityNotFoundError):
            store.get_entity("nope")

    def test_update_entity(self, store: GraphStore):
        store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
        node = store.update_entity("cap.a", name="A Prime")
        assert node.name == "A Prime"
        assert store.get_entity("cap.a").name == "A Prime"

    def test_reads_are_defensive_copies(self, store: GraphStore):
        store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
        leaked = store.get_entity("cap.a")
        leaked.name = "MUTATED"
        assert store.get_entity("cap.a").name == "A"

    # ---- relationship CRUD + integrity ----
    def test_edge_requires_endpoints(self, store: GraphStore):
        store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
        with pytest.raises(ReferentialIntegrityError):
            store.create_relationship(Edge(type="supports", source="app.x",
                                           target="cap.a"))

    def test_edge_roundtrip_with_metadata(self, store: GraphStore):
        store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
        store.create_entity(Node(id="svc.a", type="BusinessService", name="S"))
        store.create_relationship(Edge(
            type="supports", source="svc.a", target="cap.a",
            valid_from="2026-01-01T00:00:00Z", status="active",
            provenance={"assertedBy": "architect-42",
                        "sourceSystem": "architectureRepository"},
            properties={"confidence": 0.94}))
        edges = store.edges_of("svc.a", direction="out")
        assert len(edges) == 1
        e = edges[0]
        assert e.type == "supports" and e.target == "cap.a"
        assert e.provenance["assertedBy"] == "architect-42"  # CR-9E
        assert e.properties["confidence"] == 0.94            # CR-9E
        assert e.valid_from == "2026-01-01T00:00:00Z"        # CR-9F

    def test_delete_entity_requires_cascade(self, store: GraphStore):
        store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
        store.create_entity(Node(id="svc.a", type="BusinessService", name="S"))
        store.create_relationship(Edge(type="supports", source="svc.a", target="cap.a"))
        with pytest.raises(ReferentialIntegrityError):
            store.delete_entity("cap.a")
        store.delete_entity("cap.a", cascade=True)
        assert not store.has_entity("cap.a")
        assert store.edges_of("svc.a") == []

    def test_delete_relationship(self, store: GraphStore):
        store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
        store.create_entity(Node(id="svc.a", type="BusinessService", name="S"))
        store.create_relationship(Edge(type="supports", source="svc.a", target="cap.a"))
        store.delete_relationship("svc.a", "supports", "cap.a")
        assert store.edges_of("svc.a") == []

    # ---- queries ----
    def test_query_by_type_and_predicate(self, store: GraphStore):
        store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
        store.create_entity(Node(id="cap.b", type="BusinessCapability", name="B"))
        store.create_entity(Node(id="app.c", type="ApplicationComponent", name="C"))
        assert {n.id for n in store.query(type="BusinessCapability")} == {"cap.a", "cap.b"}
        assert [n.id for n in store.query(where=lambda n: n.name == "C")] == ["app.c"]

    def test_neighbors_and_traverse(self, store: GraphStore):
        for nid, ntype in [("cap.a", "BusinessCapability"),
                           ("svc.a", "BusinessService"),
                           ("app.a", "ApplicationComponent")]:
            store.create_entity(Node(id=nid, type=ntype, name=nid))
        store.create_relationship(Edge(type="supports", source="svc.a", target="cap.a"))
        store.create_relationship(Edge(type="supports", source="app.a", target="svc.a"))
        assert [n.id for n in store.neighbors("app.a")] == ["svc.a"]
        assert {n.id for n in store.traverse("app.a")} == {"svc.a", "cap.a"}
        assert {n.id for n in store.traverse("cap.a", direction="in")} == {"svc.a", "app.a"}

    def test_find_path(self, store: GraphStore):
        for nid, ntype in [("cap.a", "BusinessCapability"),
                           ("svc.a", "BusinessService"),
                           ("app.a", "ApplicationComponent")]:
            store.create_entity(Node(id=nid, type=ntype, name=nid))
        store.create_relationship(Edge(type="supports", source="svc.a", target="cap.a"))
        store.create_relationship(Edge(type="supports", source="app.a", target="svc.a"))
        path = store.find_path("app.a", "cap.a")
        assert path is not None and len(path) == 2
        assert [e.type for e in path] == ["supports", "supports"]
        assert store.find_path("cap.a", "app.a") is None  # directed

    # ---- transactions (CR-9BP) ----
    def test_transaction_commit(self, store: GraphStore):
        with store.transaction():
            store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
        assert store.has_entity("cap.a")

    def test_transaction_rollback(self, store: GraphStore):
        store.create_entity(Node(id="cap.a", type="BusinessCapability", name="A"))
        with pytest.raises(RuntimeError):
            with store.transaction():
                store.create_entity(Node(id="cap.b", type="BusinessCapability", name="B"))
                raise RuntimeError("boom")
        assert not store.has_entity("cap.b")  # rolled back
        assert store.has_entity("cap.a")      # committed state untouched

    def test_stats(self, store: GraphStore):
        assert store.stats() == {"nodes": 0, "edges": 0}


class TestInMemoryGraphStore(GraphStoreContract):
    """The reference implementation must satisfy its own contract."""

    @pytest.fixture()
    def store(self):
        from runtime.graph import InMemoryGraphStore
        return InMemoryGraphStore()
