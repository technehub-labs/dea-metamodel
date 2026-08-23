"""CR-AM-06 benchmark eligibility engine.

Eligibility is a governed determination about the comparability of an
AssessmentResult; it is not a property inferred from the existence of a
score or maturity level (CR-AM-06 §15).

The engine answers one question — "can this result legitimately
participate in a cross-organisation comparison within this cohort?"
(CR-AM-06 objective). It deliberately does NOT answer "how do we compare
it?" — percentile, rank, quartile, and peer-position belong to CR-AM-07
(CR-AM-06 §10).

Four policies are enforced by construction, not by trust:

* Comparability is keyed. A result joins a cohort only when its
  canonical comparability key (scenario, capability, measure,
  assessment_model, scoring_model, maturity_model) is compatible with
  the cohort's required key on every dimension (CR-AM-06 §5).
* Failure is explained. Every non-eligible determination carries
  machine-actionable reason codes from vocabulary/eligibility-reasons.yaml
  (CR-AM-06 §4, §11).
* Statuses are distinct. not-eligible (fails a participation rule),
  not-comparable (no compatible population), insufficient-data (result
  lacks evidence/coverage), expired (outside temporal boundary), and
  provisional (conditional participation) are never conflated
  (CR-AM-06 §4).
* Determination is deterministic. The engine is a pure function of
  (result, cohort, compatibility declarations, subject attributes).
  Identical inputs always reproduce the historical determination
  (CR-AM-06 §14).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping, Optional, Sequence

CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}

BENCHMARK_STATUSES = (
    "eligible",
    "provisional",
    "not-eligible",
    "not-comparable",
    "insufficient-data",
    "expired",
)

ELIGIBILITY_REASONS = (
    "scenario-definition-mismatch",
    "capability-mismatch",
    "measure-mismatch",
    "assessment-model-incompatible",
    "scoring-model-incompatible",
    "maturity-model-incompatible",
    "period-mismatch",
    "version-incompatible",
    "evidence-insufficient",
    "coverage-insufficient",
    "confidence-below-threshold",
    "population-requirements-unmet",
    "result-expired",
)

# The twelve eligibility dimensions of CR-AM-06 §8.
ELIGIBILITY_DIMENSIONS = (
    "scenario",
    "capability",
    "measure",
    "assessment_model",
    "scoring_model",
    "maturity_model",
    "period",
    "evidence",
    "coverage",
    "confidence",
    "version",
    "population",
)

# Which failure class each reason belongs to. Mirrors the `produces`
# field of vocabulary/eligibility-reasons.yaml.
REASON_STATUS = {
    "scenario-definition-mismatch": "not-comparable",
    "capability-mismatch": "not-comparable",
    "measure-mismatch": "not-comparable",
    "assessment-model-incompatible": "not-comparable",
    "scoring-model-incompatible": "not-comparable",
    "maturity-model-incompatible": "not-comparable",
    "period-mismatch": "not-comparable",
    "version-incompatible": "not-comparable",
    "evidence-insufficient": "insufficient-data",
    "coverage-insufficient": "insufficient-data",
    "confidence-below-threshold": "not-eligible",
    "population-requirements-unmet": "not-eligible",
    "result-expired": "expired",
}

# Deterministic precedence between failure classes. A result whose own
# data is incomplete cannot meaningfully be compared; a result outside
# time cannot be evaluated at all.
STATUS_PRECEDENCE = (
    "expired",
    "insufficient-data",
    "not-comparable",
    "not-eligible",
)


class EligibilityError(ValueError):
    """Raised when an eligibility evaluation violates a CR-AM-06 contract."""


class EligibilityStatus(str, Enum):
    ELIGIBLE = "eligible"
    PROVISIONAL = "provisional"
    NOT_ELIGIBLE = "not-eligible"
    NOT_COMPARABLE = "not-comparable"
    INSUFFICIENT_DATA = "insufficient-data"
    EXPIRED = "expired"


class EligibilityReason(str, Enum):
    SCENARIO_DEFINITION_MISMATCH = "scenario-definition-mismatch"
    CAPABILITY_MISMATCH = "capability-mismatch"
    MEASURE_MISMATCH = "measure-mismatch"
    ASSESSMENT_MODEL_INCOMPATIBLE = "assessment-model-incompatible"
    SCORING_MODEL_INCOMPATIBLE = "scoring-model-incompatible"
    MATURITY_MODEL_INCOMPATIBLE = "maturity-model-incompatible"
    PERIOD_MISMATCH = "period-mismatch"
    VERSION_INCOMPATIBLE = "version-incompatible"
    EVIDENCE_INSUFFICIENT = "evidence-insufficient"
    COVERAGE_INSUFFICIENT = "coverage-insufficient"
    CONFIDENCE_BELOW_THRESHOLD = "confidence-below-threshold"
    POPULATION_REQUIREMENTS_UNMET = "population-requirements-unmet"
    RESULT_EXPIRED = "result-expired"


@dataclass(frozen=True)
class ComparabilityKey:
    """Canonical comparability identity of an AssessmentResult (§5)."""

    scenario: str
    capability: str
    measure: str
    assessment_model: str
    scoring_model: str
    maturity_model: str

    @classmethod
    def from_result(cls, result: Mapping[str, Any]) -> "ComparabilityKey":
        """Derive the comparability key from result lineage (§5).

        The lineage block (CR-AM-02 §12) is the authoritative source:
        it records the exact model versions used to produce the result.
        """
        lineage = result.get("lineage") or {}
        scenario = _ref_id(lineage.get("scenario"))
        capability = _ref_id(lineage.get("capability"))
        measures = lineage.get("measures") or []
        measure = _ref_id(measures[0]) if measures else None
        assessment_model = _ref_id(lineage.get("assessment_model"))
        scoring_model = _ref_id(lineage.get("scoring_model"))
        maturity_model = _ref_id(lineage.get("maturity_model"))
        missing = [
            name
            for name, value in (
                ("scenario", scenario),
                ("capability", capability),
                ("measure", measure),
                ("assessment_model", assessment_model),
                ("scoring_model", scoring_model),
                ("maturity_model", maturity_model),
            )
            if not value
        ]
        if missing:
            raise EligibilityError(
                f"cannot derive comparability key: missing lineage references {missing}"
            )
        assert scenario and capability and measure
        assert assessment_model and scoring_model and maturity_model
        return cls(
            scenario=scenario,
            capability=capability,
            measure=measure,
            assessment_model=assessment_model,
            scoring_model=scoring_model,
            maturity_model=maturity_model,
        )

    def as_dict(self) -> dict:
        return {
            "scenario": self.scenario,
            "capability": self.capability,
            "measure": self.measure,
            "assessment_model": self.assessment_model,
            "scoring_model": self.scoring_model,
            "maturity_model": self.maturity_model,
        }


@dataclass(frozen=True)
class CompatibilityDeclaration:
    """Explicit version-compatibility declaration between model versions (§9).

    Where versions differ, the result must carry an explicit declaration
    with basis; version-number proximity is never sufficient (§9).
    """

    model_id: str
    from_version: str
    to_version: str
    benchmark: str  # "compatible" | "incompatible"
    basis: str = "explicit-mapping"


@dataclass(frozen=True)
class EligibilityDetermination:
    """The governed outcome of evaluating a result against a cohort (§3)."""

    status: str
    reasons: tuple
    comparability_key: ComparabilityKey
    cohort_id: str
    eligibility: Mapping[str, bool]

    def as_benchmark_entry(self, benchmark_model: Mapping[str, Any]) -> dict:
        """Render as an AssessmentResult.benchmark[] entry (§3, §11).

        percentile, rank, and sample_size are never emitted — they are
        CR-AM-07 comparative-analytics fields (§10).
        """
        entry: dict[str, Any] = {
            "model": {
                "id": benchmark_model["id"],
                "version": benchmark_model["version"],
            },
            "status": self.status,
            "comparability": {"key": self.comparability_key.as_dict()},
            "eligibility": dict(self.eligibility),
            "cohort": {"id": self.cohort_id},
        }
        if self.reasons:
            entry["reasons"] = list(self.reasons)
        return entry


def _ref_id(ref: Any) -> Optional[str]:
    if isinstance(ref, Mapping):
        return ref.get("id")
    return None


def _ref_version(ref: Any) -> Optional[str]:
    if isinstance(ref, Mapping):
        return ref.get("version")
    return None


def _major(version: Optional[str]) -> Optional[int]:
    if not version:
        return None
    try:
        return int(str(version).split(".", 1)[0])
    except (ValueError, IndexError):
        return None


class BenchmarkEligibilityEngine:
    """Evaluate an AssessmentResult against a BenchmarkCohort (§1, §8).

    The engine evaluates all twelve §8 dimensions and groups failures by
    class. The final status is the highest-precedence non-empty failure
    class (STATUS_PRECEDENCE); reasons from every evaluated dimension are
    retained so consumers see the full picture.
    """

    def __init__(
        self,
        compatibility_declarations: Iterable[CompatibilityDeclaration] = (),
    ) -> None:
        self._declarations = {
            (d.model_id, d.from_version, d.to_version): d
            for d in compatibility_declarations
        }

    # -- dimension evaluation -------------------------------------------------

    def _versions_compatible(
        self,
        model_id: str,
        result_version: Optional[str],
        cohort_version: Optional[str],
    ) -> bool:
        """Version compatibility per §9.

        An explicit declaration always governs. In its absence, the
        CR-AM-02 §11 default-silent rule applies: same major version is
        compatible; a major-version boundary is not.
        """
        if result_version == cohort_version:
            return True
        decl = self._declarations.get(
            (model_id, result_version or "", cohort_version or "")
        )
        if decl is not None:
            return decl.benchmark == "compatible"
        r_major, c_major = _major(result_version), _major(cohort_version)
        if r_major is None or c_major is None:
            return False
        return r_major == c_major

    def evaluate(
        self,
        result: Mapping[str, Any],
        cohort: Mapping[str, Any],
        subject_attributes: Optional[Mapping[str, Any]] = None,
        provisional_condition_id: Optional[str] = None,
    ) -> EligibilityDetermination:
        """Evaluate one result against one cohort (§1).

        Parameters
        ----------
        result:
            The AssessmentResult (mapping) to evaluate.
        cohort:
            The BenchmarkCohort (mapping) to evaluate against.
        subject_attributes:
            Optional subject metadata used for the population dimension
            (e.g. {"segment": "telecom-operators"}). Population
            requirements cannot be verified from the result alone.
        provisional_condition_id:
            When given, and no hard failure exists, the determination is
            'provisional' under the named cohort condition (§4). The
            condition MUST be declared in the cohort's
            eligibility_criteria.conditions — provisional membership is
            never invented by the engine.
        """
        key = ComparabilityKey.from_result(result)
        required_key = cohort.get("comparability_key") or {}
        criteria = cohort.get("eligibility_criteria") or {}
        boundary = cohort.get("temporal_boundary") or {}
        reasons: list[str] = []
        flags: dict[str, bool] = {
            "evidence": True,
            "coverage": True,
            "confidence": True,
            "currency": True,
            "compatibility": True,
        }

        # -- currency + period (§8) -------------------------------------------
        period = result.get("assessment_period") or {}
        p_start, p_end = period.get("start"), period.get("end")
        w_start, w_end = boundary.get("start"), boundary.get("end")
        if result.get("status") == "superseded":
            reasons.append(EligibilityReason.RESULT_EXPIRED.value)
            flags["currency"] = False
        elif p_end and w_start and p_end < w_start:
            # Entirely before the window opens: stale (§4 expired).
            reasons.append(EligibilityReason.RESULT_EXPIRED.value)
            flags["currency"] = False
        elif p_start and w_end and p_start > w_end:
            reasons.append(EligibilityReason.PERIOD_MISMATCH.value)
        elif (
            p_start
            and p_end
            and w_start
            and w_end
            and not (w_start <= p_start and p_end <= w_end)
        ):
            # Current but not fully inside the comparison window (§8 Period).
            reasons.append(EligibilityReason.PERIOD_MISMATCH.value)

        # -- evidence (§8) -----------------------------------------------------
        min_evidence = criteria.get("minimum_evidence_records", 0)
        n_evidence = len(result.get("evidence") or [])
        if n_evidence < min_evidence:
            reasons.append(EligibilityReason.EVIDENCE_INSUFFICIENT.value)
            flags["evidence"] = False

        # -- coverage (§8) -----------------------------------------------------
        # Coverage = fraction of lineage-declared measures that carry at
        # least one observation. Missing sources are never treated as zero
        # (CR-AM-05) nor as eligible (CR-AM-06).
        min_coverage = criteria.get("minimum_coverage")
        if min_coverage is not None:
            measures = (result.get("lineage") or {}).get("measures") or []
            observed = {
                _ref_id((obs or {}).get("measure"))
                for obs in (result.get("observations") or [])
            }
            observed.discard(None)
            declared = {_ref_id(m) for m in measures}
            declared.discard(None)
            if not declared:
                coverage = 0.0
            else:
                coverage = len(declared & observed) / len(declared)
            if coverage < min_coverage:
                reasons.append(EligibilityReason.COVERAGE_INSUFFICIENT.value)
                flags["coverage"] = False

        # -- confidence (§8) ---------------------------------------------------
        min_confidence = criteria.get("minimum_confidence")
        if min_confidence is not None:
            have = CONFIDENCE_ORDER.get(result.get("confidence"), -1)
            need = CONFIDENCE_ORDER.get(min_confidence, 99)
            if have < need:
                reasons.append(EligibilityReason.CONFIDENCE_BELOW_THRESHOLD.value)
                flags["confidence"] = False

        # -- semantic dimensions (§5, §8) --------------------------------------
        dimension_reasons = {
            "scenario": EligibilityReason.SCENARIO_DEFINITION_MISMATCH.value,
            "capability": EligibilityReason.CAPABILITY_MISMATCH.value,
            "measure": EligibilityReason.MEASURE_MISMATCH.value,
            "assessment_model": EligibilityReason.ASSESSMENT_MODEL_INCOMPATIBLE.value,
            "scoring_model": EligibilityReason.SCORING_MODEL_INCOMPATIBLE.value,
            "maturity_model": EligibilityReason.MATURITY_MODEL_INCOMPATIBLE.value,
        }
        key_dict = key.as_dict()
        lineage = result.get("lineage") or {}
        for dim, reason in dimension_reasons.items():
            req = required_key.get(dim)
            if req is None:
                continue
            req_id = _ref_id(req)
            req_version = _ref_version(req)
            if req_id and key_dict[dim] != req_id:
                reasons.append(reason)
                flags["compatibility"] = False
                continue
            # Identity matches; check version compatibility (§9).
            if dim == "measure":
                res_refs = lineage.get("measures") or []
                res_version = _ref_version(res_refs[0]) if res_refs else None
            else:
                res_version = _ref_version(lineage.get(dim))
            if req_version and not self._versions_compatible(
                key_dict[dim], res_version, req_version
            ):
                reasons.append(reason)
                flags["compatibility"] = False

        # -- required result compatibility declaration (§9) --------------------
        required_compat = criteria.get("required_compatibility") or {}
        result_compat = result.get("compatibility") or {}
        for axis, required_value in required_compat.items():
            if required_value == "compatible" and result_compat.get(axis) == "incompatible":
                if EligibilityReason.VERSION_INCOMPATIBLE.value not in reasons:
                    reasons.append(EligibilityReason.VERSION_INCOMPATIBLE.value)
                flags["compatibility"] = False

        # -- population (§6, §8) -----------------------------------------------
        segment = ((cohort.get("definition") or {}).get("population_segment"))
        if segment:
            subject_segment = (subject_attributes or {}).get("segment")
            if subject_segment is not None and subject_segment != segment:
                reasons.append(EligibilityReason.POPULATION_REQUIREMENTS_UNMET.value)

        # -- determination (§4) ------------------------------------------------
        failing_classes = {
            REASON_STATUS[r] for r in reasons if r in REASON_STATUS
        }
        status: str = EligibilityStatus.ELIGIBLE.value
        for cls in STATUS_PRECEDENCE:
            if cls in failing_classes:
                status = cls
                break

        if status == EligibilityStatus.ELIGIBLE.value and provisional_condition_id:
            declared = {
                (c or {}).get("id")
                for c in (criteria.get("conditions") or [])
            }
            if provisional_condition_id not in declared:
                raise EligibilityError(
                    f"provisional condition {provisional_condition_id!r} is not "
                    f"declared in cohort {cohort.get('id')!r} eligibility_criteria.conditions"
                )
            status = EligibilityStatus.PROVISIONAL.value

        return EligibilityDetermination(
            status=status,
            reasons=tuple(reasons),
            comparability_key=key,
            cohort_id=str(cohort.get("id") or ""),
            eligibility=flags,
        )


class CohortRegistry:
    """Cohort membership gate (§6, §7).

    The benchmark exists BETWEEN comparable results, not inside an
    individual organization (§7). The registry is the only path into a
    cohort's population: ineligible results cannot silently enter (§14).
    """

    def __init__(self, engine: Optional[BenchmarkEligibilityEngine] = None) -> None:
        self._engine = engine or BenchmarkEligibilityEngine()
        self._cohorts: dict[str, dict] = {}
        self._members: dict[str, list[dict]] = {}

    def register_cohort(self, cohort: Mapping[str, Any]) -> None:
        cid = cohort.get("id")
        if not cid:
            raise EligibilityError("cohort requires an id")
        self._cohorts[cid] = dict(cohort)
        self._members.setdefault(cid, [])

    def admit(
        self,
        result: Mapping[str, Any],
        cohort_id: str,
        subject_attributes: Optional[Mapping[str, Any]] = None,
        provisional_condition_id: Optional[str] = None,
        allow_provisional: bool = False,
    ) -> EligibilityDetermination:
        """Evaluate and, iff eligible, record membership.

        Returns the determination either way — the caller always receives
        the governed outcome, never a silent drop (§14).
        """
        cohort = self._cohorts.get(cohort_id)
        if cohort is None:
            raise EligibilityError(f"unknown cohort {cohort_id!r}")
        determination = self._engine.evaluate(
            result,
            cohort,
            subject_attributes=subject_attributes,
            provisional_condition_id=provisional_condition_id,
        )
        admitted = determination.status == EligibilityStatus.ELIGIBLE.value or (
            allow_provisional
            and determination.status == EligibilityStatus.PROVISIONAL.value
        )
        if admitted:
            ref = {
                "id": result.get("id"),
                "version": result.get("version"),
            }
            if ref not in self._members[cohort_id]:
                self._members[cohort_id].append(ref)
        return determination

    def population(self, cohort_id: str) -> list[dict]:
        if cohort_id not in self._cohorts:
            raise EligibilityError(f"unknown cohort {cohort_id!r}")
        return list(self._members[cohort_id])

    def meets_minimum_sample(self, cohort_id: str) -> bool:
        """A cohort below minimum sample size exists but produces no benchmark (§6)."""
        cohort = self._cohorts.get(cohort_id)
        if cohort is None:
            raise EligibilityError(f"unknown cohort {cohort_id!r}")
        return len(self._members[cohort_id]) >= cohort.get("minimum_sample_size", 1)
