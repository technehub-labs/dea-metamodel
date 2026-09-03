# CR-MM-PROC-01: Process Kernel + Business Process Specialization

| Field | Value |
|---|---|
| **CR** | CR-MM-PROC-01 |
| **Title** | Process Kernel + Business Process Specialization |
| **Status** | Proposed (working-folder draft; awaiting sign-off) |
| **Type** | Kernel introduction + specialization |
| **Scope** | `technehub-labs/dea-metamodel` |
| **Predecessor** | CR-016 (Capability kernel + specializations precedent); ADR-015; ADR-WSF-04; ADR-WSF-07; CR-BP-01 (catalog-side, superseded premise; see §15) |
| **Authority** | WSF (`World-Semantic-Foundation` local; not yet on GitHub). WSF `Process` is a Tier-3 derived construct — structural activity organization. |
| **Author** | Coder (for eaojnr) |
| **Date** | 2026-09-03 |

## 1. Change Request

Establish `dea:Process` as the **abstract Core kernel** for Process in
the OpenDEA Metamodel, and re-classify `dea:BusinessProcess` as its
**first specialization** (Business context). The architecture mirrors
the `Capability` precedent (CR-016, ADR-015) exactly:

```
WSF
 └─ Process              (structural activity construct; Tier-3 derived)

      └─ DEA inherits via specialization:

            dea:Process             (abstract Core kernel; this CR)
              ├── dea:BusinessProcess   (specialization; Core; this CR)
              │     ├─ dea:OperationalProcess   (future; ops context)
              │     ├─ dea:EngineeringProcess   (future; engineering context)
              │     └─ ... other contexts as needed
              │
              └─ (other DEA specializations to be added as use cases emerge)
```

**Why this CR exists now.** `dea:BusinessProcess` was introduced
into the Core in an earlier metamodel revision with `legacy_ids:
[dea:entity-process, Process]`. That framing promoted a single
specialization to the role of canonical kernel, which:

- contradicts the WSF discipline that `Process` is a foundational
  concept and that `Business Process` is a context specialization
  (mirroring `Capability` → `Business Capability`);
- blocks the introduction of other DEA Process specializations that
  are not "business" in nature (operations, engineering, science,
  etc.);
- forecloses the possibility of a separate catalog for non-business
  Process specializations, which the user has explicitly called for
  in the next phase.

This CR reverses the error: `dea:Process` becomes the abstract
Core kernel, and `dea:BusinessProcess` becomes the first concrete
specialization. The catalog at `dea-catalog-processes` is reframed
as the **Business Process specialization catalog**, not the
canonical Process catalog.

## 2. WSF Discipline (Authority Source)

Per `World-Semantic-Foundation/00_inbox/WSF-Foundational-Semantic-Synthesis-baseline-insight.md`:

> **Tier 3 — Derived Constructs (16):** Capacity, Ability,
> **Capability, Activity, Process, Workflow**, Transition, Outcome,
> Goal, Purpose, Intention, Policy, Rule, Requirement, Service,
> Resource, Role.

> **Capability Becomes Specialization (per §6) : KEY**
>
> ```
> WSF
>  └── Disposition
>        └── Capability
>              ├── Business Capability
>              ├── Operational Capability
>              └── Technical Capability
> ```
>
> Justifies OpenDEA's specialization without redefining universal
> meaning.

Per `World-Semantic-Foundation/00_inbox/WSF-Structure-Means-Investigation-baseline-insight.md`:

> **Process** describes the organized activity. A Process may be
> realized/represented as a Workflow. Workflow is deriv
> ational/operational rather than foundational in the same sense as
> Process.

Per `World-Semantic-Foundation/00_inbox/WSF_Ontological_Class_Investigation.md`:

> **Activity vs Process:** Activity is actual occurrence. Process
> organizes or specifies activities into a meaningful temporal/causal
> structure. This makes Process a structural activity construct.

