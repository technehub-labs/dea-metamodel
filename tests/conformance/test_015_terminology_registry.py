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
