# Cross-Repository Conformance

CR-ECF-CG-005 implementation. The cross-repo matrix + drift detector + consolidated report.

## What this is

| Artifact | Purpose | Location |
|---|---|---|
| Matrix | Current conformance posture of each repo | `conformance/matrix.yaml` |
| Drift detector | Validates invariants I1..I10 against current source | `scripts/detect_drift.py` |
| Report builder | Compiles the consolidated conformance report | `scripts/build_conformance_report.py` |
| Conformance report (human) | The headline artifact | `conformance/CONFORMANCE-REPORT-v0.1.md` |
| Conformance report (machine) | Tooling consumption | `conformance/conformance-report.json` |

## Invariants

The drift detector tests the 10 invariants from CR-ECF-CG-005 §3:

| # | Invariant | Detector check |
|---|---|---|
| I1 | Domain Identity | every canonical reference's `domain` is in the canonical PascalCase enum |
| I2 | Stage Identity | every canonical reference's `stage` is in the canonical PascalCase enum |
| I3 | Coordinate Identity | (domain, stage) pair maps to one identifier |
| I4 | Coordinate Cardinality | 7 x 7 = 49 coordinates are derivable |
| I5 | Contextualization | downstream uses `ecfConformance` as a separate field, not by redefining Domain/Stage |
| I6 | Identity Preservation | capability id (dea:capability-...) is independent of any ECF Coordinate |
| I7 | No Cell Population | no repository assumes all 49 coordinates must be populated |
| I8 | Terminology | "Enterprise Concept Framework" is the only expansion |
| I9 | Identifier Resolution | all downstream identifiers match the canonical lowerCamelCase pattern |
| I10 | Version Compatibility | all consumers declare `contractVersion=1.0.0` |

## How to use

### Build a report

```bash
python3 scripts/build_conformance_report.py
```

Writes `conformance/CONFORMANCE-REPORT-v0.1.md` and `conformance/conformance-report.json`.

### Check for drift

```bash
python3 scripts/detect_drift.py          # soft warnings only; exit 0 if no hard failures
python3 scripts/detect_drift.py --strict # any warning fails the gate
```

### Refresh the matrix

The matrix is currently hand-curated in `conformance/matrix.yaml`. Future automation: derive it from the report JSON; do not hand-edit both.

## Current posture

Run `build_conformance_report.py` and read `CONFORMANCE-REPORT-v0.1.md` for the headline. The first matrix records the post-tranche posture: all three consumer repos are CONFORMANT-WITH-EXTENSION against `dea:ecf@1.0.0` (contract version 1.0.0).

## Enforcement

CG-006 wires the drift detector + report builder into CI. The metamodel-side enforcement workflow runs both scripts on every PR. Consumer-repo CI hooks (to be added in CG-006 implementation PR #2) run the same scripts in their own pipelines.

## Out-of-scope flags

- `dea-catalog-business-capabilities/README.md` and `docs/FOUNDATIONS.md` mention "Enterprise Composition Framework" (a non-canonical expansion). Pre-existing user content; not introduced by this PR. Recorded as a soft drift warning.