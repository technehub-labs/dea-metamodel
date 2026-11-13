#!/usr/bin/env python3
"""CR-AM-12 — cardinal root and cross-model relation validation.

Validates the federation's relatability surface (CR-AM-12 §3):

  1. CATALOGUE INTEGRITY — the reference catalogue resolves identity and
     version only, and every maturity model in the federation appears in it
     exactly once. A model that cannot be resolved from the root cannot be
     relatable to anything.

  2. ENDPOINT RESOLUTION — every edge endpoint and every comparability
     participant in model-relations.yaml resolves against the catalogue.
     A dangling endpoint is a broken edge, not a warning.

  3. RELATIONSHIP-TYPE CONFORMANCE — every edge carries a relationship_type
     from the CLOSED CR-AM-01 §17 vocabulary. `evaluated-by` is NOT in that
     vocabulary (it belongs to the CR-5 metamodel profile, where it means
     AssessmentResult → AggregationRule); using it here would be a
     vocabulary breach, so it is rejected explicitly with that reason.

  4. CORRELATION/CAUSAL SEPARATION (CR-MET-012 §6) — the two records are
     never collapsed. Every Correlation MUST carry confusion_guard: false
     (a correlation asserting causation is a governance failure); every
     CausalHypothesis MUST carry a validation_state, a falsification_test
     and a counter_evidence list; no Correlation may carry a mechanism, and
     no CausalHypothesis may present itself as an observed association.

  5. DOTTED-LINE COMPLETENESS — every capability model in the catalogue is
     reachable from the EA-practice model by a dotted-line edge, so the
     dotted line is total over the federation rather than partial.

Exit 0 with OK when clean; exit 1 listing every failure otherwise.

Usage:
  python3 assessment-models/tests/relations/test_model_relations.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOGUE = REPO_ROOT / "assessment-models" / "catalog" / "reference-catalog.yaml"
RELATIONS = REPO_ROOT / "assessment-models" / "catalog" / "model-relations.yaml"
VOCABULARY = REPO_ROOT / "assessment-models" / "vocabulary" / "relationship-types.yaml"
RELATION_EXAMPLES = REPO_ROOT / "assessment-models" / "relations" / "examples"

EA_PRACTICE_MODEL = "dea:maturity-ea-capability"

# Edge types that exist in the CR-5 metamodel profile but NOT in the closed
# CR-AM-01 §17 assessment vocabulary. Their presence here is a vocabulary
# breach, and the error says so rather than silently listing them.
PROFILE_ONLY_TYPES = {
    "evaluated-by": "belongs to the CR-5 metamodel profile (AssessmentResult "
                    "→ AggregationRule/ScoringRule), not to the closed §17 "
                    "assessment relationship vocabulary",
}


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def main() -> int:
    errors: list[str] = []

    catalogue = load(CATALOGUE)
    relations = load(RELATIONS)
    vocabulary = load(VOCABULARY)

    permitted = {v["id"] for v in vocabulary.get("values") or []}
    permitted |= set((vocabulary.get("legacy_aliases") or {}).keys())

    references = catalogue["catalogue"]["references"]
    by_id = {r["id"]: r for r in references}
    maturity_models = {r["id"] for r in references if r.get("kind") == "maturity-model"}

    # --- 1. catalogue integrity -------------------------------------------
    seen = set()
    for ref in references:
        key = (ref.get("kind"), ref.get("id"))
        if key in seen:
            errors.append(
                f"catalogue: duplicate ({ref.get('kind')}, {ref.get('id')}) entry"
            )
        seen.add(key)
        if not ref.get("version"):
            errors.append(f"catalogue: {ref.get('id')} has no version")

    if EA_PRACTICE_MODEL not in maturity_models:
        errors.append(
            f"catalogue: the EA-practice model {EA_PRACTICE_MODEL} is absent — "
            "the dotted line has no anchor"
        )

    # --- 2. endpoint resolution -------------------------------------------
    edges = relations["relations"].get("edges") or []
    comparability = relations["relations"].get("comparability") or []

    def resolve(endpoint: str, where: str) -> None:
        if endpoint not in by_id:
            errors.append(
                f"{where}: endpoint {endpoint!r} does not resolve against the "
                "reference catalogue"
            )

    for edge in edges:
        resolve(edge["source_id"], f"edge {edge.get('id')}")
        resolve(edge["target_id"], f"edge {edge.get('id')}")

    for comp in comparability:
        for model in comp.get("models") or []:
            resolve(model, f"comparability {comp.get('id')}")
        anchor = (comp.get("anchor_ref") or "")
        # anchor_ref is "<id>:<version>" — strip the version suffix to get the
        # canonical id the catalogue resolves.
        if anchor and anchor.rsplit(":", 1)[0] not in by_id:
            errors.append(
                f"comparability {comp.get('id')}: anchor_ref {anchor!r} does "
                "not resolve against the reference catalogue"
            )

    for anchor in relations["relations"].get("anchors") or []:
        resolve(anchor["id"], "anchor")

    # --- 3. relationship-type conformance ---------------------------------
    for edge in edges:
        rtype = edge.get("relationship_type")
        if rtype in PROFILE_ONLY_TYPES:
            errors.append(
                f"edge {edge.get('id')}: relationship_type {rtype!r} is not in "
                f"the closed §17 vocabulary — it {PROFILE_ONLY_TYPES[rtype]}"
            )
        elif rtype not in permitted:
            errors.append(
                f"edge {edge.get('id')}: relationship_type {rtype!r} is not in "
                f"the controlled vocabulary (allowed: {sorted(permitted)})"
            )

    # --- 4. correlation / causal separation -------------------------------
    examples = sorted(RELATION_EXAMPLES.glob("*.yaml"))
    if not examples:
        errors.append(
            f"relations/examples: no worked example found under {RELATION_EXAMPLES}"
        )

    for example in examples:
        doc = load(example)
        etype = doc.get("type")
        if etype == "Correlation":
            if doc.get("confusion_guard") is not False:
                errors.append(
                    f"{example.name}: a Correlation MUST carry confusion_guard: "
                    "false — a record that asserts causation from co-variation "
                    "alone is a governance failure (CR-MET-012 §6)"
                )
            for banned in ("mechanism", "cause_ref", "effect_ref",
                           "validation_state", "falsification_test"):
                if banned in doc:
                    errors.append(
                        f"{example.name}: a Correlation must not carry "
                        f"{banned!r} — the correlation/causal distinction must "
                        "not be collapsed (CR-MET-012 §6)"
                    )
        elif etype == "CausalHypothesis":
            if "confusion_guard" in doc:
                errors.append(
                    f"{example.name}: a CausalHypothesis asserts a mechanism; "
                    "it must not carry confusion_guard (that field belongs to a "
                    "Correlation, which asserts association only)"
                )
            if not doc.get("validation_state"):
                errors.append(
                    f"{example.name}: a CausalHypothesis MUST carry a "
                    "validation_state — 'asserted' is the honest value when "
                    "nobody has tested it"
                )
            if not doc.get("falsification_test"):
                errors.append(
                    f"{example.name}: a CausalHypothesis MUST carry a "
                    "falsification_test — a hypothesis with no test is not "
                    "testable"
                )
            if doc.get("counter_evidence") is None:
                errors.append(
                    f"{example.name}: a CausalHypothesis MUST carry a "
                    "counter_evidence list — absence of counter-evidence is "
                    "not evidence of its absence"
                )
        else:
            errors.append(
                f"{example.name}: expected type 'Correlation' or "
                f"'CausalHypothesis', got {etype!r}"
            )

    # --- 5. dotted-line completeness --------------------------------------
    dotted_targets = {
        edge["target_id"]
        for edge in edges
        if edge.get("dotted_line") and edge.get("source_id") == EA_PRACTICE_MODEL
    }
    for model in sorted(maturity_models):
        if model == EA_PRACTICE_MODEL:
            continue
        if model not in dotted_targets:
            errors.append(
                f"dotted line: {model} has no dotted-line edge from "
                f"{EA_PRACTICE_MODEL} — the dotted line must be total over "
                "the federation, not partial"
            )

    if errors:
        print(f"FAIL — {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        f"OK — catalogue: {len(references)} references "
        f"({len(maturity_models)} maturity models); "
        f"relations: {len(edges)} edges, {len(comparability)} comparability "
        f"declarations, {len(examples)} worked example(s)"
    )
    print(
        f"OK — every relationship_type is in the closed §17 vocabulary; "
        f"correlation/causal separation holds; dotted line covers all "
        f"{len(maturity_models) - 1} capability models"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
