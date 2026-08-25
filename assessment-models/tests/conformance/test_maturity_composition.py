"""CR-AM-10 Phase 1 maturity component & reference conformance tests.

Covers the Phase 1 contract (CR-AM-10 §11 Phase 1): the MaturityComponent
and ComponentReference schemas, the component-kinds / reference-kinds
vocabularies, the component registry, and the worked examples — including
the spec acceptance tests (a published dimension-package validates; an
import reference and an override reference validate). The boundary guards
verify there is no silent inheritance: a kindless reference is refused,
an import carrying a payload is refused, an override without rationale is
refused, and a component reference without a pinned version is refused.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, RefResolver

REPO_ROOT = Path(__file__).resolve().parents[3]

COMPONENT_SCHEMA_PATH = "assessment-models/schemas/maturity-component.schema.json"
REFERENCE_SCHEMA_PATH = "assessment-models/schemas/component-reference.schema.json"
COMPONENT_KINDS_PATH = "assessment-models/vocabulary/component-kinds.yaml"
REFERENCE_KINDS_PATH = "assessment-models/vocabulary/reference-kinds.yaml"
REGISTRY_PATH = "assessment-models/maturity/components/registry.yaml"
COMPONENT_EXAMPLE_PATH = (
    "assessment-models/maturity/component-examples/operations-service-dimensions.yaml"
)
IMPORT_EXAMPLE_PATH = (
    "assessment-models/maturity/component-examples/dt-imports-operations-dimensions.yaml"
)
OVERRIDE_EXAMPLE_PATH = (
    "assessment-models/maturity/component-examples/dt-overrides-incident-response.yaml"
)


def _preserve_timestamp_strings(loader, node):
    return loader.construct_scalar(node)


yaml.SafeLoader.add_constructor("tag:yaml.org,2002:timestamp", _preserve_timestamp_strings)


def load_yaml(rel_path: str):
    return yaml.safe_load((REPO_ROOT / rel_path).read_text())


def load_json(rel_path: str):
    return json.loads((REPO_ROOT / rel_path).read_text())


def _validator(schema_path: str):
    schema = load_json(schema_path)
    common = load_json("assessment-models/schemas/common.schema.json")
    # Pre-load every schema that may be referenced via $ref so
    # RefResolver never tries to fetch them over HTTP. CI runs the
    # whole suite via `python -m unittest discover` with no network,
    # and a 404 on any $ref aborts the whole run.
    store = {
        "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
        "common.schema.json": common,
    }
    resolver = RefResolver(base_uri="", referrer=schema, store=store)
    return Draft202012Validator(schema, resolver=resolver)


def vocab_ids(rel_path: str) -> set:
    return {v["id"] for v in load_yaml(rel_path)["values"]}


class MaturityComponentSchemaTest(unittest.TestCase):
    """Component schema integrity (CR-AM-10 §3)."""

    def test_schema_parses_as_draft_2020_12(self):
        schema = load_json(COMPONENT_SCHEMA_PATH)
        self.assertEqual(
            schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_required_fields_match_spec(self):
        schema = load_json(COMPONENT_SCHEMA_PATH)
        for field in ("id", "version", "metamodel_version", "name",
                      "kind", "published_by", "status", "content"):
            self.assertIn(field, schema["required"])

    def test_kind_enum_matches_vocabulary(self):
        """Drift guard: the schema enum and the controlled vocabulary
        must carry exactly the same component kinds."""
        schema = load_json(COMPONENT_SCHEMA_PATH)
        self.assertEqual(
            set(schema["properties"]["kind"]["enum"]),
            vocab_ids(COMPONENT_KINDS_PATH))

    def test_content_is_references_only(self):
        """No-silent-inheritance boundary: a component carries id:version
        pointers, never inline maturity content."""
        schema = load_json(COMPONENT_SCHEMA_PATH)
        content = schema["properties"]["content"]
        self.assertEqual(content["items"]["$ref"],
                         "common.schema.json#/$defs/modelReference")

    def test_component_example_validates(self):
        validator = _validator(COMPONENT_SCHEMA_PATH)
        doc = load_yaml(COMPONENT_EXAMPLE_PATH)
        errors = sorted(validator.iter_errors(doc), key=lambda e: e.path)
        self.assertEqual([], [e.message for e in errors])


class ComponentReferenceSchemaTest(unittest.TestCase):
    """Reference schema integrity + reference-kind guards (CR-AM-10 §4)."""

    def test_schema_parses_as_draft_2020_12(self):
        schema = load_json(REFERENCE_SCHEMA_PATH)
        self.assertEqual(
            schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_kind_is_mandatory(self):
        """A reference without a kind is refused — there is no implicit
        fourth kind."""
        schema = load_json(REFERENCE_SCHEMA_PATH)
        self.assertIn("kind", schema["required"])

    def test_kind_enum_matches_vocabulary(self):
        """Drift guard: the schema enum and the controlled vocabulary
        must carry exactly the same reference kinds."""
        schema = load_json(REFERENCE_SCHEMA_PATH)
        self.assertEqual(
            set(schema["properties"]["kind"]["enum"]),
            vocab_ids(REFERENCE_KINDS_PATH))

    def test_component_version_is_mandatory(self):
        """Composition pins id:version — a versionless reference is
        refused (never track a moving target)."""
        schema = load_json(REFERENCE_SCHEMA_PATH)
        self.assertIn("version", schema["properties"]["component"]["required"])

    def test_import_example_validates(self):
        validator = _validator(REFERENCE_SCHEMA_PATH)
        doc = load_yaml(IMPORT_EXAMPLE_PATH)
        errors = sorted(validator.iter_errors(doc), key=lambda e: e.path)
        self.assertEqual([], [e.message for e in errors])

    def test_override_example_validates(self):
        validator = _validator(REFERENCE_SCHEMA_PATH)
        doc = load_yaml(OVERRIDE_EXAMPLE_PATH)
        errors = sorted(validator.iter_errors(doc), key=lambda e: e.path)
        self.assertEqual([], [e.message for e in errors])

    def test_kindless_reference_is_refused(self):
        validator = _validator(REFERENCE_SCHEMA_PATH)
        doc = {"component": {"id": "dea:component-x", "version": "1.0.0"}}
        self.assertFalse(validator.is_valid(doc))

    def test_import_with_payload_is_refused(self):
        """No silent inheritance: import means verbatim. An import
        carrying additions/replaces/rationale is a conformance error."""
        validator = _validator(REFERENCE_SCHEMA_PATH)
        base = load_yaml(IMPORT_EXAMPLE_PATH)
        for payload in (
            {"additions": [{"id": "dea:dimension-x", "version": "1.0.0"}]},
            {"replaces": [{"id": "dea:dimension-x", "version": "1.0.0"}]},
            {"rationale": "just because"},
        ):
            doc = dict(base, **payload)
            self.assertFalse(
                validator.is_valid(doc),
                f"import with {list(payload)} must be refused")

    def test_override_without_rationale_is_refused(self):
        validator = _validator(REFERENCE_SCHEMA_PATH)
        doc = load_yaml(OVERRIDE_EXAMPLE_PATH)
        del doc["rationale"]
        self.assertFalse(validator.is_valid(doc))

    def test_override_without_replaces_is_refused(self):
        validator = _validator(REFERENCE_SCHEMA_PATH)
        doc = load_yaml(OVERRIDE_EXAMPLE_PATH)
        del doc["replaces"]
        self.assertFalse(validator.is_valid(doc))

    def test_extend_requires_additions(self):
        validator = _validator(REFERENCE_SCHEMA_PATH)
        doc = {"component": {"id": "dea:component-x", "version": "1.0.0"},
               "kind": "extend"}
        self.assertFalse(validator.is_valid(doc))
        doc["additions"] = [{"id": "dea:dimension-x", "version": "1.0.0"}]
        self.assertTrue(validator.is_valid(doc))


class ComponentRegistryTest(unittest.TestCase):
    """Registry guards (CR-AM-10 §3, Phase 1 catalogue file)."""

    def test_component_id_version_pairs_are_unique(self):
        registry = load_yaml(REGISTRY_PATH)["registry"]
        pairs = [(c["id"], c["version"]) for c in registry["components"]]
        self.assertEqual(
            len(pairs), len(set(pairs)),
            "duplicate (id, version) pair in component registry")

    def test_every_registered_component_file_exists(self):
        registry = load_yaml(REGISTRY_PATH)["registry"]
        for component in registry["components"]:
            path = REPO_ROOT / "assessment-models" / component["path"]
            self.assertTrue(
                path.exists(),
                f"registered component file missing: {component['path']}")

    def test_every_component_example_is_registered(self):
        """Collision-rejection guard: an unregistered component file in
        component-examples/ is a conformance error."""
        registry = load_yaml(REGISTRY_PATH)["registry"]
        registered = {c["id"] for c in registry["components"]}
        example_dir = REPO_ROOT / "assessment-models/maturity/component-examples"
        validator = _validator(COMPONENT_SCHEMA_PATH)
        for path in sorted(example_dir.glob("*.yaml")):
            doc = yaml.safe_load(path.read_text())
            if not validator.is_valid(doc):
                continue  # reference examples, not components
            self.assertIn(
                doc["id"], registered,
                f"component example {path.name} is not in the registry")


if __name__ == "__main__":
    unittest.main()
