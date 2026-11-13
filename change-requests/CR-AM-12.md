# CR-AM-12 — Cardinal Root, Cross-Model Relations and the Dotted Line

## Status

- **State:** Proposed (this PR).
- **Series tag:** `CR-AM` (Assessment Metamodel). Continues after CR-AM-11.
- **Primary repo:** `technehub-labs/dea-metamodel` (catalogue, relations graph, schemas, CI).
- **Companion repos:** `Assessment-Models/assessment-registry` (the `canonical` binding and the
  org-local root view), `Assessment-Models/assessment-ci` (the cross-org binding check),
  `technehub-labs/dea-governance` (the federated reconciler), and the new DEA-owned
  `technehub-labs/maturity-model-ea-capability`.
- **Umbrella:** CR-AM-01 (OpenDEA Assessment Metamodel Evolution).
- **Depends on:** CR-AM-03 (reference catalogue, portfolio), CR-AM-09 (maturity scale and the
  canonical v2 band instance), CR-AM-11 (federated assessment model ecosystem).
- **Related:** CR-MET-012 §6 (the correlation / causal-hypothesis distinction).
- **Owner:** Emmanuel A. Otchere.

## Primary objective

Give the federation the **cardinal root** the vision requires: a single reference surface on
which every maturity model in the Assessment-Models organisation is **relatable and traceable**,
so that an organisation holding, say, a Technology maturity result and a Services Delivery
maturity result can reason about the relationship between them — and so that a capability
model's weak result can be traced back to weak enterprise architecture practice.

CR-AM-11 delivered the repo-per-model topology (each model independently versioned and
released) and the registry as the integration spine. What it did not deliver is the
*relatability* half: the federation could resolve each model's repository, but nothing bound
the models to each other, and the upstream reference catalogue covered only four of the eight
models, so two-thirds of the federation had no canonical identity at all.

## What this CR changes

### 1. The reference catalogue becomes the cardinal root (v1.0.0 → v1.1.0)

`assessment-models/catalog/reference-catalog.yaml` gains every published maturity model plus
the component registry and the shared band instance:

| Kind | Id | Version |
|---|---|---|
| `maturity-model` | `dea:maturity-technology` | 1.0.0 |
| `maturity-model` | `dea:maturity-modernization` | 1.0.0 |
| `maturity-model` | `dea:maturity-operations` | 1.0.0 |
| `maturity-model` | `dea:maturity-services-delivery` | 1.0.0 |
| `maturity-model` | `dea:maturity-autonomous-operations` | 1.0.1 |
| `maturity-model` | `dea:maturity-digital-transformation-operationalized` | 1.0.1 |
| `maturity-model` | `dea:maturity-digital-transformation` | 1.0.0 |
| `maturity-model` | `dea:maturity-ea-capability` | 1.0.0 |
| `component-registry` | `dea:registry-maturity-components` | 1.0.0 |
| `maturity-bands` | `dea:maturity-bands-v2` | 1.0.0 |

The band instance is included because **every** model in the federation declares
`band_reference: dea:maturity-bands-v2` — it is the one reference genuinely common to all of
them, and the coordinate system on which cross-model comparison actually happens. It was
absent from the catalogue while being depended upon by every model.

The catalogue is versioned 1.1.0 (minor: additive references only, no existing entry changed).

### 2. Id reconciliation — five inconsistencies, not three

Extending the catalogue surfaced id drift between what a model calls itself and what the
federation calls it. These are corrected here, and each correction is a *fix* of a divergence,
never a rename of a published artefact:

| Model | Divergent self-declaration | Reconciled canonical id |
|---|---|---|
| Autonomous Operations | `dea:maturity-autonomous-operations-dimensions` (repo register) | `dea:maturity-autonomous-operations` |
| Digital Transformation (composite) | `dea:maturity-model-digital-transformation` (component registry `published_by`) | `dea:maturity-digital-transformation` |
| Autonomous Operations (example) | `model: dea:maturity-autonomous-operations` | consistent — no change |