> **Process ≠ Workflow (per §4):** Workflow describes the
> executable/coordination structure; **Workflow may be derived /
> representational rather than foundational in the same sense as
> Process. WSF should not prematurely promote Workflow to the same
> level as Entity or Capability.**

## 3. Architectural Decision

**Decision MM-PROC-01-D01** — `dea:Process` is the **abstract Core
kernel** for Process in the OpenDEA Metamodel. The WSF discipline is
inherited: Process is structural activity organization. All concrete
Process kinds are specializations per WSF ADR-WSF-04; they live in
the Core (for the first kind, mirroring `dea:BusinessCapability`) or
in profiles (for non-first kinds, mirroring
`dea:SystemCapability`).

**Decision MM-PROC-01-D02** — `dea:BusinessProcess` is the **first
specialization** of `dea:Process`, in the Core, anchored to the
`dea:business` profile by membership. It supports the Business
Architecture use case and Business Operations. Its sub-classifications
(`operational` / `support` / `management` carried by the catalog's
`process_intent` field) are preserved as catalog-internal semantics,
not promoted to additional kernel entities.

**Decision MM-PROC-01-D03** — Other DEA specializations of Process
(`dea:OperationalProcess`, `dea:EngineeringProcess`, etc.) **may be
added** when concrete use cases emerge. They are not introduced by this
CR; this CR only establishes the kernel and the first specialization.

**Decision MM-PROC-01-D04** — `wsf:Process` (in the forthcoming
`technehub-labs/wsf` repository) is the upstream reference class for
`dea:Process`. The federation mapping `dea:Process` ↔ `wsf:Process`
is recorded (ALIGNED; per WSF ADR-WSF-07 precedent used by
`dea:Capability` ↔ `wsf:Capability`).

## 4. Required Changes — `dea-metamodel`

### 4.1 Add `dea:Process` (abstract Core kernel)

In `metamodel/dea-metamodel.yaml`, immediately above the existing
`dea:BusinessProcess` entry (currently line 562), add:

```yaml
- id: dea:Process
  name: Process
  legacy_ids:
  - dea:entity-process      # pre-WSF authority id (CR-001 lineage)
  - Process                  # natural-language reference
  definition: 'A structural organization of activities into a
    meaningful temporal/causal pattern, grounded in the WSF
    Process discipline (wsf:Process; WSF Foundational Semantic
    Synthesis §6). Abstract root of all Process kinds; kinds are
    specializations per WSF ADR-WSF-04 and live in the Core
    (for the first kind) or in profiles (for non-first kinds).'
  layer: null
  dimension: null
  building_block: null
  abstract: true
  status: normative
  lifecycle: planned
  class_alias: null
  catalog_repo: null
  artifacts:
    json_schema: null
    sqlite_table: null
    pydantic_model: null
    ts_interface: null
  membership:
    kind: core
    profile: null
```

### 4.2 Reclassify `dea:BusinessProcess` as a specialization

The existing `dea:BusinessProcess` block (line 562) is preserved
**byte-equivalent except** for the `legacy_ids` and `definition`
fields. Specifically:

- `legacy_ids` is reduced from `[dea:entity-process, Process]` to
  `[]`. The two legacy ids migrate to `dea:Process.legacy_ids`
  (4.1). `dea:BusinessProcess.legacy_ids: []` reflects the fact
  that `dea:BusinessProcess` is itself a clean specialization with
  no prior identity confusion at this id.
- The `definition` is extended with the specialization lineage:
  *"Specializes `dea:Process` (this CR; ADR-015 precedent; WSF
  ADR-WSF-04). Supports Business Architecture and Business Operations
  use cases."*
- All other fields (`layer`, `dimension`, `building_block`,
  `abstract`, `status`, `lifecycle`, `class_alias`, `catalog_repo`,
  `artifacts`, `membership`) are unchanged.

### 4.3 Add `dea:specializes` registry entry

