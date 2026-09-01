# CR-ECF-CG-006: Automated Conformance Enforcement

| Field | Value |
|-------|-------|
| **CR** | CR-ECF-CG-006 |
| **Title** | Automated Conformance Enforcement |
| **Status** | Proposed |
| **Type** | CI / Validation |
| **Implements** | CR-ECF-CG-005 |
| **Scope** | ECF-consuming repositories |
| **Author** | Coder (for eaojnr) |
| **Date** | 2026-09-01 |

I would add one final CR rather than leaving the gate as a manual review.

## 1. Purpose

Automate the ECF Conformance Gate so that semantic drift is detected during repository change.

## 2. Validation Pipeline

The implementation shall provide:

Canonical ECF Specification
          |
          V
      Load Contract
          |
          V
     Validate Schema
          |
          V
   Validate Identifiers
          |
          V
   Validate References
          |
          V
 Validate Terminology
          |
          V
 Validate Invariants
          |
          V
 Generate Report
          |
          V
       PASS / FAIL

## 3. Mandatory CI Checks

CI shall fail when:

- an ECF Domain is invalid;
- an ECF Stage is invalid;
- a Coordinate is malformed;
- a canonical identifier cannot be resolved;
- a local conflicting ECF definition is introduced;
- a prohibited semantic interpretation is detected;
- a required conformance declaration is missing;
- an incompatible ECF contract version is declared.

## 4. Pull Request Behavior

Changes affecting ECF references shall trigger conformance validation.

The validation output shall identify:

repository
file
artifact
rule
expected
actual
severity

## 5. Conformance Report

The generated report shall be suitable for:

- human review;
- CI artifacts;
- machine consumption;
- portfolio-level status reporting.

## 6. Acceptance Criteria

- [ ] CI validation executes automatically.
- [ ] ECF contract violations fail the gate.
- [ ] Validation evidence is retained.
- [ ] Cross-repository references are checked.
- [ ] Conformance status is reproducible.
- [ ] Contract version is reported.

## 7. Definition of Done (this proposal PR)

One file (this CR verbatim against the source tranche). Ships alongside CR-ECF-CG-005 in this same proposal PR. Implementation PR (the metamodel-side enforcement workflow + the consumer-repo hooks) ships on subsequent acceptance.

## 8. References

CR-ECF-CG-001 (gate definition); CR-ECF-CG-005 (cross-repo conformance, this batch).