# Touchpoints — Handshake & Touchpoint Model

CR-AM-13 §5 (issue #213). Governs how sibling assessment models in the
Assessment-Models ecosystem declare and mirror their seams, published as the
`maturity-touchpoint-contract` family in
`assessment-models/contracts/contract-suite.yaml`.

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
| `mirrors` / `peer_touchpoint_id` | Mirror records: the declaring record this one reciprocates |
| `peer_asset`, `peer_repo`, `peer_contract_version` | Peer identity and the peer contract line the record is written against |
| `direction`, `mapping_type` | `feeds`, `consumes`, `shared-component` or `boundary` |
| `criteria_mapping[]` | `ours` ↔ `theirs` permanent criterion-id pairs with free-text `note`; `theirs: pending-peer-register` is allowed while a peer register is in flight |
| `overlap_resolution` | Boundary doctrine: which side assesses what; shared evidence is single-assessed and cited by both models |
| `reciprocity` | `required` — ecosystem CI checks the mirrored record exists with the reverse identity |
| `peer_status` / `status_note` | Lifecycle of the peer side (e.g. `mirror-merged-tag-pending`, `peer-release-merged-tag-pending`) |

## Reciprocity rule

A declared touchpoint **requires** a mirrored record in the peer repository
(`mirrors:` + `peer_touchpoint_id:`), and vice versa. Duplicated criteria
across models are prohibited: a seam either single-assesses evidence once and
cites it from both sides, or splits ownership by an explicit boundary
declaration.

## Versioning

The family publishes at **v0.1.0-draft** (issue #213). Promotion to 1.0.0 is
gated on at least three models adopting the contract (CR-AM-13 §8 risk
mitigation); adoption already includes
`maturity-model-operations` (declarations, 6 touchpoints) and the six peers
publishing mirror records (autonomous-operations, digital-transformation,
digital-transformation-operationalized, modernization, services-delivery,
technology). A consumer manifest stays `status: draft` until the contract
release it pins is tagged and resolvable.
