"""Test 003 (CR-1.9): no entity contains a relationship that is also
independently represented as a relationship instance, unless explicitly
declared as a derived convenience property."""
import json

from conftest import BASE

# The single declared derived convenience property (Entity base schema)
# plus the Measurement / MeasurementObservation relationship references
# declared by CR-MET-003 (these ARE the relationship instance on the
# entity; the registry relationship and the field reference the same
# thing). Full audit-then-specifies per CR-MET-003 §4.3.1.
ALLOWED_CONVENIENCE = {
    "relationships",
    "applies_metric",    # CR-MET-003: Measurement -> dea:PerformanceMetric
    "measures_subject",  # CR-MET-003: Measurement -> dea:measured-by target
    "produced_by",       # CR-MET-003: MeasurementObservation -> dea:Measurement
}


def test_no_undeclared_relationship_state(relationships):
    rel_names = {r["name"] for r in relationships} | {r["id"].split(":", 1)[1] for r in relationships}
    violations = []
    for path in sorted((BASE / "schemas" / "entities").glob("*.json")):
        schema = json.loads(path.read_text())
        for prop, spec in schema.get("properties", {}).items():
            norm = prop.replace("-", "").replace("_", "").lower()
            if prop in ALLOWED_CONVENIENCE:
                continue
            if isinstance(spec, dict) and spec.get("deprecated"):
                continue  # CR-2F: marked for removal in CR-003; no longer authoritative
            if any(norm == rn.replace("-", "").lower() for rn in rel_names):
                violations.append(f"{path.name}: property {prop!r} duplicates relationship vocabulary")
    assert not violations, "Undeclared relationship state on entities:\n" + "\n".join(violations)
