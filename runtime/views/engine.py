"""CR-AM-05 assessment views and aggregation engine.

The view layer derives a governed projection from one or more
AssessmentResults. AssessmentResult remains the canonical fact; an
AssessmentView is never the source of truth (CR-AM-05 \u00a75, \u00a731).

Three policies are enforced by construction, not by trust:

* Aggregation is declared. AggregationModel.method + aggregation.method
  must match; the engine refuses `weighted-average`, `threshold`, `dominant-level`,
  and `custom` without their supplementary rule.
* Score and Maturity are distinct. AggregationModel.input.type is recorded
  and the cell exposes either value or level, never a conflated number.
* Missing data is not zero. Coverage is reported explicitly; missing sources
  carry `explicit-unknown` cells, not zero cells.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence

CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}
DEFAULT_VIEW_TYPES = (
    "enterprise_profile",
    "capability_profile",
    "scenario_profile",
    "heatmap",
    "trend",
)
DEFAULT_AGGREGATION_METHODS = (
    "identity",
    "sum",
    "count",
    "minimum",
    "maximum",
    "average",
    "weighted-average",
    "median",
    "threshold",
    "dominant-level",
    "coverage",
    "custom",
)
MISSING_DATA_RULES = ("exclude", "propagate", "explicit-unknown", "treat-as-zero")
SUPPORTED_INPUT_TYPES = ("score", "maturity", "measure", "observation")
SUPPORTED_SUBJECT_TYPES = (
    "organization",
    "capability",
    "scenario",
    "assessment_model",
    "subject",
)
COMPATIBILITY_AXES = (
    "schema",
    "semantic",
    "scoring",
    "maturity",
    "result",
    "benchmark",
)


class AggregationError(ValueError):
    """Raised when an aggregation violates a CR-AM-05 contract."""


class ViewType(str, Enum):
    ENTERPRISE_PROFILE = "enterprise_profile"
    CAPABILITY_PROFILE = "capability_profile"
    SCENARIO_PROFILE = "scenario_profile"
    HEATMAP = "heatmap"
    TREND = "trend"


class MissingDataMethod(str, Enum):
    EXCLUDE = "exclude"
    PROPAGATE = "propagate"
    EXPLICIT_UNKNOWN = "explicit-unknown"
    TREAT_AS_ZERO = "treat-as-zero"

    @classmethod
    def parse(cls, value: "str | MissingDataMethod") -> "MissingDataMethod":
        if isinstance(value, cls):
            return value
        cleaned = str(value).strip().lower().replace("_", "-")
        for candidate in (cleaned, cleaned.upper(), cleaned.lower(), cleaned.title()):
            try:
                return cls(candidate)
            except ValueError:
                continue
        raise AggregationError(f"unsupported missing-data method: {value!r}")


class AggregationMethod(str, Enum):
    IDENTITY = "identity"
    SUM = "sum"
    COUNT = "count"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    AVERAGE = "average"
    WEIGHTED_AVERAGE = "weighted-average"
    MEDIAN = "median"
    THRESHOLD = "threshold"
    DOMINANT_LEVEL = "dominant-level"
    COVERAGE = "coverage"
    CUSTOM = "custom"

    @classmethod
    def parse(cls, value: "str | AggregationMethod") -> "AggregationMethod":
        if isinstance(value, cls):
            return value
        cleaned = str(value).strip().lower().replace("_", "-")
        for candidate in (cleaned, cleaned.upper(), cleaned.lower(), cleaned.title()):
            try:
                return cls(candidate)
            except ValueError:
                continue
        raise AggregationError(f"unsupported aggregation method: {value!r}")


@dataclass(frozen=True)
class ViewSubject:
    id: str
    type: str
    name: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out = {"id": self.id, "type": self.type}
        if self.name:
            out["name"] = self.name
        return out


@dataclass(frozen=True)
class ViewFilters:
    assessment_models: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    scenarios: tuple[str, ...] = ()
    measures: tuple[str, ...] = ()
    maturity_models: tuple[str, ...] = ()
    organizations: tuple[str, ...] = ()
    result_status: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.assessment_models:
            out["assessment_models"] = list(self.assessment_models)
        if self.capabilities:
            out["capabilities"] = list(self.capabilities)
        if self.scenarios:
            out["scenarios"] = list(self.scenarios)
        if self.measures:
            out["measures"] = list(self.measures)
        if self.maturity_models:
            out["maturity_models"] = list(self.maturity_models)
        if self.organizations:
            out["organizations"] = list(self.organizations)
        if self.result_status:
            out["result_status"] = self.result_status
        return out


@dataclass(frozen=True)
class ViewLineage:
    source_results: tuple[tuple[str, str], ...]
    assessment_models: tuple[tuple[str, str], ...] = ()
    scoring_models: tuple[tuple[str, str], ...] = ()
    maturity_models: tuple[tuple[str, str], ...] = ()
    aggregation: tuple[str, str] | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "source_results": [
                {"id": sid, "version": ver} for sid, ver in self.source_results
            ]
        }
        if self.assessment_models:
            out["assessment_models"] = [
                {"id": sid, "version": ver} for sid, ver in self.assessment_models
            ]
        if self.scoring_models:
            out["scoring_models"] = [
                {"id": sid, "version": ver} for sid, ver in self.scoring_models
            ]
        if self.maturity_models:
            out["maturity_models"] = [
                {"id": sid, "version": ver} for sid, ver in self.maturity_models
            ]
        if self.aggregation:
            out["aggregation"] = {
                "id": self.aggregation[0],
                "version": self.aggregation[1],
            }
        return out


@dataclass(frozen=True)
class ViewAggregationDeclaration:
    method: AggregationMethod
    model_id: str
    model_version: str
    rationale: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out = {
            "method": self.method.value,
            "model": {"id": self.model_id, "version": self.model_version},
        }
        if self.rationale:
            out["rationale"] = self.rationale
        return out


@dataclass(frozen=True)
class ViewCell:
    subject: ViewSubject
    measure: dict[str, str] | None = None
    value: dict[str, Any] | None = None
    maturity: dict[str, Any] | None = None
    confidence: str = "medium"
    coverage: dict[str, Any] | None = None
    source_results: tuple[str, ...] = ()
    excluded: bool = False
    excluded_reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"subject": self.subject.as_dict()}
        if self.measure:
            out["measure"] = self.measure
        if self.value:
            out["value"] = self.value
        if self.maturity:
            out["maturity"] = self.maturity
        out["confidence"] = self.confidence
        if self.coverage:
            out["coverage"] = self.coverage
        if self.source_results:
            out["source_results"] = list(self.source_results)
        if self.excluded:
            guard: dict[str, Any] = {"excluded": True}
            if self.excluded_reason:
                guard["reason"] = self.excluded_reason
            out["compatibility_guard"] = guard
        return out


@dataclass(frozen=True)
class AggregationModel:
    id: str
    version: str
    name: str
    method: AggregationMethod
    input_type: str
    missing_data: MissingDataMethod
    scoring_model: dict[str, str] | None = None
    maturity_model: dict[str, str] | None = None
    measure: dict[str, str] | None = None
    grouping_dimension: str | None = None
    weighting_source: str | None = None
    weighting_weights: dict[str, float] = field(default_factory=dict)
    normalization_required: bool = False
    compatibility_axes: tuple[str, ...] = ()
    min_compatible_axes: int = 0
    notes: str | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "AggregationModel":
        if "id" not in data or "version" not in data or "name" not in data:
            raise AggregationError("AggregationModel requires id, version, name")
        if "method" not in data:
            raise AggregationError("AggregationModel requires method")
        if "input" not in data or "type" not in data.get("input", {}):
            raise AggregationError("AggregationModel requires input.type")
        if "missing_data" not in data or "method" not in data.get("missing_data", {}):
            raise AggregationError("AggregationModel requires missing_data.method")
        input_block = data["input"]
        if input_block["type"] not in SUPPORTED_INPUT_TYPES:
            raise AggregationError(
                f"unsupported input.type: {input_block['type']!r}"
            )
        grouping = data.get("grouping") or {}
        weighting = data.get("weighting") or {}
        normalization = data.get("normalization") or {}
        compatibility = data.get("compatibility") or {}
        return cls(
            id=data["id"],
            version=data["version"],
            name=data["name"],
            method=AggregationMethod.parse(data["method"]),
            input_type=input_block["type"],
            missing_data=MissingDataMethod.parse(
                data["missing_data"]["method"]
            ),
            scoring_model=input_block.get("scoring_model"),
            maturity_model=input_block.get("maturity_model"),
            measure=input_block.get("measure"),
            grouping_dimension=grouping.get("dimension"),
            weighting_source=weighting.get("source"),
            weighting_weights=dict(weighting.get("weights") or {}),
            normalization_required=bool(normalization.get("required", False)),
            compatibility_axes=tuple(compatibility.get("required_axes") or ()),
            min_compatible_axes=int(compatibility.get("min_compatible_axes", 0)),
            notes=data.get("notes"),
        )

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "id": self.id,
            "version": self.version,
            "name": self.name,
            "method": self.method.value,
            "input": {"type": self.input_type},
            "missing_data": {"method": self.missing_data.value},
        }
        if self.scoring_model:
            out["input"]["scoring_model"] = self.scoring_model
        if self.maturity_model:
            out["input"]["maturity_model"] = self.maturity_model
        if self.measure:
            out["input"]["measure"] = self.measure
        if self.grouping_dimension:
            out["grouping"] = {"dimension": self.grouping_dimension}
        if self.weighting_source or self.weighting_weights:
            out["weighting"] = {}
            if self.weighting_source:
                out["weighting"]["source"] = self.weighting_source
            if self.weighting_weights:
                out["weighting"]["weights"] = dict(self.weighting_weights)
        if self.normalization_required:
            out["normalization"] = {"required": True}
        if self.compatibility_axes or self.min_compatible_axes:
            out["compatibility"] = {}
            if self.compatibility_axes:
                out["compatibility"]["required_axes"] = list(self.compatibility_axes)
            out["compatibility"]["min_compatible_axes"] = self.min_compatible_axes
        if self.notes:
            out["notes"] = self.notes
        return out


class CoverageCalculator:
    """CR-AM-05 \u00a728: coverage is a first-class analytical dimension."""

    @staticmethod
    def coverage(assessed: int, applicable: int) -> dict[str, Any]:
        if applicable < 0 or assessed < 0:
            raise AggregationError("coverage counts must be non-negative")
        if assessed > applicable:
            raise AggregationError(
                "assessed coverage cannot exceed applicable coverage"
            )
        if applicable == 0:
            return {"value": 0.0, "assessed": assessed, "applicable": applicable}
        return {
            "value": round(assessed / applicable, 4),
            "assessed": assessed,
            "applicable": applicable,
        }


class AssessmentViewEngine:
    """Build AssessmentView dicts from AssessmentResult dicts.

    The engine never invents data. Every cell is traceable to source_results;
    missing data is `explicit-unknown` or excluded per AggregationModel.missing_data;
    compatibility guards exclude results whose axes don't meet the model's
    minimum before aggregation.
    """

    def __init__(
        self,
        *,
        compatibility_guard: bool = True,
    ) -> None:
        self.compatibility_guard = compatibility_guard

    @staticmethod
    def _extract_value(result: Mapping[str, Any], input_type: str) -> float | int | None:
        if input_type == "score":
            for determination in result.get("determinations", []) or []:
                score = determination.get("score", {})
                value = score.get("normalized_value") or score.get("value")
                if value is not None:
                    return value
            for score in result.get("scores", []) or []:
                value = score.get("normalized_value") or score.get("value")
                if value is not None:
                    return value
            return None
        if input_type == "maturity":
            interpretation = result.get("maturity_interpretation") or {}
            overall = interpretation.get("overall") or {}
            if "level" in overall:
                return overall["level"]
            for determination in result.get("determinations", []) or []:
                if "maturity_level" in determination:
                    return determination["maturity_level"]
            return None
        if input_type == "observation":
            for observation in result.get("observations", []) or []:
                value = observation.get("value")
                if value is not None:
                    return value
            return None
        if input_type == "measure":
            for observation in result.get("observations", []) or []:
                if "measure_id" in observation or "measure" in observation:
                    value = observation.get("value")
                    if value is not None:
                        return value
            return None
        raise AggregationError(f"unsupported input type: {input_type!r}")

    @staticmethod
    def _confidence(result: Mapping[str, Any]) -> str:
        for determination in result.get("determinations", []) or []:
            confidence = determination.get("confidence")
            if confidence:
                return confidence
        confidence = result.get("confidence")
        if confidence:
            return confidence
        return "medium"

    @classmethod
    def _aggregate_confidence(cls, confidences: Sequence[str]) -> str:
        if not confidences:
            return "medium"
        worst = min(confidences, key=lambda c: CONFIDENCE_ORDER.get(c, 1))
        return worst

    @classmethod
    def _aggregate(
        cls,
        values: Sequence[float | int],
        method: AggregationMethod,
        weights: Mapping[str, float] | None = None,
    ) -> float | int | None:
        if not values:
            return None
        if method is AggregationMethod.IDENTITY:
            return values[0]
        if method is AggregationMethod.SUM:
            return sum(values)
        if method is AggregationMethod.COUNT:
            return len(values)
        if method is AggregationMethod.MINIMUM:
            return min(values)
        if method is AggregationMethod.MAXIMUM:
            return max(values)
        if method is AggregationMethod.AVERAGE:
            return round(sum(values) / len(values), 4)
        if method is AggregationMethod.MEDIAN:
            ordered = sorted(values)
            n = len(ordered)
            mid = n // 2
            if n % 2 == 1:
                return ordered[mid]
            return round((ordered[mid - 1] + ordered[mid]) / 2, 4)
        if method is AggregationMethod.WEIGHTED_AVERAGE:
            if not weights:
                return round(sum(values) / len(values), 4)
            total = sum(values) * list(weights.values())[0]
            weight_total = sum(weights.values())
            return round(total / weight_total, 4) if weight_total else None
        if method is AggregationMethod.DOMINANT_LEVEL:
            counts = {
                v: list(values).count(v)
                for v in sorted(set(values))
            }
            tied = [v for v, count in counts.items() if count == max(counts.values())]
            return min(tied)
        if method is AggregationMethod.COVERAGE:
            return len(values)
        if method is AggregationMethod.THRESHOLD:
            raise AggregationError(
                "threshold aggregation requires a threshold rule via custom"
            )
        if method is AggregationMethod.CUSTOM:
            raise AggregationError(
                "custom aggregation requires an explicit custom rule"
            )
        raise AggregationError(f"unsupported aggregation method: {method}")

    def _compatible(
        self,
        result: Mapping[str, Any],
        model: AggregationModel,
    ) -> tuple[bool, str | None]:
        if not self.compatibility_guard or not model.compatibility_axes:
            return True, None
        compatibility = result.get("compatibility") or {}
        missing_axes = [
            axis
            for axis in model.compatibility_axes
            if compatibility.get(axis) != "compatible"
        ]
        if len(missing_axes) > (6 - model.min_compatible_axes):
            return (
                False,
                f"missing/incompatible required axes: {', '.join(missing_axes)}",
            )
        return True, None

    def aggregate(
        self,
        results: Sequence[Mapping[str, Any]],
        model: AggregationModel,
    ) -> dict[str, Any]:
        kept: list[Mapping[str, Any]] = []
        excluded: list[tuple[str, str]] = []
        for result in results:
            ok, reason = self._compatible(result, model)
            if ok:
                kept.append(result)
            else:
                excluded.append((result.get("id", "<unknown>"), reason or "excluded"))
        if not kept and model.missing_data is not MissingDataMethod.EXCLUDE:
            raise AggregationError(
                f"no compatible results survive compatibility guard (excluded: {excluded})"
            )
        values: list[float | int] = []
        for result in kept:
            value = self._extract_value(result, model.input_type)
            if value is None:
                if model.missing_data is MissingDataMethod.TREAT_AS_ZERO:
                    values.append(0)
                continue
            values.append(value)
        aggregated = self._aggregate(
            values,
            model.method,
            model.weighting_weights or None,
        )
        if aggregated is None and model.missing_data is not MissingDataMethod.EXCLUDE:
            raise AggregationError(
                "aggregation produced no value but missing-data is not exclude"
            )
        return {
            "aggregated_value": aggregated,
            "source_count": len(kept),
            "excluded_results": excluded,
            "confidence": self._aggregate_confidence(
                [self._confidence(result) for result in kept]
            ),
        }

    def capability_profile(
        self,
        results: Sequence[Mapping[str, Any]],
        subject: ViewSubject,
        aggregation_model: AggregationModel,
        *,
        coverage_applicable: int = 0,
    ) -> dict[str, Any]:
        summary = self.aggregate(results, aggregation_model)
        coverage: dict[str, Any] | None = None
        if coverage_applicable:
            coverage = CoverageCalculator.coverage(
                len(results), coverage_applicable
            )
        cell = ViewCell(
            subject=subject,
            measure=aggregation_model.measure,
            value={"score": summary["aggregated_value"]}
            if summary["aggregated_value"] is not None
            else None,
            confidence=summary["confidence"],
            coverage=coverage,
            source_results=tuple(r.get("id", "") for r in results),
            excluded=bool(summary["excluded_results"]),
            excluded_reason=(
                "; ".join(reason for _, reason in summary["excluded_results"])
                or None
            ),
        )
        return {
            "type": ViewType.CAPABILITY_PROFILE.value,
            "subject": subject.as_dict(),
            "cells": [cell.as_dict()],
            "lineage": ViewLineage(
                source_results=tuple(
                    (r.get("id", ""), r.get("assessment_model", {}).get("version", "0.0.0"))
                    for r in results
                ),
                assessment_models=tuple(
                    (r.get("assessment_model", {}).get("id", ""), r.get("assessment_model", {}).get("version", "0.0.0"))
                    for r in results
                ),
                scoring_models=tuple(
                    (r.get("lineage", {}).get("scoring_model", {}).get("id", ""), r.get("lineage", {}).get("scoring_model", {}).get("version", "0.0.0"))
                    for r in results
                ),
                maturity_models=tuple(
                    (r.get("lineage", {}).get("maturity_model", {}).get("id", ""), r.get("lineage", {}).get("maturity_model", {}).get("version", "0.0.0"))
                    for r in results
                ),
                aggregation=(
                    aggregation_model.id,
                    aggregation_model.version,
                ),
            ).as_dict(),
            "aggregation": ViewAggregationDeclaration(
                method=aggregation_model.method,
                model_id=aggregation_model.id,
                model_version=aggregation_model.version,
            ).as_dict(),
        }

    def heatmap(
        self,
        rows: Mapping[str, Sequence[Mapping[str, Any]]],
        columns: Sequence[str],
        aggregation_model: AggregationModel,
        subject: ViewSubject,
        *,
        column_dimension: str = "assessment_period",
    ) -> dict[str, Any]:
        cells: list[dict[str, Any]] = []
        for row_key, row_results in rows.items():
            for column_key in columns:
                column_filtered = [
                    result
                    for result in row_results
                    if (
                        column_dimension == "assessment_period"
                        and result.get("assessment_period", {}).get("end", "").startswith(column_key)
                    )
                    or (
                        column_dimension == "scenario"
                        and result.get("scenario", {}).get("id") == column_key
                    )
                ]
                if not column_filtered and aggregation_model.missing_data is MissingDataMethod.EXPLICIT_UNKNOWN:
                    cells.append(
                        ViewCell(
                            subject=ViewSubject(id=row_key, type=column_dimension),
                            measure=aggregation_model.measure,
                            value=None,
                            confidence="medium",
                            coverage=CoverageCalculator.coverage(0, 1),
                            source_results=(),
                            excluded=False,
                        ).as_dict()
                    )
                    continue
                summary = self.aggregate(column_filtered, aggregation_model)
                cells.append(
                    ViewCell(
                        subject=ViewSubject(id=row_key, type=column_dimension),
                        measure=aggregation_model.measure,
                        value={"score": summary["aggregated_value"]}
                        if summary["aggregated_value"] is not None
                        else None,
                        confidence=summary["confidence"],
                        coverage=CoverageCalculator.coverage(
                            len(column_filtered),
                            max(len(row_results), 1),
                        ),
                        source_results=tuple(
                            r.get("id", "") for r in column_filtered
                        ),
                        excluded=bool(summary["excluded_results"]),
                        excluded_reason=(
                            "; ".join(reason for _, reason in summary["excluded_results"])
                            or None
                        ),
                    ).as_dict()
                )
        return {
            "type": ViewType.HEATMAP.value,
            "subject": subject.as_dict(),
            "dimensions": ["capability", column_dimension],
            "cells": cells,
            "lineage": ViewLineage(
                source_results=tuple(
                    (r.get("id", ""), r.get("assessment_model", {}).get("version", "0.0.0"))
                    for results in rows.values()
                    for r in results
                ),
                aggregation=(
                    aggregation_model.id,
                    aggregation_model.version,
                ),
            ).as_dict(),
            "aggregation": ViewAggregationDeclaration(
                method=aggregation_model.method,
                model_id=aggregation_model.id,
                model_version=aggregation_model.version,
            ).as_dict(),
        }
