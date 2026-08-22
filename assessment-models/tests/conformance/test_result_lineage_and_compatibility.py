"""
CR-AM-03 §17 + §14 lineage + compatibility test — every migrated result
carries complete versioned lineage AND a 6-axis compatibility declaration.
"""
import unittest
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RESULT_PATHS = {
    "technology":        REPO_ROOT / "assessment-models" / "examples" / "technology-result.yaml",
    "modernization":     REPO_ROOT / "assessment-models" / "examples" / "modernization-result.yaml",
    "operations":        REPO_ROOT / "assessment-models" / "examples" / "operations-result.yaml",
    "services-delivery": REPO_ROOT / "assessment-models" / "examples" / "services-delivery-result.yaml",
}
EXECUTION_PATHS = {
    "technology":        REPO_ROOT / "assessment-models" / "examples" / "executions" / "technology-execution.yaml",
    "modernization":     REPO_ROOT / "assessment-models" / "examples" / "executions" / "modernization-execution.yaml",
    "operations":        REPO_ROOT / "assessment-models" / "examples" / "executions" / "operations-execution.yaml",
    "services-delivery": REPO_ROOT / "assessment-models" / "examples" / "executions" / "services-delivery-execution.yaml",
}
REQUIRED_LINEAGE = ["assessment_model", "assessment_instrument", "assessment_execution", "capability", "scenario",
                    "measures", "scoring_model", "maturity_model"]
REQUIRED_AXES = ["schema", "semantic", "scoring", "maturity", "result", "benchmark"]


class TestResultLineageAndCompatibility(unittest.TestCase):
    """AC-AM03-13: every result contains complete versioned lineage.
    AC-AM03-14: every result carries the six compatibility dimensions."""

    def test_result_paths_exist(self):
        for d, p in RESULT_PATHS.items():
            assert p.exists(), f"{d}: result missing at {p}"

    def test_every_result_has_full_lineage(self):
        """AC-AM03-13: lineage is required by the canonical result schema."""
        for d, p in RESULT_PATHS.items():
            with open(p) as fh:
                doc = yaml.safe_load(fh)
            lineage = doc.get("lineage")
            assert lineage is not None, f"{d}: lineage missing"
            for key in REQUIRED_LINEAGE:
                assert key in lineage, f"{d}: lineage.{key} missing"
            # Every lineage ref must have id+version
            for k, v in lineage.items():
                if k == "measures":
                    for m in v:
                        assert "id" in m and "version" in m, f"{d}: measure {m} missing id/version"
                else:
                    assert "id" in v and "version" in v, f"{d}: lineage.{k} missing id/version"

    def test_every_result_has_six_axis_compatibility(self):
        """AC-AM03-14: compatibility declaration must declare all six axes."""
        for d, p in RESULT_PATHS.items():
            with open(p) as fh:
                doc = yaml.safe_load(fh)
            comp = doc.get("compatibility")
            assert comp is not None, f"{d}: compatibility missing"
            for axis in REQUIRED_AXES:
                assert axis in comp, f"{d}: compatibility.{axis} missing"
                assert comp[axis] in ("compatible", "incompatible"), f"{d}: {axis}={comp[axis]!r}"

    def test_every_migrated_result_identifies_its_execution(self):
        """AC-AM03-12/16: every result is traceable to the completed execution."""
        for d, p in RESULT_PATHS.items():
            with open(p) as fh:
                result = yaml.safe_load(fh)
            execution = yaml.safe_load(EXECUTION_PATHS[d].read_text())
            execution_ref = result.get("assessment_execution", {}).get("id")
            assert execution_ref is not None, f"{d}: assessment_execution missing"
            assert execution_ref == execution["id"], f"{d}: execution reference drift"

            for ref_key in ("assessment_model", "assessment_instrument", "capability", "scenario", "scoring_model", "maturity_model"):
                ref = result["lineage"].get(ref_key)
                assert ref and ref.get("id") and ref.get("version"), f"{d}: incomplete lineage.{ref_key}"
            assert result["lineage"]["assessment_execution"]["id"] == execution_ref

    def test_each_result_records_its_source_response_vector(self):
        """AC-AM03-18: worked results are reproducible from a fixed response vector."""
        for d, p in RESULT_PATHS.items():
            with open(p) as fh:
                result = yaml.safe_load(fh)
            responses = {r["question_id"]: r["value"] for r in result.get("source_responses", [])}
            assert responses, f"{d}: source response vector missing"
            for score in result.get("scores", []):
                dimension = score["dimension"]
                values = [
                    responses[q["question_id"]]
                    for q in result.get("source_responses", [])
                    if q["question_id"].split("-q", 1)[0] == dimension
                ]
                assert values, f"{d}: no source responses for {dimension}"
                assert score["value"] == round(sum(values) / len(values), 1), (
                    f"{d}: score is not reproducible from source responses"
                )

    def test_every_migrated_result_carries_benchmark_eligibility(self):
        """AC-AM03-18: eligibility is explicit but no ranking is calculated."""
        for d, p in RESULT_PATHS.items():
            with open(p) as fh:
                result = yaml.safe_load(fh)
            eligibility = result.get("benchmark_eligibility")
            assert eligibility is not None, f"{d}: benchmark_eligibility missing"
            assert eligibility.get("status") in ("eligible", "not-comparable", "insufficient-data", "provisional")
            assert "percentile" not in eligibility and "rank" not in eligibility, (
                f"{d}: CR-AM-03 prohibits calculated benchmark position in eligibility"
            )


if __name__ == "__main__":
    import unittest
    unittest.main(verbosity=2)