The `dea:specializes` relationship (per CR-016) gains `dea:Process`
in its source-type enumeration and `dea:Process` in its target-type
enumeration. The registry copy at
`metamodel/registry/relationships.yaml` is updated in lockstep.

A new specialization assertion is added:
`dea:BusinessProcess --specializes--> dea:Process`.

### 4.4 Federation mapping (WSF)

In `mappings/wsf/mapping.yaml`, add (mirroring
`dea:Capability ↔ wsf:Capability`):

```yaml
- dea_id: dea:Process
  wsf_id: wsf:Process
  confidence: EXACT
  lossiness: ""
  notes: |
    Abstract Core kernel; mirrors wsf:Process (WSF Foundational
    Semantic Synthesis §6; Tier-3 derived construct). Federation
    is alignment, not redefinition.
```

### 4.5 Schema implications

`schemas/entities/process.json` (the `dea:BusinessProcess` instance
schema) is **unchanged**. Its title `"Process"` is misleading
post-this-CR and should be updated to `"Business Process"` in a
follow-up minor edit (not part of this CR's scope).

`schemas/entities/entity.json` (the abstract entity root schema)
is unchanged. `dea:Process` has no instance schema (matches the
`dea:Capability` precedent: the abstract root is not directly
instantiated).

### 4.6 Vocabulary / glossary

`docs/glossary.md` (or equivalent) gains an entry for `dea:Process`
mirroring the entry for `dea:Capability` (abstract Core kernel).

## 5. Required Changes — Other Repos

### 5.1 `dea-architecture-framework` (OpenDEAM root model)

`model/opendeam-model.yaml` (currently line 500) declares
`dea:entity-process` as a layer-L3 entity. Post-this-CR, the root
model declares:

```yaml
- entity_id: dea:Process             # abstract Core kernel
  display_name: Process
  class_alias: null
  layer: null                         # abstract; not directly allocated
  dimension: null
  status: normative
  legacy_aliases:
  - dea:entity-process
- entity_id: dea:BusinessProcess     # specialization
  display_name: Business Process
  class_alias: BP
  layer: L3
  building_block: L3-value-delivery
  status: normative
  discriminator: business-process-specialization
```

A separate CR (CR-AR-FMWK-01) carries this update; it is gated on
this CR merging first.

### 5.2 `dea-catalog-processes`

The catalog at `dea-catalog-processes` is reframed as the **Business
Process specialization catalog**, not the canonical Process
catalog. A follow-up CR (CR-BP-SPEC-BP-01; drafted alongside this
CR) carries the catalog-side alignment:

- `metamodel-pointer.yaml` declares **two** entity ids:
  - `dea:Process` (kernel; not directly instantiated).
  - `dea:BusinessProcess` (specialization; instantiated).
- The legacy id `dea:entity-process` is recorded under
  `dea:Process.legacy_ids`, not under `dea:BusinessProcess`.
- The catalog name is reframed in prose (README): "Business Process
  Specialization Catalog — OpenDEA's Business Architecture context
  for the WSF Process kernel."
- Sub-classifications (`operational` / `support` / `management`)
  remain internal to the Business Process specialization, not promoted
  to kernel entities.

### 5.3 Capability catalog (parallel reference)

`dea-catalog-business-capabilities` already operates on
`dea:BusinessCapability` as a specialization of the abstract
`dea:Capability` kernel. This CR's Process architecture mirrors
that template exactly. No change required for the capability
catalog.

## 6. Sub-classifications Within Business Process (Preserved)

Per CR-BP-01 §7, the canonical Business Process definition is
**unchanged** by CR-BP-01 and remains so here:

> A structured set of activities that produces a defined outcome.

The catalog-internal sub-classifications of Business Process remain
valid and are **not** promoted to additional kernel entities:

| Sub-classification | Schema field | Status |
|---|---|---|
| Operational | `process_intent: operational` | Preserved (not a kernel) |
| Support | `process_intent: support` | Preserved (not a kernel) |
| Management | `process_intent: management` | Preserved (not a kernel) |

These are audience/intent classifications of Business Process
specifically, **not** Process kernel kinds. A future CR may
elevate one of them to a separate Process specialization
(`dea:OperationalProcess` for instance) if a non-Business use
case materializes.

## 7. Acceptance Criteria

- [ ] `dea:Process` exists as an abstract Core kernel in
      `metamodel/dea-metamodel.yaml` with `abstract: true`,
      `layer: null`, `class_alias: null`, `catalog_repo: null`.
- [ ] `dea:Process.legacy_ids` includes `dea:entity-process` and
      `Process`.
- [ ] `dea:BusinessProcess.legacy_ids` is empty.
- [ ] `dea:BusinessProcess.definition` records the specialization
      lineage (`Specializes dea:Process (this CR; ADR-015
      precedent; WSF ADR-WSF-04)`).
- [ ] `dea:specializes` registry entry accepts
      `dea:BusinessProcess -> dea:Process` and `dea:Process` as
      a valid target.
- [ ] Federation mapping `dea:Process <-> wsf:Process` exists in
      `mappings/wsf/mapping.yaml`.
- [ ] No competing canonical Process entity exists in the Core
      (verification: `grep "id: dea:.*Process" metamodel/dea-metamodel.yaml`
      returns the kernel + BusinessProcess + none of
      `dea:OperationalProcess` / `dea:EngineeringProcess` introduced
      by this CR).
- [ ] CR-AR-FMWK-01 (root-model update) is opened as a follow-up.
- [ ] CR-BP-SPEC-BP-01 (catalog-side alignment) is opened as a
      follow-up.

## 8. Why Not Just Promote `dea:BusinessProcess` Back?

A reasonable alternative to this CR is to keep `dea:BusinessProcess`
as the canonical kernel and add `dea:OperationalProcess`,
`dea:EngineeringProcess` etc. as siblings (not specializations).
That alternative was rejected because:

- it contradicts the WSF discipline that `Business` is a
  specialization context, not a kernel axis;
- it duplicates the WSF ↔ DEA federation work for every sibling;
- it removes the structural template established by CR-016
  (capability kinds as specializations of an abstract root);
- it forecloses the case where a Process is genuinely
  **context-neutral** (neither business, operations, nor
  engineering).

The specialization-from-kernel template is the established
OpenDEA discipline for context-bearing entity kinds; Process
follows it.

## 9. Out of Scope

- The introduction of `dea:OperationalProcess`,
  `dea:EngineeringProcess`, or any other Process specialization
  beyond Business. They are gated on a concrete use case.
- Workflow modeling (WSF separates Process from Workflow).
- Activity semantics (WSF separates Process from Activity
  occurrence).
- The catalog at `dea-catalog-processes` itself (handled by
  CR-BP-SPEC-BP-01; a separate repo).
- The OpenDEAM root model update (handled by CR-AR-FMWK-01; a
  separate repo).
- ECF matrix semantics (unchanged; Process Context is the
  catalog-level mechanism, governed by CR-BP-02+).

## 10. References

- `dea-metamodel/change-requests/CR-016.md` — Capability
  specialization precedent.
- `dea-metamodel/docs/adr/ADR-015-capability-classification-by-specialization.md`.
- `World-Semantic-Foundation/00_inbox/WSF-Foundational-Semantic-Synthesis-baseline-insight.md`
  §6 (Capability Becomes Specialization); Tier-3 derived construct
  list.
- `World-Semantic-Foundation/00_inbox/WSF-Structure-Means-Investigation-baseline-insight.md`
  §2-§7 (Process vs Workflow).
- `World-Semantic-Foundation/00_inbox/WSF_Ontological_Class_Investigation.md`
  §10 (Process as structural activity organization).
- `dea-catalog-processes/change-requests/CR-BP-01.md` —
  superseded catalog-side CR; the **canonical-identity decision
  is reversed** by this CR; the **governance / validator / CI work**
  is preserved and re-anchored (CR-BP-SPEC-BP-01).

## 11. Provenance

- Date: 2026-09-03
- Triggered by: user reframe 2026-09-03 ("WSF is authoritative on the
  concept of process; DEA is expected to inherit that and then
  create a specialization in the enterprise context, with the
  specialization being 'business'").
- Working folder: `/home/hermes/dea-work/process/00_inbox/`.

## 12. Versioning

No canonical version bump. The Core gains exactly one abstract
anchor (mirroring CR-016). Concrete kinds remain in the Core
(dea:BusinessProcess) and in profiles (future kinds, gated).

## 13. Migrations

No instance migration. The current
`dea-catalog-processes` schemas, governance docs, and (forthcoming)
catalog entries carry `dea:BusinessProcess` references; those remain
valid post-this-CR because `dea:BusinessProcess` is preserved (only
its `legacy_ids` and `definition` change).

## 14. Pitfalls and Watch-Outs

- The `dea:BusinessProcess` schema title
  (`schemas/entities/process.json` → `"title": "Process"`) is
  misleading post-this-CR; rename to `"Business Process"` in a
  follow-up minor edit (not this CR's scope).
- The `dea:specializes` relationship source/target type lists
  must be updated in **two** places (the relationship definition
  in `dea-metamodel.yaml` and the registry copy in
  `metamodel/registry/relationships.yaml`). Forgetting the second
  is a known drift trap.
- The OpenDEAM root model
  (`dea-architecture-framework/model/opendeam-model.yaml`)
  declares `dea:entity-process` as a layer-L3 entity. The CR does
  not touch the root model; CR-AR-FMWK-01 does.
- The `dea-catalog-processes` `validate-allocation` workflow
  pins `dea-architecture-framework@v0.2.1`. Until CR-AR-FMWK-01
  ships, the catalog's CI will continue to fail
  `validate-allocation` (because the root model still says
  `dea:entity-process`). This is acceptable; the failure is
  diagnostic of an upstream lag, not of the metamodel.

## 15. Relationship to CR-BP-01 (catalog-side)

CR-BP-01 (merged at `dea-catalog-processes@a34c7ff`) was drafted
before this CR. Its premise — that `dea:BusinessProcess` is the
sole canonical OpenDEA semantic identity for Process — is reversed
by this CR. The catalog-side artifacts (governance doc, validator,
CI wire, README/CHANGELOG) are **preserved and re-anchored** under
CR-BP-SPEC-BP-01, which declares:

- `dea:Process` (kernel) and `dea:BusinessProcess` (specialization)
  both declared in the catalog pointer.
- `dea:entity-process` is recorded as the legacy id of `dea:Process`,
  not of `dea:BusinessProcess`.
- The CR-BP-01 §7 canonical definition ("A structured set of
  activities that produces a defined outcome") is preserved as the
  BusinessProcess specialization definition.
- Sub-classifications (`operational` / `support` / `management`)
  remain catalog-internal.

A revert of `a34c7ff` is recommended before opening
CR-BP-SPEC-BP-01, so the new CR ships on a clean main.

## 16. Strategic Significance

This CR is structurally identical to CR-016 for Capability. It
completes the Process half of the kernel + specializations
discipline. Without it:

- other DEA Process specializations cannot be introduced
  coherently;
- the WSF ↔ DEA federation map has no Process anchor;
- the catalog at `dea-catalog-processes` is the *only* Process
  catalog, foreclosing non-business Process kinds.

With it:

- `dea:Process` is the kernel; WSF authority chain is honored;
- `dea:BusinessProcess` is the first specialization, anchored to
  the `dea:business` profile (mirroring `dea:BusinessCapability`);
- other specializations can be added as use cases emerge;
- the catalog at `dea-catalog-processes` becomes the Business
  Process specialization catalog, with a clean path to
  additional specialization catalogs (operations, engineering)
  when needed.