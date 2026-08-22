# Compatibility

The OpenDEA Assessment Metamodel requires **explicit compatibility metadata** on every model version. SemVer alone is insufficient because adding a question can change the statistical interpretation of a score (CR-AM-01 §11 / §26).

## The six compatibility axes

Every model version declares six compatibility axes (see `schemas/common.schema.json#/$defs/compatibility`):

| Property | Meaning |
|----------|---------|
| `schema` | Existing validators accept the document shape. |
| `semantic` | Existing constructs retain their meaning. |
| `scoring` | Scores retain the same interpretation. |
| `maturity` | Results retain the same maturity interpretation. |
| `result` | Result structure remains interoperable. |
| `benchmark` | Results may participate in cross-organisation benchmarking. |

## Compatibility ≠ SemVer

SemVer describes *how* the change was made. Compatibility describes *what* the change preserves. They are independent:

- A PATCH may declare `benchmark: incompatible` if benchmark eligibility rules changed.
- A MAJOR may declare `schema: compatible` if the new version explicitly handles old result structures.

The compatibility metadata is the **declared ground truth** for whether two versions can interoperate. Never infer compatibility from semver alone.

## Benchmark eligibility

A result is benchmark-eligible only if **all** of the following are true:

1. The AssessmentModel version satisfies the benchmark's `required_assessment_model.version_range`.
2. The Scenario version satisfies the benchmark's `required_scenario.version_range`.
3. Every Capability version satisfies the benchmark's `required_capabilities.version_range`.
4. The result's compatibility declaration carries `benchmark: compatible` when eligibility is established.
5. The versioned result lineage and eligibility references are consistent.

Otherwise, the result carries `benchmark_eligibility.status: not-comparable` rather than being silently included (CR-AM-03 §22).

## Reference

- CR-AM-01 §25 (Comparability Contract)
- CR-AM-01 §27 (Assessment Compatibility Matrix)
- CR-AM-01 §28 (Benchmark Eligibility)
- `schemas/common.schema.json#/$defs/compatibility`
- `schemas/compatibility.schema.json`
- `examples/benchmark-eligibility.yaml`