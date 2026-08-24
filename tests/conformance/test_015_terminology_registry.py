"""CR-CM-000: terminology alignment — registry integrity and semantic
boundary enforcement between the Enterprise Concept Framework and the
OpenDEA Concepts Model (AC-1..AC-7)."""
import re

import yaml

from conftest import BASE

REGISTRY_PATH = BASE / "vocabulary" / "terminology-registry.yaml"
CR_PATH = BASE / "change-requests" / "CR-CM-000.md"

EXPECTED_ARTIFACTS = {
    "enterprise-concept-framework",
    "opendea-concepts-model",
    "opendea-foundational-metamodel",
    "catalogs",
    "profiles",
}
EXPECTED_RESERVED = {"Domain", "Stage"}
EXPECTED_CM_TERMS = {"Concept Area", "Concept Profile", "Concept Classification", "ECF Context"}


def _registry():
    assert REGISTRY_PATH.exists(), "CR-CM-000: terminology registry missing"
    return yaml.safe_load(REGISTRY_PATH.read_text())


def test_cr_cm_000_landed_verbatim():
    assert CR_PATH.exists(), "change-requests/CR-CM-000.md missing"
    text = CR_PATH.read_text()
    assert text.startswith("CR-CM-000 — Terminology Alignment")
    for term in ("Domain", "Stage", "Concept Area", "Concept Profile",
                 "Concept Classification", "ECF Context"):
        assert term in text


def test_registry_declares_all_five_artifact_boundaries():
    reg = _registry()
    ids = {a["id"] for a in reg["artifacts"]}
    assert ids == EXPECTED_ARTIFACTS, "registry must bound exactly the five CR-CM-000 artifacts"


def test_domain_and_stage_reserved_for_ecf():
    reg = _registry()
    reserved = {t["term"]: t for t in reg["reserved_terms"]}
    assert set(reserved) == EXPECTED_RESERVED
    for term, entry in reserved.items():
        assert entry["owner"] == "enterprise-concept-framework", \
            f"{term} must be owned by the Enterprise Concept Framework"
        assert entry["qualified_form"].startswith("ECF "), \
            f"{term} must declare an ECF-qualified form"


def test_concepts_model_terms_introduced():
    reg = _registry()
    terms = {t["term"]: t for t in reg["concepts_model_terms"]}
    assert set(terms) == EXPECTED_CM_TERMS
    for term, entry in terms.items():
        assert entry["owner"] == "opendea-concepts-model", \
            f"{term} must be owned by the OpenDEA Concepts Model"


def test_concept_area_membership_is_many_to_many():
    """AC-3: Concepts may belong to multiple Concept Areas."""
    reg = _registry()
    area = next(t for t in reg["concepts_model_terms"] if t["term"] == "Concept Area")
    assert area["constraints"]["membership"] == "many-to-many"


def test_ecf_context_cardinality_is_zero_or_more():
    """AC-4: Concepts may have zero or more ECF Contexts."""
    reg = _registry()
    ctx = next(t for t in reg["concepts_model_terms"] if t["term"] == "ECF Context")
    assert ctx["constraints"]["cardinality"] == "zero-or-more"


def test_concept_area_and_ecf_domain_are_distinct_no_one_to_one():
    """AC-5 + AC-6: different concepts; no automatic 1:1 mapping."""
    reg = _registry()
    area = next(t for t in reg["concepts_model_terms"] if t["term"] == "Concept Area")
    ctx = next(t for t in reg["concepts_model_terms"] if t["term"] == "ECF Context")
    for entry in (area, ctx):
        assert entry["constraints"]["distinct_from"] == "ecf-domain"
        assert entry["constraints"]["one_to_one_mapping_with_ecf_domain"] is False


def test_registry_precedes_first_concepts_model():
    """AC-7: the registry is introduced before the first canonical Concepts
    Model — asserted by the registry's own provenance declaration."""
    reg = _registry()
    assert reg["registry"]["introduced_by"] == "CR-CM-000"
    assert reg["registry"]["status"] == "canonical"


def test_registry_encodes_one_rule_per_acceptance_criterion():
    reg = _registry()
    criteria = {r["criterion"] for r in reg["rules"]}
    assert criteria == {f"AC-{i}" for i in range(1, 8)}, \
        "registry must encode exactly one rule per CR-CM-000 acceptance criterion"


