"""CR-CM-000 / CR-CM-000A / CR-CM-001: terminology alignment.

The terminology registry's canonical home is
``technehub-labs/dea-concepts-model · governance/terminology-registry.yaml``
(CR-CM-000A §14, realised by CR-CM-001). The local file
``vocabulary/terminology-registry.yaml`` is a governed **pointer**: these
tests assert pointer integrity and guard against content drift back into
this repo. Registry *content* conformance (term shape, verbs, prohibitions,
Concept Areas, AC rules) is owned by the canonical home, whose
``tools/validate.py`` exercises the vocabulary against every concept file.
"""
import re

import yaml

from conftest import BASE

REGISTRY_PATH = BASE / "vocabulary" / "terminology-registry.yaml"

CANONICAL_REPOSITORY = "technehub-labs/dea-concepts-model"
CANONICAL_PATH = "governance/terminology-registry.yaml"
CANONICAL_VERSION = "1.1.0"

# Content blocks that must NEVER reappear in the local pointer — the
# downgrade is only real while the content lives solely in the canonical
# home.
CONTENT_BLOCKS = {
    "terms",
    "reserved_terms",
    "concepts_model_terms",
    "conceptual_relationships",
    "prohibited",
    "initial_concept_areas",
    "planned_repository",
    "artifacts",
    "rules",
}


def _pointer():
    assert REGISTRY_PATH.exists(), "terminology registry pointer missing"
    return yaml.safe_load(REGISTRY_PATH.read_text())


# ---------------------------------------------------------------------------
# Landed-spec guards (unchanged — these verify the CR documents, not the
# registry content)
# ---------------------------------------------------------------------------

def test_cr_cm_000_landed_verbatim():
    path = BASE / "change-requests" / "CR-CM-000.md"
    assert path.exists(), "change-requests/CR-CM-000.md missing"
    text = path.read_text()
    assert text.startswith("CR-CM-000 — Terminology Alignment")
    for term in ("Domain", "Stage", "Concept Area", "Concept Profile",
                 "Concept Classification", "ECF Context"):
        assert term in text


def test_cr_cm_000a_landed_verbatim():
    path = BASE / "change-requests" / "CR-CM-000A.md"
    assert path.exists(), "change-requests/CR-CM-000A.md missing"
    text = path.read_text()
    assert "CR-CM-000A" in text
    assert "Concept Area" in text and "ECF Context" in text


# ---------------------------------------------------------------------------
# Pointer integrity (post-CR-CM-001)
# ---------------------------------------------------------------------------

def test_pointer_declares_canonical_home():
    """CR-CM-000A §14 + CR-CM-001: the pointer resolves to the canonical
    home in dea-concepts-model."""
    reg = _pointer()["registry"]
    home = reg["canonical_home"]
    assert home["repository"] == CANONICAL_REPOSITORY
    assert home["path"] == CANONICAL_PATH
    assert str(home["version"]) == CANONICAL_VERSION


def test_pointer_status_is_not_canonical():
    """The local copy must not claim canonical authority after migration."""
    reg = _pointer()["registry"]
    assert reg["status"] == "pointer", \
        "local copy downgraded: status must be 'pointer', never 'canonical'"


def test_pointer_records_full_provenance():
    reg = _pointer()["registry"]
    assert reg["introduced_by"] == "CR-CM-000"
    assert reg["extended_by"] == "CR-CM-000A"
    assert reg["homed_by"] == "CR-CM-001"


def test_pointer_version_parity_with_canonical():
    """The pointer declares the canonical version it tracks, so a canonical
    bump is visibly signalled here on review."""
    reg = _pointer()["registry"]
    assert str(reg["version"]) == CANONICAL_VERSION


def test_no_registry_content_remains_local():
    """Drift guard: the downgrade removed every content block. If any
    block reappears, this repo forks the registry and the two copies can
    diverge — the exact failure CR-CM-001 exists to prevent."""
    doc = _pointer()
    leaked = CONTENT_BLOCKS & set(doc)
    assert not leaked, \
        f"registry content blocks reappeared in the local pointer: {sorted(leaked)} — " \
        f"govern terms only in {CANONICAL_REPOSITORY}/{CANONICAL_PATH}"


# ---------------------------------------------------------------------------
# Forward guard (unchanged — does not read the registry)
# ---------------------------------------------------------------------------

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
