"""Test 003 (CR-1.9): no entity contains a relationship that is also
independently represented as a relationship instance, unless explicitly
declared as a derived convenience property."""
import json

from conftest import BASE

# The single declared derived convenience property (Entity base schema).
ALLOWED_CONVENIENCE = {"relationships"}


def test_no_undeclared_relationship_state(relationships):
    rel_names = {r["name"] for r in relationships} | {r["id"].split(":", 1)[1] for r in relationships}
    violations = []
    for path in sorted((BASE / "schemas" / "entities").glob("*.json")):
        schema = json.loads(path.read_text())
        for prop in schema.get("properties", {}):
            norm = prop.replace("-", "").replace("_", "").lower()
            if prop in ALLOWED_CONVENIENCE:
                continue
            if any(norm == rn.replace("-", "").lower() for rn in rel_names):
                violations.append(f"{path.name}: property {prop!r} duplicates relationship vocabulary")
    assert not violations, "Undeclared relationship state on entities:\n" + "\n".join(violations)
