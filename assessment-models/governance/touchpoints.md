# Touchpoints — Handshake & Touchpoint Model

CR-AM-13 (issue #213). Governs how sibling assessment models in the
Assessment-Models ecosystem declare and mirror their seams, published as the
`maturity-touchpoint-contract` family in
`assessment-models/contracts/contract-suite.yaml` at **v0.1.0-draft**.

## Concepts

- **Handshake** — the pinned, contract-level linkage: which published
  contract family both sides score or declare against (e.g.
  `scored-by: maturity-scale-contract @ dea:maturity-bands-v2 v1.0.0`).
  Handshakes pin immutable references (tag or commit SHA), never a moving
  branch.
- **Touchpoint** — the semantic seam between two models at assessment time:
  who assesses which criteria, in which direction evidence flows, and how
  the overlap is resolved. Every touchpoint is declared once (in the model
  that owns the framing) and mirrored once in the peer repository.

## Record semantics

Validated by `assessment-models/schemas/maturity-touchpoints.schema.json`:

| Field | Meaning |
|---|---|
| `id` | Unique touchpoint or mirror-record id within the manifest |
| `mirrors` / `peer_touchpoint_id` | Mirror records: the paired declaration of the reciprocated endpoint. **Both fields are declared together or neither is** (CR-AM-13-R02); a record identifying a mirrored relationship with only one of them is structurally invalid |
| `peer_asset`, `peer_repo`, `peer_contract_version` | Peer identity and the peer contract line the record is written against |
| `direction`, `mapping_type` | `feeds`, `consumes`, `shared-component` or `boundary` |
| `criteria_mapping[]` | `ours` ↔ `theirs` permanent criterion-id pairs with free-text `note`; `theirs: pending-peer-register` is allowed while a peer register is in flight |
| `overlap_resolution` | Boundary doctrine: which side assesses what; shared evidence is single-assessed and cited by both models |
| `reciprocity` | `mirrors-<peer-touchpoint-id>` — names the peer record this declaration reciprocates (see Reciprocity vocabulary below) |
| `peer_status` / `status_note` | Lifecycle of the peer side (e.g. `mirror-merged-tag-pending`, `peer-release-merged-tag-pending`, `peer-remap-pending`) |

## Reciprocity vocabulary

The `reciprocity` field is constrained to the `mirrors-*` convention
(CR-AM-13-R03): `mirrors-` followed by the peer touchpoint id, e.g.
`mirrors-tp-ops-x-autonomous-operations`. The value is structural
self-description of the reciprocated endpoint; it is not itself proof that
the endpoint exists (see Validation boundary).

**Vocabulary transition, recorded explicitly.** Earlier 0.1.0-draft-era
material described a bare `required` placeholder. With the 2.1.x reciprocal
reconciliation, every published record across the registered portfolio
(all seven manifests: operations declarations and the six peer mirror
records) moved to the `mirrors-<id>` form; a portfolio compatibility
assessment (CR-AM-13 §6) verified no live record uses the placeholder. The
schema therefore constrains `reciprocity` to `^mirrors-[a-z0-9]+(-[a-z0-9]+)*$`
— no live record is invalidated, and `required` is retired rather than
permitted alongside the convention. Any future record attempting `required`
fails structural validation and must be corrected by its owning repository
through a separately scoped consumer change.

## Normative reciprocity requirements

Where a touchpoint declares a mirrored relationship, the referenced peer
MUST contain a corresponding reciprocal declaration that:

1. Identifies the originating model and touchpoint (its own
   `mirrors`/`peer_touchpoint_id` pair resolves back to the declaring
   record).
2. Identifies the corresponding peer endpoint (asset, repository, contract
   line).
3. Maintains the intended relationship semantics (direction/ownership
   boundary consistent with the declaring record's `overlap_resolution`).
4. Uses valid criterion mappings where criterion mappings are declared
   (`ours` ids exist in the owning model's register; `theirs` ids exist in
   the peer's, or are explicitly `pending-peer-register`).
5. Does not introduce contradictory or unresolved endpoint references.

These are ecosystem-level relationship requirements. They are normative for
every mirrored record regardless of what local tooling currently checks.

## Validation boundary

**Local schema validation establishes structural conformance only**
(CR-AM-13-R04). Passing the schema establishes: required properties and
data types; valid field formats and permitted values; internal record
structure; the paired `mirrors`/`peer_touchpoint_id` declarations; and a
well-formed representation of declared mappings.

It MUST NOT be represented as proof of:

- Peer repository or model existence.
- Peer touchpoint existence.
- Assessment criterion existence in the referenced model.
- Reciprocal relationship existence.
- Reciprocal endpoint consistency.
- Ecosystem-wide relationship integrity.

**Ecosystem-level semantic validation is a separate responsibility**
(CR-AM-13-R06), owned by `Assessment-Models/assessment-ci`. Its expected
scope: resolving peer model identity against the assessment registry;
resolving peer touchpoint identity against the peer model's declaration;
resolving mapped criteria against the appropriate model definitions;
checking reciprocal declarations and reverse endpoints; and reporting
unresolved, missing, contradictory or invalid relationships.

**Implementation status:** that ecosystem-level validation is NOT yet
implemented. Until it lands and has been successfully executed, a
structurally valid record with an unresolvable peer reference is
structurally conformant but semantically unresolved — not reciprocal.
Consumers and CI must not describe schema conformance as reciprocity
proof.

## Publication status

The family is declared at **v0.1.0-draft**; per the CR-AM-13 sequence (§10),
the immutable reference `v0.1.0-draft` is published and verified after this
governance/schema change is approved and merged — not before
(CR-AM-13-R07, CR-AM-11 §12). Consumers already declare
`maturity-touchpoint-contract 0.1.0-draft` in their handshakes; a consumer
manifest stays `status: draft` until the contract release it pins is tagged
and resolvable. Promotion to 1.0.0 is gated on at least three models
adopting the contract (CR-AM-13 §8 risk mitigation); adoption already
includes `maturity-model-operations` (declarations, six touchpoints) and
the six peers publishing mirror records (autonomous-operations,
digital-transformation, digital-transformation-operationalized,
modernization, services-delivery, technology).
