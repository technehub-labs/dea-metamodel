"""ECF kebab-case restatement validator (CR-MM-ECF-01 §3).

Closes matrix finding F1 for `dea-metamodel`: proves that every kebab-case
value used in the `ecf_domain` and `ecf_stage` enums of
`schemas/entities/business-object.json` and
`schemas/entities/organizational-unit.json` resolves 1:1 to a canonical
PascalCase value in `dea-metaframework/schemas/ecf-{domain,stage}.schema.json`.

Resolution rules (normative per CR-MM-ECF-01 §3.1):

Domain:
    kebab-case -> PascalCase -> lowerCamelCase (identifier suffix)
    governance-existence -> GovernanceAndExistence -> governanceExistence
    supply-resources    -> SupplyAndResources       -> supplyResources
    people-organization -> PeopleAndOrganization     -> peopleOrganization
    customer-demand     -> CustomerAndDemand         -> customerDemand
    product-offering    -> ProductAndOffering        -> productOffering
    operations-delivery -> OperationsAndDelivery    -> operationsDelivery
    finance-value       -> FinanceAndValue           -> financeValue

Stage:
    kebab-case == PascalCase (lowerCamelCase is the same word for all seven).
    conceive -> Conceive
    design   -> Design
    build    -> Build
    activate -> Activate
    operate  -> Operate
    improve  -> Improve
    retire   -> Retire

The validator exits 0 only if:
  1. every kebab-case value in the affected enums resolves to a canonical
     PascalCase value (via the table above); and
  2. the set of resolved PascalCase values equals the canonical enum set
     (no missing, no extra).

Otherwise it exits non-zero and prints a structured diagnostic.

Stdlib only; no third-party dependencies.

Environment variables:
    ECF_FRAMEWORK_ROOT — path to the dea-metaframework clone. Defaults to
        /home/hermes/dea-work/dea-metaframework.

Usage:
    python3 scripts/validate_ecf_kebab_restatement.py

Options:
    --self-test     Run the built-in broken-schema self-test (exit non-zero
                    if the test detects a regression in the validator itself).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FWK = Path(
    os.environ.get(
        "ECF_FRAMEWORK_ROOT",
        "/home/hermes/dea-work/dea-metaframework",
    )
)

# Schemas in this repo that restate Domain/Stage in kebab-case.
RESTATING_SCHEMAS = (
    REPO / "schemas" / "entities" / "business-object.json",
    REPO / "schemas" / "entities" / "organizational-unit.json",
)

# Normative kebab-case -> PascalCase mapping (CR-MM-ECF-01 §3.1).
# Lower-case keys so lookups are case-insensitive against the kebab-case
# values found in JSON enums.
DOMAIN_KEBAB_TO_PASCAL = {
    "governance-existence": "GovernanceAndExistence",
    "supply-resources": "SupplyAndResources",
    "people-organization": "PeopleAndOrganization",
    "customer-demand": "CustomerAndDemand",
    "product-offering": "ProductAndOffering",
    "operations-delivery": "OperationsAndDelivery",
    "finance-value": "FinanceAndValue",
}

STAGE_KEBAB_TO_PASCAL = {
    "conceive": "Conceive",
    "design": "Design",
    "build": "Build",
    "activate": "Activate",
    "operate": "Operate",
    "improve": "Improve",
    "retire": "Retire",
}

# kebab-case pattern sanity-check (lowercase letters + single hyphens).
KEBAB_PATTERN = re.compile(r"^[a-z]+(-[a-z]+)*$")


def load_canonical_enum(schema_path: Path) -> set[str]:
    """Return the canonical PascalCase enum from a framework JSON Schema."""
    if not schema_path.exists():
        raise FileNotFoundError(
            f"Canonical schema not found: {schema_path}. "
            f"Set ECF_FRAMEWORK_ROOT or clone dea-metaframework."
        )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    enum = schema.get("enum")
    if not isinstance(enum, list) or not enum:
        raise ValueError(
            f"Canonical schema {schema_path} does not declare a non-empty 'enum'."
        )
    return set(enum)


def resolve_kebab_to_pascal(
    kebab_values: list[str],
    mapping: dict[str, str],
    field_label: str,
) -> tuple[set[str], list[str]]:
    """Resolve every kebab-case value via the mapping table.

    Returns (resolved_pascal_set, errors).
    """
    errors: list[str] = []
    resolved: set[str] = set()
    for v in kebab_values:
        if not isinstance(v, str):
            errors.append(f"{field_label}: non-string enum value: {v!r}")
            continue
        if not KEBAB_PATTERN.match(v):
            errors.append(
                f"{field_label}: kebab-case value {v!r} fails pattern "
                f"(lowercase letters with single hyphens)"
            )
            continue
        if v not in mapping:
            errors.append(
                f"{field_label}: kebab-case value {v!r} is not in the "
                f"normative mapping table"
            )
            continue
        resolved.add(mapping[v])
    return resolved, errors


def validate_restating_schema(schema_path: Path) -> list[str]:
    """Validate one restating schema. Returns a list of error messages."""
    errors: list[str] = []
    if not schema_path.exists():
        return [f"restating schema not found: {schema_path}"]

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    props = schema.get("properties") or {}

    # ecf_domain
    if "ecf_domain" not in props:
        errors.append(f"{schema_path.name}: missing 'ecf_domain' property")
    else:
        ecf_domain = props["ecf_domain"]
        domain_enum = ecf_domain.get("enum")
        if not isinstance(domain_enum, list):
            errors.append(
                f"{schema_path.name}: ecf_domain.enum is not a list"
            )
        else:
            canonical = load_canonical_enum(FWK / "schemas" / "ecf-domain.schema.json")
            resolved, resolve_errors = resolve_kebab_to_pascal(
                domain_enum, DOMAIN_KEBAB_TO_PASCAL, f"{schema_path.name}:ecf_domain"
            )
            errors.extend(resolve_errors)
            missing = canonical - resolved
            extra = resolved - canonical
            if missing:
                errors.append(
                    f"{schema_path.name}:ecf_domain kebab-case restatement "
                    f"is missing canonical Domains: {sorted(missing)}"
                )
            if extra:
                errors.append(
                    f"{schema_path.name}:ecf_domain kebab-case restatement "
                    f"introduces non-canonical Domains: {sorted(extra)}"
                )

    # ecf_stage
    if "ecf_stage" not in props:
        errors.append(f"{schema_path.name}: missing 'ecf_stage' property")
    else:
        ecf_stage = props["ecf_stage"]
        stage_enum = ecf_stage.get("enum")
        if not isinstance(stage_enum, list):
            errors.append(
                f"{schema_path.name}: ecf_stage.enum is not a list"
            )
        else:
            canonical = load_canonical_enum(FWK / "schemas" / "ecf-stage.schema.json")
            resolved, resolve_errors = resolve_kebab_to_pascal(
                stage_enum, STAGE_KEBAB_TO_PASCAL, f"{schema_path.name}:ecf_stage"
            )
            errors.extend(resolve_errors)
            missing = canonical - resolved
            extra = resolved - canonical
            if missing:
                errors.append(
                    f"{schema_path.name}:ecf_stage kebab-case restatement "
                    f"is missing canonical Stages: {sorted(missing)}"
                )
            if extra:
                errors.append(
                    f"{schema_path.name}:ecf_stage kebab-case restatement "
                    f"introduces non-canonical Stages: {sorted(extra)}"
                )

    return errors


def run_self_test() -> tuple[bool, list[str]]:
    """Built-in broken-schema test: prove the validator detects drift.

    Writes a deliberately-broken schema to a temp file, calls
    validate_restating_schema, and asserts errors are returned.
    """
    broken_schema = {
        "type": "object",
        "properties": {
            "ecf_domain": {
                "type": "string",
                "enum": [
                    "governance-existence",
                    "supply-resources",
                    # intentionally missing several canonical domains
                    "finance-value",
                    # intentionally introduces a non-canonical value
                    "rogue-domain",
                ],
            },
            "ecf_stage": {
                "type": "string",
                "enum": [
                    "conceive", "design", "build", "activate", "operate",
                    "improve", "retire",
                ],
            },
        },
    }
    notes: list[str] = []
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as fh:
        json.dump(broken_schema, fh)
        tmp_path = Path(fh.name)
    try:
        errors = validate_restating_schema(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    # Expect: (a) rogue-domain flagged, (b) missing canonical Domains
    # flagged. (c) Stage set is complete so no Stage errors.
    saw_rogue = any("rogue-domain" in e for e in errors)
    saw_missing = any("is missing canonical Domains" in e for e in errors)
    if not saw_rogue:
        notes.append("self-test FAIL: did not detect rogue-domain")
    if not saw_missing:
        notes.append("self-test FAIL: did not detect missing canonical Domains")
    passed = saw_rogue and saw_missing and not notes
    return passed, notes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CR-MM-ECF-01: ECF kebab-case restatement validator"
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the broken-schema self-test and exit.",
    )
    args = parser.parse_args()

    if args.self_test:
        passed, notes = run_self_test()
        if passed:
            print("self-test PASS: validator detects broken restatement schemas.")
            return 0
        for n in notes:
            print(n)
        print("self-test FAIL: validator did not detect the deliberately-broken schema.")
        return 1

    print("ECF kebab-case restatement validator (CR-MM-ECF-01 §3)")
    print(f"  framework root: {FWK}")
    print(f"  repo root:      {REPO}")

    all_errors: list[str] = []
    for schema in RESTATING_SCHEMAS:
        errs = validate_restating_schema(schema)
        all_errors.extend(errs)

    if all_errors:
        print("FAIL: ECF kebab-case restatement does not resolve 1:1 to canonical.", file=sys.stderr)
        for e in all_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    # Self-test also runs in normal mode (catches validator regressions).
    passed, notes = run_self_test()
    if not passed:
        print("FAIL: built-in self-test detected a validator regression.", file=sys.stderr)
        for n in notes:
            print(f"  - {n}", file=sys.stderr)
        return 2

    print("PASS: every kebab-case value in the restating schemas resolves 1:1 "
          "to the canonical PascalCase enum.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())