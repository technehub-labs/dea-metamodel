#!/usr/bin/env python3
"""Generate the OpenDEA specification artifacts from the normative source (CR-8).

CR-8 §49/§50: documentation is a GENERATED ARTIFACT, never a manually maintained
parallel truth. Everything here derives from metamodel/dea-metamodel.yaml +
metamodel/core/ + metamodel/profiles/.

Outputs:
  specification/semantic-inventory.yaml   (CR-8.1 inventory + CR-8.2 reconciliation)
  specification/vocabulary.yaml           (CR-8 §5 canonical vocabulary export)
  specification/catalogues/entities.md    (§49 concept catalogue)
  specification/catalogues/relationships.md (§49 relationship catalogue)

Run: python3 .github/scripts/generate_specification.py
"""
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

BASE = Path(__file__).parent.parent.parent
SPEC = BASE / "specification"

CR_OF_PROFILE = {
    "core": "CR-4",
    "dea:business": "CR-4", "dea:ecosystem": "CR-4", "dea:digital": "CR-4",
    "dea:data": "CR-4", "dea:technology": "CR-4", "dea:ai": "CR-4",
    "dea:governance-framework": "CR-4",
    "dea:assessment": "CR-5", "dea:dmm": "CR-5",
    "dea:lifecycle": "CR-6",
    "dea:governance": "CR-7", "dea:agentic": "CR-7",
}


def main():
    norm = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())
    version = norm["metamodel"]["version"]
    entities = norm["entities"]
    rels = norm["relationships"]

    SPEC.mkdir(exist_ok=True)
    (SPEC / "catalogues").mkdir(exist_ok=True)

    # ---------- CR-8.1 semantic inventory ----------
    inv_entities = []
    for e in entities:
        m = e.get("membership") or {}
        owner = "core" if m.get("kind") == "core" else m.get("profile")
        inv_entities.append({
            "id": e["id"], "name": e["name"],
            "semantic_category": owner,
            "abstract": bool(e.get("abstract")),
            "status": e.get("status"), "lifecycle": e.get("lifecycle"),
            "source_cr": CR_OF_PROFILE.get(owner, "CR-1..3"),
        })
    inv_rels = []
    for r in rels:
        inv_rels.append({
            "id": r["id"], "name": r["name"], "category": r["category"],
            "inverse": r.get("inverse"),
            "temporal": bool(r.get("temporal")),
            "status": r.get("status"),
        })

    # ---------- CR-8.2 reconciliation findings ----------
    findings = []
    name_counts = Counter(e["name"] for e in entities)
    for name, n in sorted(name_counts.items()):
        if n > 1:
            findings.append({"kind": "duplicate-name", "subject": name,
                             "resolution": "REVIEW REQUIRED"})
    # relationship inversions: declared inverse ids that collide with another canonical id
    rel_ids = {r["id"] for r in rels}
    for r in rels:
        inv = r.get("inverse")
        if inv and inv in rel_ids and inv != r["id"]:
            findings.append({"kind": "inverse-collides-with-canonical",
                             "subject": f"{r['id']} <-> {inv}",
                             "resolution": "documented: single canonical direction (CR-2 R002), inverse is query alias only"})
    if not any(f["kind"] == "duplicate-name" for f in findings):
        findings.append({"kind": "duplicate-name", "subject": "none",
                         "resolution": "clean — no duplicate canonical names (CR-8.2)"})

    inventory = {
        "inventory_version": version,
        "generated_from": "metamodel/dea-metamodel.yaml",
        "counts": {"entities": len(entities), "relationships": len(rels),
                   "core_entities": sum(1 for e in inv_entities if e["semantic_category"] == "core"),
                   "profiles": len(set(e["semantic_category"] for e in inv_entities) - {"core"})},
        "entities": inv_entities,
        "relationships": inv_rels,
        "reconciliation": findings,
    }
    (SPEC / "semantic-inventory.yaml").write_text(
        "# CR-8.1/8.2 semantic inventory + reconciliation — GENERATED, do not edit\n"
        + yaml.dump(inventory, sort_keys=False, allow_unicode=True, width=120))

    # ---------- CR-8 §5 canonical vocabulary ----------
    vocab = {
        "vocabulary_version": version,
        "namespace": "https://technehub-labs.github.io/dea-metamodel/",
        "prefix": "dea",
        "concepts": [{
            "id": e["id"], "name": e["name"], "canonical_name": e["name"].replace(" ", ""),
            "definition": e.get("definition", ""),
            "semantic_category": e2["semantic_category"],
            "abstract": e2["abstract"], "status": e.get("status"),
            "version": version,
        } for e, e2 in zip(entities, inv_entities)],
    }
    (SPEC / "vocabulary.yaml").write_text(
        "# CR-8 §5 canonical OpenDEA vocabulary — GENERATED, do not edit\n"
        + yaml.dump(vocab, sort_keys=False, allow_unicode=True, width=120))

    # ---------- §49 catalogues ----------
    ent_md = ["# OpenDEA Concept Catalogue (generated)", "",
              f"Version {version} — {len(entities)} concepts. Source: `metamodel/dea-metamodel.yaml`.", "",
              "| Concept | Category | Abstract | Definition |", "|---|---|---|---|"]
    for e, e2 in zip(entities, inv_entities):
        d = (e.get("definition", "") or "").replace("|", "\\|").replace("\n", " ")
        ent_md.append(f"| `{e['id']}` | {e2['semantic_category']} | {'yes' if e2['abstract'] else 'no'} | {d} |")
    (SPEC / "catalogues" / "entities.md").write_text("\n".join(ent_md) + "\n")

    rel_md = ["# OpenDEA Relationship Catalogue (generated)", "",
              f"Version {version} — {len(rels)} relationship types. Canonical direction is source-to-target (CR-2 R002); inverses are query aliases.", "",
              "| Relationship | Category | Inverse | Temporal | Definition |", "|---|---|---|---|---|"]
    for r in rels:
        d = (r.get("definition", "") or "").replace("|", "\\|").replace("\n", " ")
        rel_md.append(f"| `{r['id']}` | {r['category']} | `{r.get('inverse')}` | {'yes' if r.get('temporal') else 'no'} | {d} |")
    (SPEC / "catalogues" / "relationships.md").write_text("\n".join(rel_md) + "\n")

    print(f"specification generated at v{version}: inventory({len(entities)}e/{len(rels)}r), vocabulary, 2 catalogues")


if __name__ == "__main__":
    sys.exit(main())
