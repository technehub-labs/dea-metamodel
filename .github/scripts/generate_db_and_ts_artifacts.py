#!/usr/bin/env python3
"""Generate the sqlite and TypeScript artefacts for every declared entity.

Why this exists
---------------
Every entity in `metamodel/dea-metamodel.yaml` declares four artifacts. Two
were verified historically (json_schema by validate_json_schemas.py, pydantic by
a git-diff gate). The other two were declared for over a hundred entities each
and nothing checked that the named table or interface actually existed, so an
entity could declare an artifact that was never produced and still pass CI.

This script closes that gap by deriving both artifacts from the canonical JSON
Schema of each entity. Deriving rather than hand-writing is the point: the
column set, the CHECK constraints, the field optionality, and the union types
then cannot drift from `metamodel/dea-metamodel.yaml`, because the metamodel is
the only input.

Deterministic. Running it twice produces byte-identical output, so the drift
gate's STALE check stays meaningful.

Usage
-----
    python3 .github/scripts/generate_db_and_ts_artifacts.py
    python3 .github/scripts/generate_db_and_ts_artifacts.py --check
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parent.parent.parent
METAMODEL = BASE / "metamodel" / "dea-metamodel.yaml"
SCHEMA = BASE / "sqlite" / "schema.sql"
TS = BASE / "typescript" / "src" / "interfaces.ts"

# Shared identity and lifecycle fields carried by every entity. Each is already
# represented by the entities table (or is not tabular), so repeating them as
# columns would duplicate storage and diverge from the registry.
SHARED = {
    "id", "type", "name", "description", "version", "lifecycle_status",
    "external_references", "relationships", "metadata",
}

# SQLite reserved words. A property colliding with one must be quoted or the
# schema does not parse; BusinessProcess.trigger and Escalation.trigger are the
# live cases.
RESERVED = {
    "all", "and", "as", "asc", "between", "by", "case", "cast", "check",
    "collate", "column", "commit", "conflict", "constraint", "create", "cross",
    "current_date", "current_time", "current_timestamp", "default",
    "deferrable", "delete", "desc", "distinct", "drop", "else", "escape",
    "except", "exclusive", "exists", "for", "foreign", "from", "full", "glob",
    "group", "having", "in", "index", "insert", "intersect", "into", "is",
    "join", "key", "left", "like", "limit", "match", "natural", "not", "null",
    "of", "offset", "on", "or", "order", "plan", "primary", "query", "raise",
    "references", "regexp", "reindex", "rename", "replace", "right",
    "rollback", "select", "set", "table", "temp", "temporary", "then", "to",
    "transaction", "trigger", "union", "unique", "update", "using", "vacuum",
    "values", "view", "when", "where", "with",
}

RULE = "-- " + "\u2550" * 70
TS_RULE = "// " + "\u2550" * 70
BANNER_MARKER = RULE + "\n-- Generated entity tables."
TS_BANNER_MARKER = TS_RULE + "\n// Generated entity interfaces."
BANNER = (
    RULE + "\n"
    "-- Generated entity tables.\n"
    "--\n"
    "-- Column names and CHECK constraints are derived from each entity's canonical\n"
    "-- JSON Schema (properties and enums), so they cannot drift from\n"
    "-- metamodel/dea-metamodel.yaml. Regenerate rather than hand-edit:\n"
    "--     python3 .github/scripts/generate_db_and_ts_artifacts.py\n"
    "-- The artifact drift gate (.github/scripts/validate_artifacts.py) enforces that\n"
    "-- every entity's declared table exists.\n"
    + RULE + "\n"
)

DASHES = {
    "–": "-",
    "—": ";",
    "⸻": "; ",
    "…": "...",
    " ": " ",
    "→": "->",
    "’": "'",
    "“": '"',
    "”": '"',
}


def scrub_text(value: str) -> str:
    """Normalise punctuation copied from canonical descriptions.

    The JSON Schemas contain em-dashes, non-breaking spaces, and typographic
    quotes. Propagating them verbatim injects D-004 violations into generated
    comments: interfaces.ts had zero D-004 hits before this slice and six after,
    every one of them inherited from a schema description.

    D-004 forbids em-dashes and U+2E3B, so an em-dash becomes the semicolon
    divider the house style already uses.
    """
    out = value
    for bad, good in DASHES.items():
        out = out.replace(bad, good)
    return re.sub(r"[ \t]+", " ", out).strip()


def quote(name: str) -> str:
    return f'"{name}"' if name.lower() in RESERVED else name


def base_type(schema: dict) -> str:
    t = schema.get("type")
    if isinstance(t, list):
        t = t[0] if t else "string"
    return t or "string"


def sql_column(prop: str, schema: dict) -> str:
    t = base_type(schema)
    ident = quote(prop)
    if t == "string":
        if "enum" in schema:
            vals = ",".join(
                "'" + str(v).replace("'", "''") + "'" for v in schema["enum"]
            )
            return f"TEXT CHECK({ident} IN ({vals}))"
        return "TEXT"
    if t in ("integer", "number"):
        return "REAL"
    if t == "boolean":
        return f"INTEGER CHECK({ident} IN (0,1))"
    if t == "array":
        return "TEXT"
    if t == "object":
        return "TEXT"
    return "TEXT"


def ts_type(prop: str, schema: dict, indent: int = 0) -> str:
    t = base_type(schema)
    if "enum" in schema:
        return " | ".join("'" + str(v) + "'" for v in schema["enum"])
    if t == "string":
        return "string"
    if t in ("integer", "number"):
        return "number"
    if t == "boolean":
        return "boolean"
    if t == "array":
        item = schema.get("items") or {}
        return f"{ts_type(prop, item)}[]"
    if t == "object":
        return "Record<string, unknown>"
    return "unknown"


def load() -> tuple[list[dict], dict]:
    metamodel = yaml.safe_load(METAMODEL.read_text())
    return metamodel["entities"], metamodel


def entity_schema(entity: dict) -> dict | None:
    """Canonical JSON Schema for an entity, or None when not declared."""
    path = (entity.get("artifacts") or {}).get("json_schema")
    if not path:
        return None
    full = BASE / path
    return json.loads(full.read_text()) if full.exists() else None


def build_sql(entities: list[dict], existing: str) -> tuple[str, list[str], list[str]]:
    present = set(
        re.findall(
            r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z_][A-Za-z0-9_]*)",
            existing,
            re.I,
        )
    )
    declared = {
        e["artifacts"]["sqlite_table"]
        for e in entities
        if (e.get("artifacts") or {}).get("sqlite_table")
    }
    blocks: list[str] = []
    added: list[str] = []
    for entity in entities:
        table = (entity.get("artifacts") or {}).get("sqlite_table")
        if not table or table in present:
            continue
        schema = entity_schema(entity)
        if schema is None:
            continue
        props = schema.get("properties", {})
        columns = [
            "    entity_id           TEXT PRIMARY KEY "
            "REFERENCES entities(id) ON DELETE CASCADE"
        ]
        for prop in (p for p in props if p not in SHARED):
            columns.append(f"    {prop:20s} {sql_column(prop, props[prop])}")
        # Commas BETWEEN columns. Omitting them yields a schema that looks
        # correct in a diff but does not parse.
        blocks.append(
            f"CREATE TABLE IF NOT EXISTS {table} (\n" + ",\n".join(columns) + "\n);\n"
        )
        present.add(table)
        added.append(table)

    missing = sorted(t for t in declared if t not in present)
    if not blocks:
        return existing, added, missing

    # Drop any previously appended banner, then emit exactly one at the end.
    body = existing.split(BANNER_MARKER)[0].rstrip("\n")
    return body + "\n\n" + BANNER + "\n" + "\n".join(blocks), added, missing


def build_ts(entities: list[dict], existing: str) -> tuple[str, list[str]]:
    exported = set(
        re.findall(r"export\s+(?:interface|type)\s+([A-Za-z_][A-Za-z0-9_]*)", existing)
    )
    blocks: list[str] = []
    added: list[str] = []
    names: list[str] = []
    for entity in entities:
        name = entity["id"].split(":", 1)[-1]
        declared = (entity.get("artifacts") or {}).get("ts_interface")
        if not declared or name in exported:
            continue
        schema = entity_schema(entity)
        if schema is None:
            continue
        props = schema.get("properties", {})
        required = set(schema.get("required", []))
        lines = [f"export interface {name} extends BaseEntity {{", f"  type: '{name}';"]
        for prop in (p for p in props if p not in SHARED):
            optional = "" if prop in required else "?"
            comment = ""
            if props[prop].get("description"):
                text = scrub_text(str(props[prop]["description"]).replace("\n", " "))
                comment = f"  // {text}\n"
            lines.append(f"{comment}  {prop}{optional}: {ts_type(prop, props[prop])};")
        lines.append("}")
        blocks.append("\n".join(lines))
        added.append(name)
        names.append(name)

    if not blocks:
        return existing, names

    # Strip any previously written banner before appending, so repeated runs
    # do not accumulate a fresh header on every invocation. Appending to
    # `existing` unconditionally makes the generator non-idempotent and the
    # STALE check in the drift gate can never go quiet.
    body = existing.split(TS_BANNER_MARKER)[0].rstrip("\n")
    banner = (
        TS_RULE + "\n"
        "// Generated entity interfaces.\n"
        "//\n"
        "// Field names, optionality, and union types are derived from each\n"
        "// entity's canonical JSON Schema (properties, required, enums), so they\n"
        "// cannot drift from metamodel/dea-metamodel.yaml. Regenerate rather\n"
        "// than hand-edit:\n"
        "//     python3 .github/scripts/generate_db_and_ts_artifacts.py\n"
        + TS_RULE + "\n\n"
    )
    return body + "\n" + banner + "\n\n".join(blocks) + "\n", names


def register_in_aggregates(existing: str, names: list[str]) -> str:
    """Add generated interface names to the AnyEntity union and ENTITY_TYPES.

    Without this the interfaces compile but are unreachable through the union
    consumers actually use, so AnyEntity silently omits them. 90 exported
    interfaces were already in that state before this slice: Entity,
    Stakeholder, Actor and 87 others were never registered.

    Line-based rather than regex-block-based: the union and the array have no
    terminating token, so a block regex is guesswork about where each ends.
    """
    if not names:
        return existing
    lines = existing.split("\n")
    union = re.compile(r"^\s*\|\s*(\w+)\s*$")
    quoted = re.compile(r"^\s*'([A-Za-z_][A-Za-z0-9_]*)',\s*$")

    i = 0
    while i < len(lines) and not lines[i].startswith("export type AnyEntity"):
        i += 1
    if i < len(lines):
        i += 1
        have = set()
        last = i
        while i < len(lines):
            m = union.match(lines[i])
            if not m:
                break
            have.add(m.group(1))
            last = i
            i += 1
        add = [n for n in names if n not in have]
        if add:
            lines[last + 1 : last + 1] = [f"  | {n}" for n in add]

    i = 0
    while i < len(lines) and not lines[i].startswith("export const ENTITY_TYPES"):
        i += 1
    if i < len(lines):
        i += 1
        have_e = set()
        last = i
        while i < len(lines):
            m = quoted.match(lines[i])
            if not m:
                break
            have_e.add(m.group(1))
            last = i
            i += 1
        add_e = [n for n in names if n not in have_e]
        if add_e:
            lines[last + 1 : last + 1] = [f"  '{n}'," for n in add_e]

    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--check",
        action="store_true",
        help="report drift without writing (exit 1 if regeneration is needed)",
    )
    args = ap.parse_args()

    entities, _ = load()
    sql, sql_added, sql_missing = build_sql(entities, SCHEMA.read_text())
    ts, ts_added = build_ts(entities, TS.read_text())
    # Register every DECLARED interface, not only the ones generated in this
    # run. Restricting to ts_added would leave entities whose interface already
    # existed but was never added to the union permanently absent, which is how
    # Entity, Stakeholder, Actor and 87 others were unreachable.
    ts = register_in_aggregates(
        ts,
        [
            e["id"].split(":", 1)[-1]
            for e in entities
            if (e.get("artifacts") or {}).get("ts_interface")
        ],
    )

    print(f"entities        : {len(entities)}")
    print(f"sqlite tables   : +{len(sql_added)} generated, {len(sql_missing)} still missing")
    if sql_missing:
        print(f"                  {sql_missing}")
    print(f"ts interfaces   : +{len(ts_added)} generated")

    if args.check:
        stale = (sql != SCHEMA.read_text()) or (ts != TS.read_text())
        print("DRIFT: regeneration required" if stale else "clean")
        return 1 if stale else 0

    if sql_added:
        SCHEMA.write_text(sql)
    # Written unconditionally: a run that generates no new interfaces must
    # still be able to repair the AnyEntity union and ENTITY_TYPES registry.
    # Guarding this on ts_added made that repair unreachable after the first
    # successful generation.
    TS.write_text(ts)
    print("written")
    return 0


if __name__ == "__main__":
    sys.exit(main())