The `-dimensions` suffix named the repo's *criteria register*, not the model; the composite
model's `published_by` carried the repo name rather than the model id. Both were recorded in
the upstream artefacts and are corrected at source in the companion repositories
(`Assessment-Models/maturity-model-autonomous-operations` and the upstream component registry).

### 3. `model-relations.yaml` — the federation's relatability graph

A new artefact, `assessment-models/catalog/model-relations.yaml`, declaring two structures
that are deliberately kept apart:

- **`edges`** — the structural relation graph over canonical model references. Every edge
  carries a `relationship_type` drawn from the **closed** CR-AM-01 §17 vocabulary. The dotted
  line is declared here: `dea:maturity-ea-capability` **supports** each capability model.
  Each dotted-line edge also records the *traversal* direction (capability model → EA-practice
  model), because the edge records the direction of influence while the dotted line is the
  direction of explanation.

- **`comparability`** — the declared cross-model *comparison* surface: which model pairs may be
  correlated, on which axis, anchored to what. This is deliberately **not** a structural edge:
  a comparison is a derived analytical artefact over scores, not a containment or derivation
  relationship between two models. Encoding it as an edge would assert a structural fact the
  vision does not claim.

#### The finding that shapes the comparability surface

Every capability and measure id in the reference catalogue is **domain-scoped**
(`dea:capability-technology-architecture` vs `dea:capability-incident-response-capability`).
**No two capability maturity models share a single capability or measure id.** The only
measurement anchor genuinely shared across all models is the canonical v2 band instance.

Consequently, cross-model correlation is computable **today at model-score level only**. The
comparability declarations say so per pair (`shared_capabilities: []`, `shared_measures: []`)
rather than implying a capability-level join that does not exist. Raising a pair to
capability level is a *content* change in the catalogue — both models must bind the same
canonical capability id — not a change to the relation graph. This is stated explicitly so
the next implementer does not read the empty lists as an oversight.

### 4. Correlation and causation are carried as two distinct records (CR-MET-012 §6)

The vision asks for "the causal relationships and correlations between the scores". The
metamodel has already decided how to honour that without collapsing the two
(CR-MET-012 §6, Q22c): they are distinct first-class constructs and must not be merged. This
CR applies that decision rather than re-deciding it.

Two worked examples land under `assessment-models/relations/examples/`:

- `correlation-technology-services-delivery.yaml` — a `dea:Correlation` recording **observed
  co-variation only**, with the mandatory `confusion_guard: false`.
- `causal-hypothesis-ea-practice-to-technology-maturity.yaml` — a `dea:CausalHypothesis`
  recording the **asserted mechanism** of the dotted line, with `validation_state: asserted`
  (nobody has run the falsification test), declared confidence, explicit counter-evidence and
  a falsification test.

The dotted line is therefore an *asserted, falsifiable, explicitly-unvalidated* influence —
never a proven cause, and never reported as one. A correlation is never dressed as causation.

### 5. CI enforcement

A new `validate-model-relations` job fails the build on:

1. catalogue integrity — duplicate or unversioned entries; a missing EA-practice model (the
   dotted line would have no anchor);
2. endpoint resolution — every edge endpoint, comparability participant and anchor must
   resolve against the catalogue;
3. relationship-type conformance — every `relationship_type` must be in the closed §17
   vocabulary. `evaluated-by` is rejected **with its reason**: it belongs to the CR-5 metamodel
   profile (`AssessmentResult → AggregationRule/ScoringRule`), not to the assessment vocabulary,
   so it is the wrong shape for a model→model edge;
4. correlation/causal separation — a `Correlation` must carry `confusion_guard: false` and must
   not carry `mechanism`/`cause_ref`/`effect_ref`/`validation_state`/`falsification_test`; a
   `CausalHypothesis` must carry `validation_state`, `falsification_test` and
   `counter_evidence`, and must not carry `confusion_guard`;
5. dotted-line totality — every capability model in the catalogue must be reachable from the
   EA-practice model by a dotted-line edge, so the dotted line is total over the federation
   rather than partial.

The two worked examples are additionally validated against the published entity schemas
(`schemas/entities/correlation.json`, `schemas/entities/causal-hypothesis.json`).

