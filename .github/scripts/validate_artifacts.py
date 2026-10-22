#!/usr/bin/env python3
"""Verify every declared generated artifact is present and current.

Every entity in metamodel/dea-metamodel.yaml declares four artifacts under
`artifacts:`:

    json_schema   a per-entity JSON Schema file
    pydantic_model a generated pydantic module
    sqlite_table  a table name that must exist in sqlite/schema.sql
    ts_interface  the shared TypeScript interface module

This script closes the gap where only `json_schema` and `pydantic_model` were
verified. `sqlite_table` and `ts_interface` were declared for 137 and 135
entities respectively but nothing checked that the named table or interface
actually existed, so an entity could declare an artifact that was never
produced and still pass CI.

Three distinct failure classes are reported separately, because they have
different causes and different fixes:

    MISSING   the artifact was declared and never produced. Fix: produce it.
    STALE     a generator exists and re-running it changed the output.
              Fix: commit the regenerated output in the same PR.
    ABSENT    the artifact kind is declared but the target has no such
              artifact at all. Fix: produce it or amend the declaration.

The gate RATCHETS rather than failing on absolute counts. The repository
carries a pre-existing backlog of declared-but-never-produced artifacts. Failing
on every finding would mean permanently red CI, which gets disabled and then
protects nothing. Instead the current counts are recorded in
.github/artifact-drift-baseline.json and the gate fails only when a count
INCREASES. The backlog can shrink; it can never grow.

Usage:
    python3 .github/scripts/validate_artifacts.py            # enforce the ratchet
    python3 .github/scripts/validate_artifacts.py --report   # report only, exit 0
    python3 .github/scripts/validate_artifacts.py --update-baseline

Exit codes:
    0  no regression (backlog within baseline)
    1  a finding count exceeded its baseline, or no baseline exists
    2  the script could not read its inputs (a distinct, louder failure)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
METAMODEL = BASE / "metamodel" / "dea-metamodel.yaml"
SQLITE_SCHEMA = BASE / "sqlite" / "schema.sql"
TS_INTERFACES = BASE / "typescript" / "src" / "interfaces.ts"
BASELINE = BASE / ".github" / "artifact-drift-baseline.json"

# Generators and the tree each one owns. Each is run before and after a file
# snapshot so staleness is detected by CONTENT, never by mtime.
GENERATORS: list[tuple[str, tuple[str, ...]]] = [
    (".github/scripts/generate_registry.py", ("metamodel/registry/",)),
    (".github/scripts/generate_specification.py", ("specification/",)),
    (".github/scripts/generate_pydantic.py", ("pydantic/",)),
]


def snapshot(paths: tuple[str, ...]) -> dict[str, str]:
    """Content hashes for every file under the given repo-relative paths."""
    import hashlib

    out: dict[str, str] = {}
    for rel in paths:
        root = BASE / rel
        if not root.exists():
            continue
        for f in sorted(root.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts:
                out[str(f.relative_to(BASE))] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def run_generator(script: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, script], capture_output=True, text=True, cwd=BASE
    )
    return proc.returncode, (proc.stderr or proc.stdout or "").strip()


def check_stale() -> list[str]:
    """Re-run every generator and report which owned trees changed."""
    findings: list[str] = []
    for script, trees in GENERATORS:
        before = snapshot(trees)
        code, err = run_generator(script)
        if code != 0:
            findings.append(f"{script} exited {code}: {err[:200]}")
            continue
        after = snapshot(trees)
        if before == after:
            continue
        added = sorted(set(after) - set(before))
        removed = sorted(set(before) - set(after))
        changed = sorted(k for k in set(before) & set(after) if before[k] != after[k])
        detail = []
        if changed:
            detail.append(f"{len(changed)} changed")
        if added:
            detail.append(f"{len(added)} added")
        if removed:
            detail.append(f"{len(removed)} removed")
        findings.append(
            f"{script} produced stale output in {', '.join(trees)} "
            f"({'; '.join(detail)}). Commit the regenerated files."
        )
    return findings


def check_sqlite(entities: list[dict]) -> tuple[list[str], dict]:
    """Every declared sqlite_table must exist as a CREATE TABLE in schema.sql."""
    if not SQLITE_SCHEMA.exists():
        return [f"{SQLITE_SCHEMA.relative_to(BASE)} does not exist"], {}
    sql = SQLITE_SCHEMA.read_text(errors="ignore")
    present = set(
        re.findall(
            r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z_][A-Za-z0-9_]*)",
            sql,
            re.IGNORECASE,
        )
    )
    missing = []
    declared = set()
    for e in entities:
        table = (e.get("artifacts") or {}).get("sqlite_table")
        if not table:
            continue
        declared.add(table)
        if table not in present:
            missing.append(f"{e['id']} declares sqlite_table '{table}' but no such table exists")
    return missing, {"declared": len(declared), "present": len(declared & present)}


def check_typescript(entities: list[dict]) -> tuple[list[str], dict]:
    """Every declared ts_interface target must exist and export a name per entity."""
    if not TS_INTERFACES.exists():
        return [f"{TS_INTERFACES.relative_to(BASE)} does not exist"], {}
    text = TS_INTERFACES.read_text(errors="ignore")
    exported = set(
        re.findall(r"export\s+(?:interface|type)\s+([A-Za-z_][A-Za-z0-9_]*)", text)
    )
    missing_files = []
    missing_ifaces = []
    seen_targets: set[str] = set()
    for e in entities:
        rel = (e.get("artifacts") or {}).get("ts_interface")
        if not rel:
            continue
        if rel not in seen_targets:
            seen_targets.add(rel)
            if not (BASE / rel).exists():
                missing_files.append(
                    f"{e['id']} declares ts_interface '{rel}' but that file does not exist"
                )
        # The convention is that the exported interface name matches the entity
        # name, or the entity's class_alias where one is assigned.
        name = e["id"].split(":", 1)[-1]
        if name not in exported:
            alias = e.get("class_alias")
            if not (alias and alias in exported):
                missing_ifaces.append(
                    f"{e['id']} has no exported TypeScript interface (looked for '{name}')"
                )
    return missing_files + missing_ifaces, {
        "declared_files": len(seen_targets),
        "exported_names": len(exported),
    }


def check_file_backed(entities: list[dict], kind: str) -> list[str]:
    """json_schema and pydantic_model are file paths; each must exist."""
    missing = []
    for e in entities:
        rel = (e.get("artifacts") or {}).get(kind)
        if not rel:
            continue
        if not (BASE / rel).exists():
            missing.append(f"{e['id']} declares {kind} '{rel}' but that file does not exist")
    return missing


def load_baseline() -> dict:
    """The recorded finding counts the gate will not let grow.

    A gate that fails on every finding is a gate that gets disabled. The
    repository already carries a substantial backlog of declared-but-never-
    produced artifacts (32 tables and ~84 interfaces predate the Metric
    programme). This gate therefore RATCHETS: it fails when the finding count
    increases above the recorded baseline, and reports the existing backlog
    without blocking. Backlog can shrink, never grow.
    """
    if not BASELINE.exists():
        return {}
    return json.loads(BASELINE.read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="report without failing")
    ap.add_argument(
        "--update-baseline",
        action="store_true",
        help="record the current counts as the new baseline (use only when the "
        "backlog is deliberately re-baselined, never to silence new drift)",
    )
    args = ap.parse_args()

    try:
        import yaml
    except ImportError:
        print("ERROR: pyyaml is required to read the canonical source", file=sys.stderr)
        return 2

    if not METAMODEL.exists():
        print(f"ERROR: {METAMODEL} does not exist", file=sys.stderr)
        return 2

    entities = yaml.safe_load(METAMODEL.read_text())["entities"]

    stale = check_stale()
    missing_schema = check_file_backed(entities, "json_schema")
    missing_pydantic = check_file_backed(entities, "pydantic_model")
    missing_sqlite, sqlite_stats = check_sqlite(entities)
    missing_ts, ts_stats = check_typescript(entities)

    sections = [
        ("STALE generator output", stale),
        ("MISSING json_schema", missing_schema),
        ("MISSING pydantic_model", missing_pydantic),
        ("MISSING sqlite_table", missing_sqlite),
        ("MISSING ts_interface", missing_ts),
    ]

    counts = {label: len(v) for label, v in sections}
    total = sum(counts.values())

    print("Artifact drift report")
    print("=" * 72)
    for label, findings in sections:
        status = "OK" if not findings else f"{len(findings)} FINDING(S)"
        print(f"\n{label}: {status}")
        for f in findings[:12]:
            print(f"  - {f}")
        if len(findings) > 12:
            print(f"  ... and {len(findings) - 12} more")
    print("\n" + "=" * 72)
    print(
        f"sqlite: {sqlite_stats.get('present', 0)}/{sqlite_stats.get('declared', 0)} declared tables present"
    )
    print(
        f"typescript: {ts_stats.get('exported_names', 0)} exported interfaces across "
        f"{ts_stats.get('declared_files', 0)} declared file(s)"
    )
    print(f"TOTAL FINDINGS: {total}")

    if args.update_baseline:
        BASELINE.write_text(json.dumps(counts, indent=2, sort_keys=True) + "\n")
        print(f"\nBaseline written to {BASELINE.relative_to(BASE)}")
        return 0

    baseline = load_baseline()
    if not baseline:
        if args.report:
            print("\nNo baseline recorded; reporting only.")
            return 0
        print(
            "\nERROR: no artifact-drift baseline recorded. Run with --update-baseline\n"
            "to record the current backlog, then commit the baseline file.",
            file=sys.stderr,
        )
        return 1

    regressions = []
    for label, findings in sections:
        base = baseline.get(label, 0)
        if len(findings) > base:
            regressions.append((label, base, len(findings)))

    if regressions:
        print("\n" + "=" * 72)
        print("ARTIFACT DRIFT REGRESSION")
        for label, base, now in regressions:
            print(f"  {label}: baseline {base} -> now {now} (+{now - base})")
        print(
            "\nNew drift was introduced. Produce the artifact, or amend the "
            "declaration in metamodel/dea-metamodel.yaml.\n"
            "If this is a deliberate re-baseline, say so explicitly; do not "
            "silently update the baseline."
        )
        return 1

    if total:
        print(
            f"\nRatchet OK: no finding exceeds its recorded baseline.\n"
            f"{total} findings remain against a baseline of {sum(baseline.values())}; "
            "the backlog is pre-existing and may shrink."
        )
    else:
        print("\nAll artifacts present and current.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
