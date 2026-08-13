#!/usr/bin/env python3
"""Generate pydantic/ models from schemas/entities/*.json + metamodel.yaml.

Closes the v0.1.0-alpha drift where metamodel.yaml referenced pydantic/
modules that did not exist (ADR-0002 execution, decision 4b). Each entity
listed in metamodel.yaml with a `pydantic_model` path gets a generated
module; `pydantic/entity.py` holds the shared BaseEntity.

Generation is deterministic — same schemas always produce byte-identical
output. CI verifies this (ci.yml regenerates and diffs).

Run: python3 .github/scripts/generate_pydantic.py
"""
import json
import re
import sys
from pathlib import Path

import yaml

BASE = Path(__file__).parent.parent.parent
SCHEMA_DIR = BASE / "schemas" / "entities"
OUT_DIR = BASE / "pydantic"
INDEX = BASE / "metamodel.yaml"

HEADER = '''"""{title} — generated from schemas/entities/{schema_file}.

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""
'''

BASE_PY = '''"""Abstract root for all DEA metamodel entities (generated).

Do not edit manually — regenerate with:
    python3 .github/scripts/generate_pydantic.py
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class RelationshipInstance(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    description: Optional[str] = None
    weight: Optional[float] = None
    provenance: Optional[str] = None
    bidirectional: Optional[bool] = None


class EntityMetadata(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    status: Optional[str] = None


class Entity(BaseModel):
    """Abstract root type for all metamodel entities."""

    id: str = Field(pattern=r"^[a-z][a-z0-9-]*:[a-z0-9-]+$")
    type: str
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    version: str = Field(pattern=r"^\\d+\\.\\d+\\.\\d+$")
    tags: Optional[list[str]] = None
    relationships: Optional[list[RelationshipInstance]] = None
    metadata: Optional[EntityMetadata] = None
'''


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def py_type(prop: dict, required: bool) -> str:
    """Map a JSON Schema property to a Python type annotation."""
    t = prop.get("type")
    if "const" in prop:
        base = f"Literal[{prop['const']!r}]"
    elif "enum" in prop and t == "string":
        base = "Literal[" + ", ".join(repr(v) for v in prop["enum"]) + "]"
    elif t == "string":
        base = "str"
    elif t == "number":
        base = "float"
    elif t == "integer":
        base = "int"
    elif t == "boolean":
        base = "bool"
    elif t == "array":
        base = "list[str]"
    elif t == "object":
        base = "dict[str, Any]"
    elif isinstance(t, list):  # e.g. ["number", "string"]
        base = "Any"
    else:
        base = "Any"
    return base if required else f"Optional[{base}]"


def gen_module(name: str, schema_path: Path) -> str:
    schema = json.loads(schema_path.read_text())
    required = set(schema.get("required", []))
    props = schema.get("properties", {})

    lines = [HEADER.format(title=schema.get("title", name), schema_file=schema_path.name)]
    lines.append("from __future__ import annotations\n")
    lines.append("from typing import Any, Literal, Optional\n")
    lines.append("from pydantic import Field\n")
    # NOTE: top-level import (not relative) — this directory is named
    # `pydantic/` per metamodel.yaml, which shadows the pydantic library
    # when the REPO ROOT is on sys.path. Consumers must put the pydantic/
    # directory itself on sys.path and import these as top-level modules.
    lines.append("from entity import Entity, EntityMetadata, RelationshipInstance\n")
    lines.append("\n")

    desc = schema.get("description", "")
    lines.append(f"class {name}(Entity):")
    if desc:
        lines.append(f'    """{desc}"""\n')
    skip = {"id", "name", "description", "version", "tags", "relationships", "metadata"}
    any_field = False
    for pname, prop in props.items():
        if pname in skip:
            continue
        ann = py_type(prop, pname in required)
        if pname in required:
            lines.append(f"    {pname}: {ann}")
        else:
            lines.append(f"    {pname}: {ann} = None")
        if prop.get("description"):
            d = prop["description"].replace('"""', '\\"\\"\\"')
            lines.append(f'    """{d}"""')
        any_field = True
    if not any_field:
        lines.append("    pass")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "entity.py").write_text(BASE_PY)

    index = yaml.safe_load(INDEX.read_text())
    written = []
    for entry in index.get("entities", []):
        name = entry["name"]
        schema_rel = entry.get("schema")
        model_rel = entry.get("pydantic_model")
        if not model_rel:
            continue
        if name == "Entity":
            continue  # handled by BASE_PY
        schema_path = BASE / schema_rel if schema_rel else None
        if not schema_path or not schema_path.exists():
            print(f"WARNING: {name}: schema {schema_rel} missing — generating stub", file=sys.stderr)
            content = HEADER.format(title=name, schema_file="(missing)") + \
                "from .entity import Entity\n\n\nclass " + name + "(Entity):\n    pass\n"
        else:
            content = gen_module(name, schema_path)
        out = BASE / model_rel
        out.parent.mkdir(exist_ok=True)
        out.write_text(content)
        written.append(model_rel)

    init = '"""DEA metamodel pydantic models (generated)."""\n'
    (OUT_DIR / "__init__.py").write_text(init)
    print(f"Wrote {len(written)} pydantic modules + entity.py to pydantic/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