def test_no_concepts_model_artifact_uses_bare_domain_field():
    """AC-1/AC-2 forward guard: when Concepts Model artifacts land, none may
    declare a bare `domain:` field — uses must be ECF-qualified or
    namespace-qualified."""
    candidates = [BASE / "concepts-model", BASE / "concepts-models"]
    for root in candidates:
        if not root.exists():
            continue
        for path in root.rglob("*.yaml"):
            text = path.read_text()
            bare = re.findall(r"^\s*domain:\s*\S", text, flags=re.MULTILINE)
            assert not bare, \
                f"{path.relative_to(BASE)} uses bare `domain:` — use `ecf_domain` or a namespace-qualified form (CR-CM-000 AC-1/AC-2)"


# ---------------------------------------------------------------------------
# CR-CM-000A supplement conformance
# ---------------------------------------------------------------------------

EXPECTED_TERMS = {
    "Domain", "Stage", "ECF Context", "Concept", "Concept Area",
    "Concept Profile", "Concept Classification", "Entity", "EntitySpec",
    "Relationship", "Catalog",
}
EXPECTED_VERBS = {
    "has-ecf-context", "uses-domain", "uses-stage", "belongs-to",
    "includes", "maps-to",
}
EXPECTED_INITIAL_AREAS = {
    "Enterprise", "Operations", "Intelligence", "Execution", "Control",
    "Scenario", "Value", "Measurement", "Systems",
}
EXPECTED_PROHIBITIONS = {
    "generic-domain-attribute", "concept-area-as-ecf-domain",
    "profile-as-domain", "implicit-metamodel-type",
}


def test_cr_cm_000a_landed_verbatim():
    path = BASE / "change-requests" / "CR-CM-000A.md"
    assert path.exists(), "change-requests/CR-CM-000A.md missing"
    text = path.read_text()
    assert "CR-CM-000A" in text
    assert "Concept Area" in text and "ECF Context" in text


def test_registry_declares_canonical_terms_with_namespace_status_owner():
    """CR-CM-000A §7 + §14: every canonical term carries the registry shape."""
    reg = _registry()
    terms = {t["name"]: t for t in reg["terms"]}
    assert set(terms) == EXPECTED_TERMS
    for name, entry in terms.items():
        for field in ("namespace", "status", "owner", "layer", "canonical_meaning"):
            assert entry.get(field), f"term {name} missing {field}"


def test_domain_and_stage_reserved_in_terms_block():
    """CR-CM-000A §3.1, §15."""
    reg = _registry()
    terms = {t["name"]: t for t in reg["terms"]}
    for reserved in ("Domain", "Stage"):
        assert terms[reserved]["namespace"] == "ECF"
        assert terms[reserved]["status"] == "reserved"
        assert terms[reserved]["owner"] == "dea-metaframework"


def test_concepts_model_terms_namespaced_to_concept_model():
    reg = _registry()
    terms = {t["name"]: t for t in reg["terms"]}
    for name in ("ECF Context", "Concept", "Concept Area", "Concept Profile",
                 "Concept Classification"):
        assert terms[name]["namespace"] == "ConceptModel"
        assert terms[name]["owner"] == "dea-concepts-model"


def test_conceptual_relationship_verbs_registered():
    """CR-CM-000A §9."""
    reg = _registry()
    verbs = {(r["id"], r["source"]) for r in reg["conceptual_relationships"]}
    assert {v for v, _ in verbs} == EXPECTED_VERBS
    # maps-to must be explicitly distinguished from inheritance
    maps_to = next(r for r in reg["conceptual_relationships"] if r["id"] == "maps-to")
    assert "inherits" in maps_to["note"] or "inheritance" in maps_to["note"]


def test_prohibited_semantics_registered():
    """CR-CM-000A §10."""
    reg = _registry()
    ids = {p["id"] for p in reg["prohibited"]}
    assert ids == EXPECTED_PROHIBITIONS


def test_initial_concept_areas_registered():
    """CR-CM-000A §11."""
    reg = _registry()
    assert set(reg["initial_concept_areas"]) == EXPECTED_INITIAL_AREAS


def test_planned_repository_uses_concept_areas_not_domains():
    """CR-CM-000A §15: the dea-concepts-model layout uses concept-areas/."""
    reg = _registry()
    planned = reg["planned_repository"]
    assert planned["name"] == "dea-concepts-model"
    assert "concept-areas/" in planned["required_layout"]
    assert "domains/" in planned["forbidden_paths"]
    assert "governance/terminology-registry.yaml" in planned["required_layout"]


def test_registry_records_extension_provenance():
    reg = _registry()
    assert reg["registry"]["introduced_by"] == "CR-CM-000"
    assert reg["registry"]["extended_by"] == "CR-CM-000A"
