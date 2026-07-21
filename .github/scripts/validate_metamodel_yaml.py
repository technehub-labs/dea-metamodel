#!/usr/bin/env python3
"""Validate metamodel.yaml against expected structure."""
import sys, yaml, json
from pathlib import Path

BASE = Path(__file__).parent.parent.parent

def main():
    with open(BASE / "metamodel.yaml") as f:
        mm = yaml.safe_load(f)

    errors = []

    # Check top-level keys
    required = ["metamodel", "entities", "relationships"]
    for k in required:
        if k not in mm:
            errors.append(f"Missing top-level key: {k}")

    # Check each entity has required fields
    for e in mm.get("entities", []):
        for f in ["name", "description", "schema"]:
            if f not in e:
                errors.append(f"Entity '{e.get('name','?')}' missing field: {f}")

    # Check each relationship has required fields
    for r in mm.get("relationships", []):
        for f in ["name", "description", "schema"]:
            if f not in r:
                errors.append(f"Relationship '{r.get('name','?')}' missing field: {f}")

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"✓ metamodel.yaml valid ({len(mm['entities'])} entities, {len(mm['relationships'])} relationships)")

if __name__ == "__main__":
    main()
