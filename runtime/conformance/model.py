"""Runtime conformance model (CR-9.10)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set


class ConformanceClass(str, Enum):
    """CR-9CL: runtime conformance classes.

    These are the seven classes the reference runtime claims and exercises
    through the test suite. They are deliberately explicit; adding a new
    class is a contract change, not a refactor.
    """

    CORE = "Core"
    PROFILE = "Profile"
    API = "API"
    QUERY = "Query"
    VALIDATION = "Validation"
    PROVENANCE = "Provenance"
    SECURITY = "Security"


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
    suite_count: int = field(init=False, default=0)
    classes_covered: Set[str] = field(init=False, default_factory=set)

    def __post_init__(self):
        object.__setattr__(self, "suite_count", len(self.suites))
        object.__setattr__(
            self, "classes_covered",
            {cls.value for s in self.suites for cls in s.classes})

    def as_dict(self) -> Dict[str, object]:
        return {
            "schemaVersion": self.schema_version,
            "suiteCount": self.suite_count,
            "classesCovered": sorted(self.classes_covered),
            "suites": [
                {"name": s.name, "description": s.description,
                 "classes": [c.value for c in s.classes]}
                for s in self.suites
            ],
        }
