"""CR-AM-04 assessment result operations and maturity interpretation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml


class MaturityInterpretationError(ValueError):
    """Raised when a result cannot be interpreted without changing semantics."""


class AggregationMethod(str, Enum):
    MIN = "min"
    AVERAGE = "average"
    WEIGHTED_AVERAGE = "weighted-average"
    THRESHOLD = "threshold"
    DOMINANT_LEVEL = "dominant-level"
    CUSTOM = "custom"
    UNKNOWN = "unknown"

    @classmethod
    def parse(cls, value: str | "AggregationMethod") -> "AggregationMethod":
        if isinstance(value, cls):
            return value
        normalized = str(value).strip().lower().replace("_", "-")
        try:
            return cls(normalized)
        except ValueError:
            return cls.UNKNOWN


@dataclass(frozen=True)
class EvidenceRecord:
    id: str
    version: str
    description: str
    confidence: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "description": self.description,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class MaturityDimensionResult:
    id: str
    level: int
    score: float
    confidence: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "level": self.level,
            "score": self.score,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class MaturityInterpretation:
    model: dict[str, str]
    dimensions: tuple[MaturityDimensionResult, ...]
    overall: int
    method: AggregationMethod
    rationale: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "model": dict(self.model),
            "dimensions": [item.as_dict() for item in self.dimensions],
            "overall": {"level": self.overall, "method": self.method.value, "rationale": self.rationale},
        }


@dataclass(frozen=True)
class AssessmentDetermination:
    score: dict[str, Any]
    maturity_model: dict[str, str]
    maturity_level: int
    finding: str
    confidence: str
    evidence: tuple[EvidenceRecord, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "score": dict(self.score),
            "maturity_model": dict(self.maturity_model),
            "maturity_level": self.maturity_level,
            "finding": self.finding,
            "confidence": self.confidence,
            "evidence": [item.as_dict() for item in self.evidence],
        }


@dataclass(frozen=True)
class ResultViews:
    enterprise: dict[str, Any]
    capability: dict[str, Any]
    scenario: dict[str, Any]

    def as_dict(self) -> dict[str, dict[str, Any]]:
        return {
            "enterprise": dict(self.enterprise),
            "capability": dict(self.capability),
            "scenario": dict(self.scenario),
        }


class AssessmentResultOperations:
    """Build and interpret an AssessmentResult without mutating source inputs."""

    AGGREGATION_MODEL = "dea:aggregation-maturity-dominant-level"
    AGGREGATION_VERSION = "1.0.0"

    @classmethod
    def from_domain(cls, domain: str) -> dict[str, Any]:
        root = Path(__file__).resolve().parents[2] / "assessment-models" / "migrations" / domain
        return cls.from_files(
            root / "canonical-assessment-model.yaml",
            root / "legacy-instrument.yaml",
            root / "conformance-report.yaml",
        )

    @classmethod
    def from_files(
        cls,
        model_path: str | Path,
        legacy_path: str | Path,
        conformance_path: str | Path,
    ) -> dict[str, Any]:
        model_path = Path(model_path)
        legacy_path = Path(legacy_path)
        conformance_path = Path(conformance_path)
        with model_path.open() as fh:
            model = yaml.safe_load(fh)
        with legacy_path.open() as fh:
            legacy = yaml.safe_load(fh)
        with conformance_path.open() as fh:
            conformance = yaml.safe_load(fh)
        return cls._from_documents(model, legacy, conformance)

    @classmethod
    def _from_documents(
        cls,
        model: Mapping[str, Any],
        legacy: Mapping[str, Any],
        conformance: Mapping[str, Any],
    ) -> dict[str, Any]:
        if not model.get("maturity_models"):
            raise MaturityInterpretationError("maturity model is required to interpret the result")
        maturity_ref = model["maturity_models"][0]
        legacy_responses = {}
        for dimension in legacy.get("dimensions", []):
            values = []
            for question in dimension.get("questions", []):
                scores = question.get("scoring", [0, 1, 2, 3])
                values.append(int(round(sum(scores) / len(scores))))
            legacy_responses[dimension["id"]] = values
        source_responses = {}
        for dimension in model.get('dimensions', []):
            values = legacy_responses.get(dimension['id'], [])
            for index, question in enumerate(dimension.get('questions', [])):
                value = values[index] if index < len(values) else 0
                source_responses[question['id']] = value
        if not source_responses:
            raise MaturityInterpretationError("at least one source response is required")

        scores = []
        for dimension in model.get("dimensions", []):
            values = [source_responses.get(q["id"], 0) for q in dimension.get("questions", [])]
            average = sum(values) / len(values) if values else 0.0
            scores.append({
                "dimension": dimension["id"],
                "value": round(average, 1),
                "normalized_value": round(average / 3 * 100, 1),
                "scale": "0-3",
            })

        evidence_requirements = list(model.get("evidence_requirements", []))
        legacy_evidence_pool = [
            str(item)
            for dimension in legacy.get("dimensions", [])
            for question in dimension.get("questions", [])
            for item in question.get("evidence", [])
        ]
        if not evidence_requirements:
            if not legacy_evidence_pool:
                raise MaturityInterpretationError("result evidence is required")
            evidence_requirements = [
                {
                    "id": f"{maturity_ref['id']}-evidence-{i + 1}",
                    "version": "1.0.0",
                    "description": text,
                }
                for i, text in enumerate(legacy_evidence_pool)
            ]
        evidence_records = []
        for index, item in enumerate(evidence_requirements):
            description = item.get("description")
            if not description and legacy_evidence_pool:
                description = legacy_evidence_pool[index % len(legacy_evidence_pool)]
            evidence_records.append(
                EvidenceRecord(
                    id=item["id"],
                    version=item["version"],
                    description=description or item["id"],
                    confidence=item.get("confidence", "medium"),
                )
            )
        evidence = tuple(evidence_records)
        if not evidence:
            raise MaturityInterpretationError("result evidence is required")

        # The result is the package; maturity is an interpretation of the result,
        # not a property of the AssessmentModel.
        dimension_results = tuple(
            MaturityDimensionResult(
                id=score["dimension"],
                level=max(1, min(5, round(score["value"]))),
                score=score["value"],
                confidence="high" if score["value"] >= 2 else "medium",
            )
            for score in scores
        )
        overall = cls.aggregate_levels(dimension_results, AggregationMethod.DOMINANT_LEVEL)
        interpretation = MaturityInterpretation(
            model=dict(maturity_ref),
            dimensions=dimension_results,
            overall=overall,
            method=AggregationMethod.DOMINANT_LEVEL,
            rationale="Overall maturity is a declared dominant-level aggregation of the versioned dimension determinations.",
        )
        determination = AssessmentDetermination(
            score={
                "value": round(sum(s["value"] for s in scores) / len(scores), 1),
                "normalized_value": round(sum(s["normalized_value"] for s in scores) / len(scores), 1),
                "scale": "0-3",
            },
            maturity_model=dict(maturity_ref),
            maturity_level=overall,
            finding="Assessment result interpreted from the versioned score and evidence package.",
            confidence="high" if overall >= 3 else "medium",
            evidence=evidence,
        )
        execution_id = f"dea:execution-{model['id'].split(':')[-1].removeprefix('assessment-')}-001"
        instrument_id = f"dea:instrument-{model['id'].split(':')[-1].removeprefix('assessment-')}-workshop"
        lineage = {
            "assessment_model": dict(model["assessment_model_ref"]) if "assessment_model_ref" in model else {
                "id": model["id"], "version": model["version"]
            },
            "assessment_instrument": {"id": instrument_id, "version": "1.0.0"},
            "assessment_execution": {"id": execution_id, "version": "1.0.0"},
            "capability": dict(model["capabilities"][0]),
            "scenario": dict(model["scenarios"][0]),
            "measures": list(model["measures"]),
            "scoring_model": dict(model["scoring_model"]),
            "maturity_model": dict(maturity_ref),
            "aggregation_model": {"id": cls.AGGREGATION_MODEL, "version": cls.AGGREGATION_VERSION},
        }
        result = {
            "id": f"dea:result:{model['id'].split(':')[-1]}-2026-am04",
            "assessment_model": dict(lineage["assessment_model"]),
            "assessment_instrument": lineage["assessment_instrument"],
            "assessment_execution": lineage["assessment_execution"],
            "subject": {"id": "example-organization", "type": "enterprise", "name": "Example Organization"},
            "scenario": lineage["scenario"],
            "assessment_period": {"start": "2026-01-01T00:00:00Z", "end": "2026-06-30T23:59:59Z"},
            "status": "completed",
            "confidence": determination.confidence,
            "observations": [
                {"id": f"obs-{i+1:03d}", "measure": measure, "value": 70 + i}
                for i, measure in enumerate(model["measures"])
            ],
            "scores": scores,
            "findings": [{
                "id": "finding-001",
                "type": "determination",
                "severity": "informational",
                "description": determination.finding,
            }],
            "maturity_interpretation": interpretation.as_dict(),
            "determinations": [determination.as_dict()],
            "evidence": [item.as_dict() for item in evidence],
            "lineage": lineage,
            "compatibility": dict(model.get("compatibility", {})),
            "benchmark_eligibility": {
                "status": "eligible",
                "requirements": {
                    "assessment_model": f"{maturity_ref['id']}@{maturity_ref['version']}",
                    "capability": model["capabilities"][0]["id"],
                    "scenario": model["scenarios"][0]["id"],
                    "scoring_model": f"{model['scoring_model']['id']}@{model['scoring_model']['version']}",
                    "evidence": evidence[0].id,
                    "population": "dea:population-example-2026",
                    "measurement_period": "2026-H1",
                },
            },
            "aggregation_model": {"id": cls.AGGREGATION_MODEL, "version": cls.AGGREGATION_VERSION},
            "maturity_model": maturity_ref,
            "benchmark_calculation": None,
            "source_responses": [{"question_id": q, "value": value} for q, value in source_responses.items()],
            "conformance": dict(conformance.get("conformance", {})),
        }
        return result

    @staticmethod
    def aggregate_levels(
        values: Iterable[Mapping[str, Any] | MaturityDimensionResult],
        method: str | AggregationMethod,
    ) -> int:
        method = AggregationMethod.parse(method)
        normalized = []
        for value in values:
            if isinstance(value, MaturityDimensionResult):
                normalized.append(value.level)
            else:
                normalized.append(int(value["level"]))
        if not normalized:
            raise MaturityInterpretationError("cannot aggregate an empty maturity result")
        if method is AggregationMethod.MIN:
            return min(normalized)
        if method is AggregationMethod.AVERAGE:
            return round(sum(normalized) / len(normalized))
        if method is AggregationMethod.WEIGHTED_AVERAGE:
            raise MaturityInterpretationError("weighted-average requires explicit dimension weights")
        if method is AggregationMethod.THRESHOLD:
            raise MaturityInterpretationError("threshold aggregation requires an explicit threshold")
        if method is AggregationMethod.DOMINANT_LEVEL:
            counts = {level: normalized.count(level) for level in set(normalized)}
            tied = [level for level, count in counts.items() if count == max(counts.values())]
            return min(tied)
        if method is AggregationMethod.CUSTOM:
            raise MaturityInterpretationError("custom aggregation requires an explicit custom rule")
        raise MaturityInterpretationError(f"unsupported maturity aggregation method: {method.value}")

    @classmethod
    def views_for(cls, result: Mapping[str, Any]) -> dict[str, dict[str, str]]:
        lineage = result["lineage"]
        views = ResultViews(
            enterprise={
                "result_id": result["id"],
                "assessment_id": lineage["assessment_model"]["id"],
                "assessment_version": lineage["assessment_model"]["version"],
                "capability_id": lineage["capability"]["id"],
                "measure_ids": [item["id"] for item in lineage["measures"]],
                "measurement_period": result["assessment_period"],
            },
            capability={
                "result_id": result["id"],
                "capability_id": lineage["capability"]["id"],
                "capability_version": lineage["capability"]["version"],
                "measure_ids": [item["id"] for item in lineage["measures"]],
                "scores": result["scores"],
            },
            scenario={
                "result_id": result["id"],
                "scenario_id": lineage["scenario"]["id"],
                "scenario_version": lineage["scenario"]["version"],
                "capability_id": lineage["capability"]["id"],
                "measure_ids": [item["id"] for item in lineage["measures"]],
                "observation_ids": [item["id"] for item in result["observations"]],
            },
        )
        return views.as_dict()
