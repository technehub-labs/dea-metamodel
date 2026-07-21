#!/usr/bin/env python3
"""Validate all Turtle (.ttl) RDF files parse cleanly."""
import sys
from pathlib import Path

try:
    from rdflib import Graph
except ImportError:
    print("SKIP: rdflib not installed (pip install rdflib)")
    sys.exit(0)

BASE = Path(__file__).parent.parent.parent

def main():
    ttl_dir = BASE / "ttl"
    errors = []
    count = 0

    for ttl_path in ttl_dir.rglob("*.ttl"):
        count += 1
        try:
            g = Graph()
            g.parse(ttl_path, format="turtle")
            print(f"  ✓ {ttl_path.relative_to(BASE)}")
        except Exception as e:
            errors.append(f"{ttl_path.relative_to(BASE)}: {e}")

    if errors:
        print("\nVALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"\n✓ All {count} TTL files parse valid")

if __name__ == "__main__":
    main()
