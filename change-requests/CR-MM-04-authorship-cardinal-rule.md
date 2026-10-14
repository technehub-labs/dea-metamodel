# CR-MM-04: Authorship Cardinal Rule (Org-Wide Propagation Slice)

| Field | Value |
|-------|-------|
| **CR** | CR-MM-04 |
| **Title** | Authorship Cardinal Rule (R1, R2) - Org-Wide Propagation Slice (dea-metamodel) |
| **Status** | Accepted (per user directive 2026-10-13) |
| **Layer** | Metamodel |
| **Depends on** | CR-BP-118 (org-wide authorship cardinal rule, main authority) |
| **Companion to** | CR-DEA-BC-34 (BC slice), CR-BO-03 (BO slice), CR-OU-03 (OU slice), CR-ECF-009 (MF slice) |
| **Author** | Emmanuel A. Otchere |
| **Date** | 2026-10-13 |

## 1. The cardinal rule (pinned)

Two cardinal rules from CR-BP-118 (org-wide authority) are propagated to this
repo (dea-metamodel):

- **R1 (Authorship-field cardinal rule)**: every authorship-bearing field must
  carry a value from the allowlist `{Emmanuel A. Otchere, TechNeHub Labs}`.
  Substring matches against the denylist
  `{Coder, Agent, Hermes, Claude, GPT, Cline, OpenAI, MiniMax, MiniMax-M3}` are
  blocking (AUT-001).
- **R2 (Named-role file cardinal rule)**: any file or field whose purpose is
  to name a person playing a named role must carry the canonical identity.

The rules are CR-level (immutable by a gate change) and governance-doc-level
(immutable by a code change).

## 2. The retro sweep (metamodel-repo scope)

13 hits in 13 change-request files, all swept. Two field shapes were used:

| Shape | Count | Files |
|---|---:|---|
| `**Author**` (bold, in table row) | 11 | CR-MM-01, CR-MM-01.1, CR-MM-02, CR-MM-PROC-01, CR-014, CR-015, CR-016, CR-ECF-CG-002, CR-ECF-CG-005, CR-ECF-CG-006, CR-MM-ECF-01 |
| `**Owner**` (bold, line metadata) | 0 | (none) |
| `Owner` (legacy bare-key, line metadata) | 2 | CR-MM-ECF-02, CR-MM-ECF-03 |

Total: 13 files, 13 textual replacements. 0 entity content changes; 0 id
changes; 0 cross-reference changes. The metamodel repo has 0 entity YAMLs,
0 CITATION.cff, and 0 catalog-research YAML; the field set is CR-doc
metadata only.

## 3. The gate (metamodel-repo, blocking)

- **AUT-001 (blocking)**: substring denylist against
  `{Coder, Agent, Hermes, Claude, GPT, Cline, OpenAI, MiniMax, MiniMax-M3}`.
- **AUT-002 (blocking)**: parent-block present but field empty.
- **AUT-003 (advisory, blocking under --strict)**: value not in allowlist.

Data-driven from `reconciliation/authorship-fields.yaml`. Fields registered
for the metamodel repo (per the field shape this repo uses):

| Path | file_glob | prefix_match |
|---|---|---|
| `**Owner**` | `change-requests/CR-*.md` | (default: exact) |
| `**Author**` | `change-requests/CR-*.md` | (default: exact) |
| `Owner` (legacy bare-key) | `change-requests/CR-*.md` | (default: exact) |

The bare-key `Owner` is metamodel-specific. CR-MM-ECF-02 and CR-MM-ECF-03
predate the org-wide bold-key convention and still carry `Owner: <value>`
(without bold). The registry enumerates this shape so the gate enforces
R1 on these files too. Future metamodel CRs should use the bold-key
form; the bare-key form is grandfathered for historical record.

## 4. CI wiring

A new workflow `.github/workflows/validate-authorship.yml` runs the gate
in `--strict` mode on every push and PR. The gate has its own per-repo
test module `tests/test_check_authorship.py` (21 tests, 21/21 pass on
the metamodel repo's tree).

## 5. Out of scope (CR-118c, deferred)

Prose-content occurrences of `Agent` / `Coder` / etc. in record `name` /
`definition` / `description` fields (not the authorship-metadata fields)
are inventoried for the 118c follow-on but not rewritten in this slice.

## 6. Test posture

- 21/21 `test_check_authorship` pass.
- Gate `--strict` exit 0 against the live metamodel tree.
- 0 D-004 violations across 4 new/modified files.

## 7. Carrier

This document. Plus the CHANGELOG `[Unreleased]` entry and the new
`.github/workflows/validate-authorship.yml` workflow.
