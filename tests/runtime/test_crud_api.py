"""CR-9.1 entity/relationship API tests — registry-backed write validation."""
import pytest

from runtime.api import RuntimeService, SemanticValidationError
from runtime.graph import InMemoryGraphStore


@pytest.fixture()
def svc():
    return RuntimeService(InMemoryGraphStore())


def test_create_entity_validates_type(svc):
    with pytest.raises(SemanticValidationError, match="DEA-E001"):
        svc.create_entity("x.y", "NotAType", "Nope")


def test_create_entity_rejects_abstract_type(svc):
    # Entity is the abstract root in the canonical registry (CR-8 §9)
    with pytest.raises(SemanticValidationError, match="abstract"):
        svc.create_entity("x.y", "Entity", "Nope")


def test_create_entity_enforces_canonical_id(svc):
    with pytest.raises(SemanticValidationError, match="CR-8 §7"):
        svc.create_entity("Customer Service", "BusinessCapability", "CS")


def test_create_relationship_validates_type(svc):
    svc.create_entity("cap.a", "BusinessCapability", "A")
    svc.create_entity("svc.a", "BusinessService", "S")
    with pytest.raises(SemanticValidationError, match="DEA-E002"):
        svc.create_relationship("svc.a", "not-a-relationship", "cap.a")


def test_create_relationship_validates_endpoints(svc):
    svc.create_entity("svc.a", "BusinessService", "S")
    svc.create_entity("cap.a", "BusinessCapability", "A")
    # registry: supports sources are Actor/ApplicationComponent/Technology/… — not BusinessService
    with pytest.raises(SemanticValidationError, match="DEA-E006"):
        svc.create_relationship("svc.a", "supports", "cap.a")


def test_create_relationship_happy_path(svc):
    svc.create_entity("cap.a", "BusinessCapability", "A")
    svc.create_entity("app.a", "ApplicationComponent", "App")
    edge = svc.create_relationship("app.a", "supports", "cap.a",
                                   status="active",
                                   provenance={"assertedBy": "architect-42"})
    assert edge.type == "supports"
    assert svc.neighbors("app.a")[0].id == "cap.a"


def test_type_hierarchy_accepted(svc):
    """Agent specializes Actor (CR-7) — hierarchy-aware endpoint checks."""
    svc.create_entity("agent.a", "Agent", "A",
                      properties={"authority_ref": "auth.1", "owner_ref": "person.1"})
    svc.create_entity("pol.a", "Policy", "P")
    # constrained-by: Actor branch source must accept Agent via the TTL hierarchy
    edge = svc.create_relationship("agent.a", "constrained-by", "pol.a")
    assert edge.target == "pol.a"


def test_entity_type_immutable(svc):
    svc.create_entity("cap.a", "BusinessCapability", "A")
    with pytest.raises(SemanticValidationError, match="immutable"):
        svc.update_entity("cap.a", type="ApplicationComponent")


def test_delete_and_query(svc):
    svc.create_entity("cap.a", "BusinessCapability", "A")
    svc.create_entity("cap.b", "BusinessCapability", "B")
    assert len(svc.query(type="BusinessCapability")) == 2
    svc.delete_entity("cap.b")
    assert [n.id for n in svc.query(type="BusinessCapability")] == ["cap.a"]
