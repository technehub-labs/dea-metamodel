#!/usr/bin/env python3
"""OpenDEA Reference Validator (CR-8 §35) — the executable interpretation of the
OpenDEA Semantic Architecture & Conformance Specification.

Usage:
    python3 tools/opendea_validate.py MODEL.yaml [--json] [--normalize]

Conformance levels (specification/conformance-spec.md §27):
    0 syntax      — document parses
    1 structural  — envelope schema valid (schemas/model-envelope.json)
    2 semantic    — types/relationships/endpoints valid against the registry
    3 profile     — declared-profile rules (A/T/G families, closed-world scoped)

Exit code 0 = PASS (warnings allowed), 1 = FAIL.
"""
import json
import re
import sys
from pathlib import Path

import yaml

BASE = Path(__file__).parent.parent
ENVELOPE_SCHEMA = json.loads((BASE / "schemas" / "model-envelope.json").read_text())

# Actor subclassing (CR-7 §27/§46 — specializes Actor)
ACTOR_SUBTYPES = {"Actor", "Agent", "Orchestrator", "Controller"}


def load_registry():
    norm = yaml.safe_load((BASE / "metamodel" / "dea-metamodel.yaml").read_text())
    entities = {e["id"].split(":", 1)[1]: e for e in norm["entities"]}
    rels = {r["id"].split(":", 1)[1]: r for r in norm["relationships"]}
    # Type hierarchy from the OWL serialization (rdfs:subClassOf) — the authoritative
    # pairwise hierarchy. (Registry specializes endpoints declare permissible TYPE SETS,
    # not pairwise edges; using them here would be over-permissive.)
    spec = {}
    ttl = (BASE / "ttl" / "dea-metamodel-ontology.ttl").read_text()
    for m in re.finditer(r"dea:(\w+) a owl:Class ;\s*\n\s*rdfs:subClassOf dea:(\w+)", ttl):
        spec.setdefault(m.group(1), set()).add(m.group(2))
    return entities, rels, spec


def type_satisfies(actual, declared, spec):
    """Endpoint compatibility: exact, wildcard, Actor-branch, or specializes chain."""
    if actual == declared or declared == "Entity":
        return True
    if declared == "Actor" and actual in ACTOR_SUBTYPES:
        return True
    seen, frontier = set(), [actual]
    while frontier:
        nxt = frontier.pop()
        for parent in spec.get(nxt, ()):
            if parent == declared:
                return True
            if parent not in seen:
                seen.add(parent)
                frontier.append(parent)
    return False


class Violation:
    def __init__(self, rule, code, severity, element, message, level):
        self.rule, self.code, self.severity = rule, code, severity
        self.element, self.message, self.level = element, message, level

    def as_dict(self):
        return {"rule": self.rule, "code": self.code, "severity": self.severity,
                "element": self.element, "message": self.message}


