"""Runtime conformance model (CR-9.10)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set


class ConformanceClass(str, Enum):
    """CR-9CL + CR-11AM — runtime conformance classes.

    The first seven are the CR-9.10 classes the reference runtime claims
    and exercises through the test suite. CR-11AM extends the vocabulary
    with the six *interoperability* conformance classes that an
    implementation can declare independently. They are deliberately
    explicit; adding a new class is a contract change, not a refactor.
    """

    # CR-9.10 runtime-surfaces.
    CORE = "Core"
    PROFILE = "Profile"
    API = "API"
    QUERY = "Query"
    VALIDATION = "Validation"
    PROVENANCE = "Provenance"
    SECURITY = "Security"
    # CR-11AM interoperability surfaces.
    EXCHANGE = "Exchange"            # can import/export OpenDEA exchanges
    IDENTITY = "Identity"            # can identify + reconcile external records
    MAPPING = "Mapping"              # can declare + validate mappings
    MAPPING_RUNTIME = "Runtime"      # can expose OpenDEA runtime APIs (interop)
    FEDERATION = "Federation"        # can interact with external authoritative sources
    AGENTIC = "Agentic"              # can expose governed semantic context to agents


# Endpoints/surfaces the public conformance suite deliberately does not
# exercise. Vendor-only or future/infer-only surfaces are recorded here so
# the suite owner has a single place to update when extending coverage.
EXCLUDED_ENDPOINTS = (
    "store.infer",
    "store.autonomous_mutate",
)


@dataclass(frozen=True)
class ConformanceSuite:
    """A named conformance suite and the classes it exercises."""

    name: str
    classes: List[ConformanceClass]
    description: str = ""

    def __post_init__(self):
        seen = set()
        for cls in self.classes:
            if cls in seen:
                raise ValueError(f"conformance suite {self.name!r} declares "
                                 f"{cls.value!r} twice")
            seen.add(cls)


@dataclass(frozen=True)
class ConformanceReport:
    """The aggregated conformance report for a runtime."""

    suites: List[ConformanceSuite]
    schema_version: str = "1.0.0"
    conformance_version: str = "cr-11am-1.0.0"
    runtime_version: str = "0.0.0"
    spec_version: str = "1.0.0"
    suite_count: int = field(init=False, default=0)
    classes_covered: Set[str] = field(init=False, default_factory=set)

    def __post_init__(self):
        object.__setattr__(self, "suite_count", len(self.suites))
        object.__setattr__(
            self, "classes_covered",
            sorted({cls.value for s in self.suites for cls in s.classes}))

    def as_dict(self) -> Dict[str, object]:
        return {
            "schemaVersion": self.schema_version,
            "conformanceVersion": self.conformance_version,
            "runtimeVersion": self.runtime_version,
            "specVersion": self.spec_version,
            "suiteCount": self.suite_count,
            "classesCovered": list(self.classes_covered),
            "suites": [
                {"name": s.name, "description": s.description,
                 "classes": [c.value for c in s.classes]}
                for s in self.suites
            ],
        }

    def render_json(self) -> str:
        """Render the report as a JSON string (CR-11AN report)."""
        import json
        return json.dumps(self.as_dict(), indent=2, sort_keys=True)

    def render_text(self) -> str:
        """Human-readable single-level text report (CR-11AN report).

        Matches the shape of standard conformance summaries so a CI log is
        immediately legible without parsing JSON.
        """
        out: List[str] = []
        out.append(f"OpenDEA Conformance Report")
        out.append(f"  conformance version : {self.conformance_version}")
        out.append(f"  runtime version     : {self.runtime_version}")
        out.append(f"  spec version        : {self.spec_version}")
        out.append(f"  suites              : {self.suite_count}")
        out.append(f"  classes covered     : "
                    f"{', '.join(self.classes_covered) or '(none)'}")
        for suite in self.suites:
            classes = ", ".join(c.value for c in suite.classes)
            out.append(f"  - {suite.name} [{classes}]")
            if suite.description:
                out.append(f"      {suite.description}")
        return "\n".join(out)

    @classmethod
    def build(cls, suites: List[ConformanceSuite],
              runtime_version: str = "0.0.0",
              spec_version: str = "1.0.0") -> "ConformanceReport":
        """Convenience builder stamping runtime + spec versions."""
        return cls(
            suites=suites,
            runtime_version=runtime_version,
            spec_version=spec_version,
        )
