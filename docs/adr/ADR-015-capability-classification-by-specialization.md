# ADR-015: Capability classification: specialization over classifier entities

- Status: Proposed
- Date: 2026-08-31
- Deciders: OpenDEA architecture programme

## Context

`dea:BusinessCapability` is a flat Core anchor (L3, value delivery). The
catalogue discipline now requires typifying capabilities beyond the business
kind: system capabilities (KYC Identity Verification), infrastructure
capabilities (Data Encryption-at-Rest), AI-augmented capabilities
(Algorithmic Credit Scoring). A first-order classification is required so
that every capability compares uniformly across catalogues regardless of
kind, and so that the distinction between *what kind of capability* and
*where it sits in the enterprise* is preserved.

Four options were evaluated (2026-08-27):

- A: a new `CapabilityClass` entity above `BusinessCapability` in the
  inheritance chain.
- B: ECF coordinates as the first-order classifier.
- C: two metaclass parents (`CapabilityKind` + `CapabilityLayer`) with
  compound typing.
- D: `BusinessCapability` as the first-order root with sub-types.

The World Semantic Foundation canon has already resolved this shape.
ADR-WSF-07 grounds Capability in Disposition (capacity + ability, in
context); ADR-WSF-04 defines specialization as parent meaning plus
additional semantic constraint; and the published concept asset
`wsf/concepts/capability.md` already models `odea:BusinessCapability` as a
specialization of `wsf:Capability`. Option A duplicates the root concept
with an invented classifier (and violates the WSF cardinality principle:
no schema invented merely for symmetry). Option B conflates position with
nature. Option C senses the two orthogonal axes correctly but implements
both as typing. Option D applies the correct mechanism but roots it at a
concept that is itself a specialization.

## Decision

1. A new abstract Core entity `dea:Capability` SHALL be introduced as the
   root of all capability kinds. Definition, aligned to `wsf:Capability`:
   an attributable, contextualized potential of an Entity to accomplish a
   defined kind of effect, grounded in capacity and ability within a
   defined context.
2. `dea:BusinessCapability` SHALL specialize `dea:Capability`
   (`parent: dea:Capability`). Its meaning is preserved unchanged:
   parent meaning plus the additional constraints that it contributes to
   a business outcome, is owned by the business, and maps to ECF
   coordinates.
3. Further capability kinds SHALL be introduced only as specializations
   of `dea:Capability` (for example `SystemCapability`,
   `InfrastructureCapability`, `AIAugmentedCapability`), each defined as
   parent meaning plus additional semantic constraints per ADR-WSF-04.
   A kind specialization MUST NOT redefine capability semantics.
4. Kind specializations other than `BusinessCapability` SHALL be defined
   in profiles (ADR-002), not in the Core. The Core gains exactly one
   abstract anchor and no more, preserving the CR-8 Core freeze and the
   ADR-013 anti-accumulation rule.
5. Capability layer (Strategic / Operational / Support) SHALL be a
   governed enumeration attribute on `dea:Capability`, not a metamodel
   type and not a second inheritance parent.
6. ECF coordinates SHALL remain classification metadata on capability
   instances. They MUST NOT serve as the kind classifier: the matrix
   answers where a capability sits, not what kind it is.
7. Federation mapping SHALL be declared: `dea:Capability` maps 1:1 to
   `wsf:Capability`; `dea:BusinessCapability` maps to
   `odea:BusinessCapability` as already published in
   `wsf/concepts/capability.md`.
8. No classifier entity (`CapabilityClass`, `CapabilityKind`,
   `CapabilityLayer`) SHALL be added to the metamodel.

## Consequences

- Positive: one clean classification axis expressed through
  specialization; layer and ECF remain orthogonal attribute axes;
  catalogue entries become uniformly comparable across kinds without
  compound typing.
- Positive: Core inflation is contained to a single abstract anchor; the
  kind vocabulary is extensible in profiles without Core change.
- Positive: the metamodel is forward-compatible with WSF federation; the
  existing `wsf/concepts/capability.md` OpenDEA specialization becomes a
  declared mapping rather than an informal precedent.
- Negative: `dea:BusinessCapability` gains a parent; generated artifacts
  (JSON schemas, Pydantic models, TypeScript interfaces, entity graph)
  must regenerate; the generic legacy alias `Capability` migrates from
  `BusinessCapability` to the new root.
- Forecloses: Option A classifier entities; Option C compound typing;
  Option D mis-rooted hierarchy.

## References

- ADR-002: Core versus Profiles
- ADR-013: The Core does not accumulate
- CR-8: Core freeze and anti-inflation rule
- WSF ADR-WSF-04: Semantic Inheritance
- WSF ADR-WSF-07: Capacity:Ability:Capability
- WSF ADR-WSF-14: Semantic Context and Boundary
- `wsf/concepts/capability.md`: canonical Capability concept and OpenDEA
  specialization (World-Semantic-Foundation/wsf)
- Decision surface of 2026-08-27 (options A to D); selection of
  2026-08-31
