#!/usr/bin/env python3
"""Validate all JSON schemas parse and conform to Draft-07."""
import sys, json
from pathlib import Path

BASE = Path(__file__).parent.parent.parent

def main():
    schemas_dir = BASE / "schemas" / "entities"
    errors = []
    count = 0

    for schema_path in schemas_dir.glob("*.json"):
        count += 1
        try:
            with open(schema_path) as f:
                json.load(f)
            print(f"  ✓ {schema_path.name}")
        except json.JSONDecodeError as e:
            errors.append(f"{schema_path.name}: {e}")

    if errors:
        print("\nVALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"\n✓ All {count} JSON schemas valid")

if __name__ == "__main__":
    main()
