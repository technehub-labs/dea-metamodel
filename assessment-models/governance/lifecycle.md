# Lifecycle

Every model in the OpenDEA Assessment Metamodel passes through a defined lifecycle. The full set of states is recorded in `vocabulary/lifecycle-status.yaml`; this document explains the rationale and the rules.

## States

```
draft → experimental → alpha → beta → stable → deprecated → retired
```

| State | Meaning |
|-------|---------|
| **draft** | Initial authoring. Not yet suitable for any consumer. |
| **experimental** | Posted for early feedback. May change without notice. |
| **alpha** | API may still change. Known to be incomplete. |
| **beta** | API stabilising. Backward-compat breakage still permitted. |
| **stable** | Production-ready. Backward-compat breakage requires a MAJOR version bump and a deprecation period. |
| **deprecated** | Still valid but slated for retirement. Consumers should migrate. |
| **retired** | No longer valid for new work. Definition MUST remain available. |

## Why `retired` is distinct from `deleted`

A retired model's definition **must be retained as long as any historical AssessmentResult references it**. Tooling must refuse to delete a model whose id appears in any historical result.

This is essential for the immutability of historical results (CR-AM-01 §23 / AC-07). If a model is referenced by `dea:result:2026:000184` and is then deleted, that result can no longer be interpreted.

## Default state for new models

Newly created models start in `draft`. Moving to `experimental`, `alpha`, `beta`, `stable` is an explicit action recorded in the CHANGELOG.

## Deprecation period

A model moving from `stable` to `deprecated` enters a minimum deprecation period before retirement. The period depends on the model's reach:

| Reach | Minimum deprecation period |
|-------|----------------------------|
| Internal to one org | 1 minor version |
| Internal to multiple orgs | 1 minor version, with migration guide |
| Cross-organisation (referenced by `dea-catalog-*`) | 1 MAJOR version cycle (typically 2-3 minor versions) |

After the deprecation period, the model may move to `retired`.

## Authority and ownership

Every model declares an `owner`. The owner is responsible for:

1. Versioning decisions (when to bump)
2. Compatibility declarations
3. Deprecation notices
4. Retirement timing
5. Retention of the retired definition

If the owner role is vacated, ownership passes to the model's steward (or, failing that, the assessment-tools catalog owner).

## Reference

- CR-AM-01 §42 (Governance)
- CR-AM-01 §43 (Model Lifecycle — including the retired ≠ deleted rule)
- `vocabulary/lifecycle-status.yaml`