def validate(model_path):
    violations = []
    levels = {"syntax": "pass", "structural": "pass", "semantic": "pass", "profile": "pass"}

    # ---- Level 0: syntax ----
    try:
        doc = yaml.safe_load(Path(model_path).read_text())
        assert isinstance(doc, dict)
    except Exception as e:
        violations.append(Violation("SYNTAX", "DEA-E004", "error", str(model_path),
                                    f"document does not parse: {e}", 0))
        return _report(model_path, violations, levels, syntax_fail=True)

    # ---- Level 1: structural (envelope) ----
    import jsonschema
    for err in jsonschema.Draft7Validator(ENVELOPE_SCHEMA).iter_errors(doc):
        levels["structural"] = "fail"
        violations.append(Violation("ENVELOPE", "DEA-E004", "error",
                                    "$" + "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in err.absolute_path),
                                    err.message, 1))
    if levels["structural"] == "fail":
        return _report(model_path, violations, levels)

    entities, rels, spec = load_registry()
    declared_profiles = set(doc.get("profiles", []))
    elements = {el["id"]: el for el in doc.get("elements", [])}

    # ---- Level 2: semantic ----
    for el in doc.get("elements", []):
        etype = el.get("type", "")
        if etype not in entities:
            levels["semantic"] = "fail"
            violations.append(Violation("INV-TYPE", "DEA-E001", "error", el["id"],
                                        f"unknown type {etype!r} — not in the canonical registry", 2))
            continue
        if entities[etype].get("abstract"):
            levels["semantic"] = "fail"
            violations.append(Violation("INV-TYPE", "DEA-E001", "error", el["id"],
                                        f"type {etype} is abstract and cannot be instantiated (§9)", 2))
        for rel in el.get("relationships", []):
            rtype = rel.get("type", "")
            if rtype not in rels:
                levels["semantic"] = "fail"
                violations.append(Violation("INV-REL", "DEA-E002", "error", el["id"],
                                            f"undeclared relationship type {rtype!r}", 2))
                continue
            tgt = rel.get("target")
            if tgt not in elements:
                levels["semantic"] = "fail"
                violations.append(Violation("INV-REL", "DEA-E005", "error", el["id"],
                                            f"relationship target {tgt!r} not present in model", 2))
                continue
            rdef = rels[rtype]
            src_types = {t.split(":", 1)[1] for t in rdef["source"]["types"]}
            tgt_types = {t.split(":", 1)[1] for t in rdef["target"]["types"]}
            if not any(type_satisfies(etype, st, spec) for st in src_types):
                levels["semantic"] = "fail"
                violations.append(Violation("INV-REL", "DEA-E006", "error", el["id"],
                                            f"{etype} is not a valid source for {rtype} (expected one of {sorted(src_types)})", 2))
            ttype = elements[tgt]["type"]
            if not any(type_satisfies(ttype, tt, spec) for tt in tgt_types):
                levels["semantic"] = "fail"
                violations.append(Violation("INV-REL", "DEA-E005", "error", el["id"],
                                            f"{ttype} is not a valid target for {rtype} (expected one of {sorted(tgt_types)})", 2))

    # ---- Level 3: profile rules (closed-world within declared profiles) ----
    def edges(el, rtype):
        return [r for r in el.get("relationships", []) if r.get("type") == rtype]

    agentic = any(p.startswith("dea:agentic@") for p in declared_profiles)
    assessment = any(p.startswith("dea:assessment@") for p in declared_profiles)

    for el in doc.get("elements", []):
        etype = el.get("type", "")
        props = el.get("properties", {}) or {}
        # A008 — assessment attributes must not be intrinsic (any profile; architectural rule)
        if assessment and etype not in entities:
            continue
        if assessment:
            cat = (entities.get(etype, {}).get("membership") or {}).get("profile")
            if cat != "dea:assessment":
                for bad in ("maturity", "maturity_level", "maturity_target", "score"):
                    if bad in props:
                        levels["profile"] = "fail"
                        violations.append(Violation("A008", "DEA-E010", "error", el["id"],
                                                    f"intrinsic {bad!r} on {etype} — maturity belongs to AssessmentResult (CR-5 §2)", 3))
        if agentic and etype == "Agent":
            if not edges(el, "authorized-by") and "authority_ref" not in props:
                levels["profile"] = "fail"
                violations.append(Violation("G006", "DEA-E009", "error", el["id"],
                                            "Agent has no delegated authority (authorized-by or authority_ref)", 3))
            if "owner_ref" not in props:
                owned = any("owns" in [r.get("type") for r in other.get("relationships", [])]
                            and any(r.get("target") == el["id"] for r in other.get("relationships", []))
                            for other in doc.get("elements", []))
                if not owned:
                    levels["profile"] = "fail"
                    violations.append(Violation("G007", "DEA-E008", "error", el["id"],
                                                "Agent has no accountable owner (owner_ref or incoming owns edge)", 3))
            if not edges(el, "constrained-by"):
                levels["profile"] = "fail"
                violations.append(Violation("G008", "DEA-E008", "error", el["id"],
                                            "Agent references no governance policy (constrained-by)", 3))
        if assessment and etype == "Assessment":
            n = len(edges(el, "conducted-under"))
            if n != 1:
                levels["profile"] = "fail"
                violations.append(Violation("A001", "DEA-E003", "error", el["id"],
                                            f"Assessment must be conducted-under exactly one framework, found {n}", 3))

    return _report(model_path, violations, levels)


def _report(model_path, violations, levels, syntax_fail=False):
    errors = sum(1 for v in violations if v.severity == "error")
    warnings = sum(1 for v in violations if v.severity == "warning")
    return {
        "conformance": {"status": "failed" if errors else "passed"},
        "model": str(model_path),
        "levels": levels,
        "summary": {"errors": errors, "warnings": warnings},
        "violations": [v.as_dict() for v in violations],
    }


def normalize(doc):
    """CR-8 §36: canonicalize — sort elements, apply structural defaults, stable output."""
    out = dict(doc)
    out["elements"] = sorted(doc.get("elements", []), key=lambda e: e["id"])
    for el in out["elements"]:
        el.setdefault("version", "1.0.0")
        el["relationships"] = sorted(el.get("relationships", []),
                                     key=lambda r: (r["type"], r["target"]))
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    model_path = argv[1]
    as_json = "--json" in argv
    do_norm = "--normalize" in argv

    report = validate(model_path)
    if do_norm and report["conformance"]["status"] == "passed":
        doc = yaml.safe_load(Path(model_path).read_text())
        print(json.dumps(normalize(doc), indent=2, ensure_ascii=False))
        return 0
    if as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("OpenDEA Conformance Validator")
        print(f"Version 1.0.0 (spec {ENVELOPE_SCHEMA['metamodel_version']})")
        print(f"Model: {report['model']}")
        print("Levels: " + "  ".join(f"{k}={v}" for k, v in report["levels"].items()))
        print(f"Result: {'PASS' if report['conformance']['status'] == 'passed' else 'FAIL'}")
        print(f"Errors:   {report['summary']['errors']}")
        print(f"Warnings: {report['summary']['warnings']}")
        for v in report["violations"]:
            print(f"  [{v['severity'].upper()}] {v['rule']} ({v['code']}) {v['element']}: {v['message']}")
    return 0 if report["conformance"]["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
