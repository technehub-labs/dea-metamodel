"""CR-AM-05A hierarchical dimensions & instruments conformance tests.

One test per acceptance criterion (CR-AM-05A §39), covering the §38
required scenarios. Positive and negative paths are both exercised.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from runtime.instruments import (  # noqa: E402
    HierarchyError,
    InstrumentEvolutionError,
    hierarchy_depth,
    instrument_questions,
    iter_path,
    result_lineage_preserves_instrument,
    validate_dimension_hierarchy,
    validate_instrument_evolution,
)


def load_yaml(rel_path: str):
    return yaml.safe_load((REPO_ROOT / rel_path).read_text())


def load_json(rel_path: str):
    return json.loads((REPO_ROOT / rel_path).read_text())


EXAMPLE = "assessment-models/examples/hierarchical-maturity-assessment.yaml"


def example():
    return load_yaml(EXAMPLE)


def validator_for(schema_rel: str):
    from jsonschema import Draft202012Validator, RefResolver

    schema = load_json(f"assessment-models/schemas/{schema_rel}")
    common = load_json("assessment-models/schemas/common.schema.json")
    store = {
        "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
        "common.schema.json": common,
    }
    for extra in ("response-specification.schema.json", "assessment-item.schema.json"):
        doc = load_json(f"assessment-models/schemas/{extra}")
        store[extra] = doc
        store[doc["$id"]] = doc
    resolver = RefResolver(base_uri="", referrer=schema, store=store)
    return Draft202012Validator(schema, resolver=resolver)


class TestCRAM05A(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.example = example()

    # AC-AM05A-01 — Hierarchical Dimensions without a SubDimension class
    def test_ac_am05a_01_hierarchical_dimensions(self) -> None:
        dims = self.example["dimensions"]
        nodes = validate_dimension_hierarchy(dims)
        self.assertEqual(len(nodes), 3)
        roots = [n for n in nodes if n.is_root]
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].id, "dea:dimension-automation")
        # No SubDimension class exists anywhere in the schemas — check
        # structure (properties/$defs), not prose descriptions.
        for schema_path in (REPO_ROOT / "assessment-models/schemas").glob("*.json"):
            doc = json.loads(schema_path.read_text())
            for key in ("properties", "$defs"):
                names = set(doc.get(key, {}))
                self.assertNotIn("SubDimension", names)
                self.assertNotIn("sub_dimension", names)
                self.assertNotIn("SubSubDimension", names)

    # AC-AM05A-02 — Arbitrary depth
    def test_ac_am05a_02_arbitrary_depth(self) -> None:
        dims: list[dict] = [{"id": "d0", "version": "1.0.0"}]
        for i in range(1, 7):
            dims.append(
                {
                    "id": f"d{i}",
                    "version": "1.0.0",
                    "parent_dimension": {"id": f"d{i-1}", "version": "1.0.0"},
                }
            )
        self.assertEqual(hierarchy_depth(dims), 7)

    # AC-AM05A-03 — Cycle prevention (§38: A → B → A must fail)
    def test_ac_am05a_03_cycle_rejected(self) -> None:
        with self.assertRaises(HierarchyError):
            validate_dimension_hierarchy(
                [
                    {"id": "a", "parent_dimension": {"id": "b"}},
                    {"id": "b", "parent_dimension": {"id": "a"}},
                ]
            )
        with self.assertRaises(HierarchyError):
            validate_dimension_hierarchy(
                [{"id": "a", "parent_dimension": {"id": "a"}}]
            )
        with self.assertRaises(HierarchyError):
            validate_dimension_hierarchy(
                [
                    {"id": "a"},
                    {"id": "a"},  # duplicate identity
                ]
            )
        with self.assertRaises(HierarchyError):
            validate_dimension_hierarchy(
                [{"id": "a", "parent_dimension": {"id": "ghost"}}]
            )

    # AC-AM05A-04 — Capability independence (§38: same capability under different structures)
    def test_ac_am05a_04_capability_independence(self) -> None:
        # The example binds dea:capability-decision-automation under the
        # Decision Automation dimension; the same capability is also listed
        # at the root Automation dimension — reuse across structures.
        root = self.example["dimensions"][0]
        leaf = self.example["dimensions"][2]
        root_caps = {c["id"] for c in root.get("capabilities", [])}
        item_caps = {
            item["capability"]["id"]
            for section in self.example["instrument"]["sections"]
            for item in section["items"]
            if "capability" in item
        }
        self.assertIn("dea:capability-decision-automation", root_caps & item_caps)
        # Capability schema exists independently and has no parent_dimension.
        cap_schema = load_json("assessment-models/schemas/capability.schema.json")
        self.assertNotIn("parent_dimension", cap_schema.get("properties", {}))
        self.assertNotIn("parentDimension", cap_schema.get("properties", {}))

    # AC-AM05A-05 — Criteria bridge evidence and maturity
    def test_ac_am05a_05_criteria_validate(self) -> None:
        v = validator_for("criterion.schema.json")
        criteria = self.example["criteria"]
        self.assertEqual(len(criteria), 2)
        for c in criteria:
            self.assertEqual(list(v.iter_errors(c)), [])
            self.assertIn("maturity_model", c)
            self.assertIn("evidence_requirement", c)

    # AC-AM05A-06 — Indicators represent observable characteristics
    def test_ac_am05a_06_indicators_validate(self) -> None:
        v = validator_for("indicator.schema.json")
        for ind in self.example["indicators"]:
            self.assertEqual(list(v.iter_errors(ind)), [])
            self.assertIn("measure", ind)
            self.assertIn("criterion", ind)

    # AC-AM05A-07 — Instruments are independently versioned
    def test_ac_am05a_07_instrument_versioning(self) -> None:
        v = validator_for("assessment-instrument.schema.json")
        inst = self.example["instrument"]
        self.assertEqual(list(v.iter_errors(inst)), [])
        self.assertEqual(inst["version"], "1.0.0")
        self.assertEqual(inst["maturity_model"]["id"], "dea:maturity-aomm")

    # AC-AM05A-08 — Questions are independently identifiable and versionable
    def test_ac_am05a_08_questions_versioned(self) -> None:
        v = validator_for("question.schema.json")
        questions = self.example["questions"]
        self.assertGreaterEqual(len(questions), 5)
        ids = set()
        for q in questions:
            self.assertEqual(list(v.iter_errors(q)), [])
            self.assertNotIn((q["id"], q["version"]), ids)
            ids.add((q["id"], q["version"]))

    # AC-AM05A-09 — Question reuse across instruments (§38)
    def test_ac_am05a_09_question_reuse(self) -> None:
        inst_a = self.example["instrument"]
        inst_b = json.loads(json.dumps(inst_a))
        inst_b["id"] = "dea:instrument-aom-automation-b"
        inst_b["version"] = "1.1.0"
        # Same question id bound in both instruments.
        q_a = instrument_questions(inst_a)
        q_b = instrument_questions(inst_b)
        self.assertEqual(q_a, q_b)
        self.assertIn("dea:q-policy-enforcement", q_a)

    # AC-AM05A-10 — Multiple response types (§38: boolean, numeric, percentage, choice, evidence)
    def test_ac_am05a_10_response_types(self) -> None:
        types = {
            q["response_specification"]["type"] for q in self.example["questions"]
        }
        self.assertTrue(
            {"boolean", "percentage", "single-choice", "multi-choice", "evidence", "measurement"}
            <= types
        )
        # Choice types must declare options; a choice spec without options fails.
        v = validator_for("response-specification.schema.json")
        bad = {"type": "single-choice"}
        self.assertNotEqual(list(v.iter_errors(bad)), [])
        good = {"type": "single-choice", "options": [{"id": "a"}, {"id": "b"}]}
        self.assertEqual(list(v.iter_errors(good)), [])
        # Percentage constrains to 0..100/percent.
        bad_pct = {"type": "percentage", "min": 10}
        self.assertNotEqual(list(v.iter_errors(bad_pct)), [])

    # AC-AM05A-11 — Questions do not own MaturityLevels
    def test_ac_am05a_11_question_maturity_decoupling(self) -> None:
        schema = load_json("assessment-models/schemas/question.schema.json")
        props = schema["properties"]
        for forbidden in ("maturity_level", "maturityLevel", "level", "maturity"):
            self.assertNotIn(forbidden, props)
        # additionalProperties false makes a maturityLevel payload fail.
        v = validator_for("question.schema.json")
        bad = {
            "id": "dea:q-bad",
            "version": "1.0.0",
            "text": "x",
            "status": "active",
            "response_specification": {"type": "boolean"},
            "maturityLevel": 4,
        }
        self.assertNotEqual(list(v.iter_errors(bad)), [])

    # AC-AM05A-12 — Multiple questions contribute to one criterion (§18)
    def test_ac_am05a_12_criterion_aggregation(self) -> None:
        criterion_items: dict[str, list] = {}
        for section in self.example["instrument"]["sections"]:
            for item in section["items"]:
                cid = (item.get("criterion") or {}).get("id")
                if cid:
                    criterion_items.setdefault(cid, []).append(item["id"])
        self.assertIn("dea:criterion-automated-policy-enforcement", criterion_items)
        self.assertGreaterEqual(
            len(criterion_items["dea:criterion-automated-policy-enforcement"]), 5
        )

    # AC-AM05A-13 — Historical integrity (§33)
    def test_ac_am05a_13_historical_integrity(self) -> None:
        lineage = self.example["result_lineage"]
        self.assertTrue(
            result_lineage_preserves_instrument({"lineage": lineage})
        )
        # Every item in the instrument pins a question version.
        for section in self.example["instrument"]["sections"]:
            for item in section["items"]:
                self.assertTrue(item["question"].get("version"))

    # AC-AM05A-14 — Incremental evolution (§29, §41)
    def test_ac_am05a_14_incremental_evolution(self) -> None:
        v10 = self.example["instrument"]
        v11 = json.loads(json.dumps(v10))
        v11["version"] = "1.1.0"
        v11["sections"][0]["items"].extend(
            [
                {
                    "id": "dea:item-policy-exception-rate",
                    "question": {"id": "dea:q-exception-rate", "version": "1.0.0"},
                    "criterion": {"id": "dea:criterion-automated-policy-enforcement", "version": "1.0.0"},
                    "sequence": 6,
                },
                {
                    "id": "dea:item-remediation-window",
                    "question": {"id": "dea:q-remediation-window", "version": "1.0.0"},
                    "criterion": {"id": "dea:criterion-automated-policy-enforcement", "version": "1.0.0"},
                    "sequence": 7,
                },
                {
                    "id": "dea:item-rollback-safety",
                    "question": {"id": "dea:q-rollback-safety", "version": "1.0.0"},
                    "criterion": {"id": "dea:criterion-automated-decision-enforcement", "version": "1.0.0"},
                    "sequence": 8,
                },
            ]
        )
        summary = validate_instrument_evolution(v10, v11)
        self.assertEqual(len(summary["added"]), 3)
        self.assertTrue(summary["maturity_model_unchanged"])
        # Changing the maturity model alongside is NOT incremental evolution.
        v_bad = json.loads(json.dumps(v11))
        v_bad["maturity_model"] = {"id": "dea:maturity-aomm", "version": "2.0.0"}
        with self.assertRaises(InstrumentEvolutionError):
            validate_instrument_evolution(v10, v_bad)

    # AC-AM05A-15 — Question retirement preserves historical results (§30)
    def test_ac_am05a_15_question_retirement(self) -> None:
        # Retire a question; historical instrument + lineage still validate.
        retired = dict(self.example["questions"][2])
        retired["status"] = "retired"
        v = validator_for("question.schema.json")
        self.assertEqual(list(v.iter_errors(retired)), [])
        # The historical instrument referencing it is untouched and valid.
        iv = validator_for("assessment-instrument.schema.json")
        self.assertEqual(list(iv.iter_errors(self.example["instrument"])), [])

    # AC-AM05A-16 — Semantic lineage path (§34)
    def test_ac_am05a_16_semantic_path(self) -> None:
        path = iter_path(
            self.example["dimensions"], "dea:dimension-decision-automation"
        )
        self.assertEqual(
            path,
            [
                "dea:dimension-automation",
                "dea:dimension-closed-loop-automation",
                "dea:dimension-decision-automation",
            ],
        )

    # AC-AM05A-17 — Existing models and results remain valid
    def test_ac_am05a_17_existing_artifacts_valid(self) -> None:
        from jsonschema import Draft202012Validator, RefResolver

        common = load_json("assessment-models/schemas/common.schema.json")
        store = {
            "https://github.com/technehub-labs/dea-metamodel/assessment-models/schemas/common.schema.json": common,
            "common.schema.json": common,
        }
        cases = [
            ("assessment-models/examples/canonical-technology-assessment.yaml",
             "assessment-models/schemas/assessment-model.schema.json"),
            ("assessment-models/examples/zero-touch-operations-assessment.yaml",
             "assessment-models/schemas/assessment-model.schema.json"),
            ("assessment-models/examples/zero-touch-operations-result.yaml",
             "assessment-models/schemas/assessment-result.schema.json"),
            ("assessment-models/examples/technology-result-am04.yaml",
             "assessment-models/schemas/assessment-result.schema.json"),
        ]
        for path, schema_path in cases:
            schema = load_json(schema_path)
            resolver = RefResolver(base_uri="", referrer=schema, store=store)
            v = Draft202012Validator(schema, resolver=resolver)
            doc = load_yaml(path)
            errs = list(v.iter_errors(doc))
            self.assertEqual(errs, [], f"{path}: {[e.message for e in errs][:3]}")

    # §31 — Question replacement via supersedes lineage
    def test_am05a_question_replacement_lineage(self) -> None:
        v2 = {
            "id": "dea:q-policy-enforcement",
            "version": "2.0.0",
            "text": "Are operational policies automatically enforced across all domains?",
            "status": "active",
            "response_specification": {"type": "boolean"},
            "supersedes": [{"id": "dea:q-policy-enforcement", "version": "1.0.0"}],
        }
        v = validator_for("question.schema.json")
        self.assertEqual(list(v.iter_errors(v2)), [])
        self.assertEqual(v2["supersedes"][0]["version"], "1.0.0")

    # §23 — Sections are organizational, never a competing semantic hierarchy
    def test_am05a_sections_organizational_only(self) -> None:
        schema = load_json("assessment-models/schemas/assessment-instrument.schema.json")
        section_props = schema["properties"]["sections"]["items"]["properties"]
        for forbidden in ("parent_section", "parentSection", "sections"):
            self.assertNotIn(forbidden, section_props)

    # Vocabulary integrity — engine-facing enums mirror YAML vocabularies
    def test_am05a_vocabulary_integrity(self) -> None:
        rt = load_yaml("assessment-models/vocabulary/response-type.yaml")
        rt_ids = {v["id"] for v in rt["values"]}
        self.assertEqual(len(rt_ids), 12)
        schema = load_json("assessment-models/schemas/response-specification.schema.json")
        self.assertEqual(set(schema["properties"]["type"]["enum"]), rt_ids)
        qs = load_yaml("assessment-models/vocabulary/question-status.yaml")
        self.assertEqual({v["id"] for v in qs["values"]}, {"draft", "active", "deprecated", "retired"})
        ds = load_yaml("assessment-models/vocabulary/dimension-status.yaml")
        self.assertEqual({v["id"] for v in ds["values"]}, {"draft", "active", "deprecated", "retired"})


if __name__ == "__main__":
    unittest.main()