## Scope

In scope:
- The catalogue extension, the relations graph, the two worked examples, the CI job, the
  validator script, this CR, and the changelog entry.
- The companion `canonical` binding in the Assessment-Models registry and the cross-org binding
  check in `Assessment-Models/assessment-ci` (separate PR, same CR).
- The DEA-owned `technehub-labs/maturity-model-ea-capability` repository (separate PR, same CR).
- The federated reconciler extension in `technehub-labs/dea-governance` (separate PR, same CR).

Out of scope:
- **Capability-level cross-model correlation.** Not computable until the catalogue gives two
  models a shared canonical capability id. Recorded as a finding, not silently enabled.
- **A Customer Experience maturity model.** New model content, not a metamodel change; tracked
  separately.
- **Any change to a published model's rubric, levels, criteria or scoring.** This CR adds
  identity, relation and governance surfaces only. No existing assessment result may be
  reinterpreted by it.
- **The legacy v1-alpha cluster.** Remains frozen per CR-AM-01 Release 1 decision D-1.

## Compatibility

Additive. No schema is changed; no existing catalogue entry is modified; no vocabulary value
is added, removed or re-scoped. Existing reference resolution is unaffected. New artefacts are
new files. The catalogue's own version moves 1.0.0 → 1.1.0, consistent with
`assessment-models/governance/versioning.md` (minor: additive references).

## Acceptance criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-1 | Every published maturity model resolves from the catalogue by one reconciled canonical id | `validate-model-relations` step 1; catalogue carries 8 maturity models |
| AC-2 | The catalogue resolves no dangling reference | `validate-model-relations` step 2 — every endpoint, participant and anchor resolves |
| AC-3 | Every edge type is in the closed §17 vocabulary | `validate-model-relations` step 3, with `evaluated-by` rejected with its reason |
| AC-4 | Correlation and causation are never collapsed | `validate-model-relations` step 4; both worked examples validate against the published entity schemas |
| AC-5 | The dotted line covers every capability model | `validate-model-relations` step 5 — 7 of 7 capability models reachable from `dea:maturity-ea-capability` |
| AC-6 | The declared comparison surface states what is genuinely comparable | `comparability` declarations carry `shared_capabilities`/`shared_measures` per pair, empty where the catalogue proves no shared id |
| AC-7 | The shared measurement anchor is resolvable | `dea:maturity-bands-v2` published in the catalogue as `maturity-bands` |
| AC-8 | No existing behaviour regresses | The pre-existing 387-test assessment-models suite passes unchanged |

## Decision notes

- **D-1 — the catalogue resolves identity; the registry resolves location.** The catalogue is
  the federation-wide *resolution authority for canonical references*. It does **not** carry
  repository pointers. Putting `Assessment-Models/<repo>` into the upstream catalogue would make
  every Assessment-Models repo creation, rename or release a standing upstream PR in a
  different organisation — a structural coupling the federation explicitly rejects
  (`Assessment-Models/.github/GOVERNANCE.md`: *"Cross-organization dependencies are contractual
  (pinned, immutable contract releases), never repository-structural"*). The two sides are
  instead joined **machine-readably and CI-enforced on both sides**: the upstream publishes
  canonical id + version; the registry declares a `canonical` binding; the binding check
  asserts the two agree. Neither side duplicates the other's fact.
- **D-2 — correlation and causation are carried as two records, not chosen between.** The
  metamodel decision already exists (CR-MET-012 §6); this CR applies it. The vision's
  "causal relationships" is honoured by the `CausalHypothesis` record — an asserted,
  falsifiable, explicitly-unvalidated mechanism — and never by a correlation.
- **D-3 — `supports` is the dotted-line edge type.** `evaluated-by` is not in the closed
  assessment vocabulary, and `compatible-with` is not in the metamodel relationship-instance
  enum either. `supports` is legal in both, and its direction (EA practice supports capability
  maturity) is the direction of influence, with the traversal direction recorded separately.
- **D-4 — the comparison surface is separate from the structural graph.** See §3 above.
