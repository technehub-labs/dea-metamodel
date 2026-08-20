# Compatibility

The OpenDEA Assessment Metamodel requires **explicit compatibility metadata** on every model version. SemVer alone is insufficient because adding a question can change the statistical interpretation of a score (CR-AM-01 §11 / §26).

## The five compatibility properties

Every model version declares five boolean compatibility properties (see `schemas/common.schema.json#/$defs/compatibility`):

| Property | Meaning |
|----------|---------|
| `backward_compatible` | Existing results from the previous version can still be processed without change. |
| `scoring_compatible` | Scores from the previous version have the same interpretation. |
| `result_compatible` | Result structure is unchanged; results can flow through downstream unchanged. |
| `maturity_compatible` | Results from the previous version can be mapped to the same maturity interpretation. |
| `benchmark_compatible` | Results from the previous version may legitimately participate in cross-organisation benchmarking with this version. |

## Compatibility ≠ SemVer

SemVer describes *how* the change was made. Compatibility describes *what* the change preserves. They are independent:

- A PATCH may declare `benchmark_compatible: false` if a benchmark population's eligibility rules changed.
- A MAJOR may declare `backward_compatible: true` if the new version explicitly handles old result structures.

The compatibility metadata is the **declared ground truth** for whether two versions can interoperate. Never infer compatibility from semver alone.

## Benchmark eligibility

A result is benchmark-eligible only if **all** of the following are true:

1. The AssessmentModel version satisfies the benchmark's `required_assessment_model.version_range`.
2. The Scenario version satisfies the benchmark's `required_scenario.version_range`.
3. Every Capability version satisfies the benchmark's `required_capabilities.version_range`.
4. The AssessmentModel declares `benchmark_compatible: true`.
5. Compatibility metadata is consistent across all referenced model versions.

Otherwise, the result receives `benchmark_status: not-comparable` rather than being silently included (CR-AM-01 §28).

## Reference

- CR-AM-01 §25 (Comparability Contract)
- CR-AM-01 §27 (Assessment Compatibility Matrix)
- CR-AM-01 §28 (Benchmark Eligibility)
- `schemas/common.schema.json#/$defs/compatibility`
- `schemas/compatibility.schema.json`
- `examples/benchmark-eligibility.yaml`