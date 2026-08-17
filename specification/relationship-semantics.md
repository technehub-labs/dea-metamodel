# Relationship Semantics (CR-8 §10-§14)

The canonical relationship vocabulary lives in `metamodel/registry/relationships.yaml`
(104 types at v1.0.0) with the full catalogue in
[`catalogues/relationships.md`](./catalogues/relationships.md) (generated).

## Rules

1. **Closed vocabulary (§10).** New relationship types enter only via CR. Arbitrary names
   must not proliferate — an undeclared `relationship_type` in a model is `DEA-E002`.
2. **Single canonical direction (§12).** Every relationship is canonical source-to-target
   (CR-2 R002). The inverse (`inverse:` in the registry) is a **query alias**, never a
   second authoring direction. Both directions are queryable; one is canonical.
3. **Full semantic descriptor (§11).** Every relationship declares: id, source types,
   target types, inverse, cardinality, transitive, symmetric, temporal, provenance, status.
4. **Cardinality (§13).** Declared per endpoint (`0..*` default; `1`, `0..1`, `1..*` where
   the semantics demand, e.g. `Assessment conducted-under Framework` = exactly one, A001).
   Machine-validated at conformance Level 2+.
5. **Categories (CR-2 + CR-6).** structural · realization · dependency · flow · serving ·
   execution · governance · information · assessment · transformation · traceability ·
   temporal (L, added CR-6).
6. **Temporal relationships (CR-6 §21/§22).** Instances may carry `valid_from`, `valid_to`,
   `status`, `recorded_at`. A *planned* edge must never be read as a current edge (T004).
7. **Derived relationships (§38).** Inferred edges (e.g. Agent → uses Tool → invokes Service
   → supports Capability ⟹ Agent indirectly-supports Capability) are computable but are
   **never written back** into the authoritative model unless explicitly requested, and then
   only with provenance (§39: derivedFrom + derivationRule).
