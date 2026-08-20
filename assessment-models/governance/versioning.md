# Versioning

The OpenDEA Assessment Metamodel uses **Semantic Versioning** (`MAJOR.MINOR.PATCH`) **plus explicit compatibility metadata**.

SemVer alone is insufficient. Adding a question can technically be a MINOR change while materially changing the statistical interpretation of the resulting score (CR-AM-01 §11 / §26). Therefore every released model version declares its compatibility properties explicitly via `compatibility: { backward_compatible, scoring_compatible, maturity_compatible, benchmark_compatible, result_compatible }` (see `schemas/compatibility.schema.json`).

## When to bump

| Bump | Use when | Score interpretation impact |
|------|---------|-----------------------------|
| **PATCH** | Typo, grammar, non-semantic clarification, additional explanatory evidence, metadata correction | **No** score interpretation may change |
| **MINOR** | Additional optional evidence, additional optional measure, new optional assessment question, new optional dimension, additive capability mapping | Existing result interpretation must remain valid; `backward_compatible: true` |
| **MAJOR** | Scoring changes, weighting changes, question meaning changes, dimension meaning changes, mandatory evidence changes, maturity interpretation changes, comparability changes, normalisation changes | A MAJOR version must never silently reinterpret historical results. The new version declares `backward_compatible: false` and historical results keep their original version reference. |

## Component versioning

Stable identifiers use the form:

```
dea:<kind>-<name>@<semver>
```

Example: `dea:capability-api-management@1.2.0`.

Each component is independently versioned:

- A `Capability` may be bumped independently of an `AssessmentModel` that references it.
- A `Measure` may be bumped independently of the `AssessmentModel` that uses it.
- An `AssessmentModel`'s version reflects the **composition** of all its components at release time.

## Lineage

Every released version records its lineage:

```yaml
lineage:
  previous_version: 1.0.0
  change_type: minor
  supersedes:
    - dea:assessment-technology@1.0.0
```

Historical AssessmentResults reference the exact version they were produced with. Bumping a model does not mutate historical results.

## CI compatibility matrix

The CI workflow generates a compatibility matrix on every release:

```
Model          Previous   Scoring   Maturity   Benchmark   Result
v1.0.0         —          —         —          —           —
v1.1.0         v1.0.0     yes       yes        yes         yes
v1.2.0         v1.1.0     yes       yes        no          yes
v2.0.0         v1.2.0     no        no         no          no
```

This makes model evolution transparent. Consumers can read the matrix to know what they can safely upgrade across.

## Reference

- CR-AM-01 §22, §25, §26, §27
- `schemas/common.schema.json#/$defs/version`
- `schemas/common.schema.json#/$defs/compatibility`
- `schemas/compatibility.schema.json`