"""CR-11 Phase 1 — Semantic interoperability model.

The critical design principle (CR-11 §2):

    OpenDEA is the semantic contract; adapters absorb external complexity.

Four distinct concepts, never conflated (CR-11A):

- **Source** — an external system or artifact (:class:`ExternalSystem`)
- **Adapter** — the technical mechanism for accessing it
  (:class:`IntegrationAdapter`; connectors are transport, adapters are
  semantic integration — CR-11D)
- **Mapping** — semantic correspondence between external and OpenDEA
  concepts (:class:`SemanticMapping`)
- **Exchange** — the actual transfer of information (:class:`Exchange`)

Phase 1 scope (CR-11BJ): Namespace, ExternalSystem, ExternalIdentifier,
Adapter, Mapping, Exchange. Entity resolution, conflicts and authority
policies land in Phase 2; the exchange JSON format + JSON Schema in Phase 3.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from ..model.identity import is_canonical_id


class InteropError(Exception):
    """Base class for interoperability model violations."""


# ---------------------------------------------------------------- namespaces
class Namespace(str, Enum):
    """CR-11AS — formal namespaces prevent semantic collisions."""
    OPENDEA = "opendea"
    DMM = "dmm"
    AI = "ai"
    SECURITY = "security"
    INDUSTRY = "industry"
    EXTERNAL = "external"


def split_concept_ref(ref: str) -> tuple:
    """'external:ApplicationComponent' → ('external', 'ApplicationComponent')."""
    if ":" not in (ref or ""):
        raise InteropError(f"concept reference {ref!r} is not namespaced (CR-11AS)")
    ns, _, name = ref.partition(":")
    if not name:
        raise InteropError(f"concept reference {ref!r} has no concept name")
    return ns, name


# ------------------------------------------------------- enums / vocabularies
class AdapterCapability(str, Enum):
    """CR-11C — what an adapter can do."""
    READ = "READ"
    WRITE = "WRITE"
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"
    SYNC = "SYNC"
    EVENT = "EVENT"
    QUERY = "QUERY"
    BULK = "BULK"
    STREAM = "STREAM"


class MappingRelation(str, Enum):
    """CR-11F — external models rarely align one-to-one."""
    EQUIVALENT = "EQUIVALENT"
    SUBTYPE_OF = "SUBTYPE_OF"
    SUPERSET_OF = "SUPERSET_OF"
    MAPS_TO = "MAPS_TO"
    COMPOSES = "COMPOSES"
    SPLITS_INTO = "SPLITS_INTO"
    MERGES_FROM = "MERGES_FROM"
    RELATED_TO = "RELATED_TO"
    NO_CORRESPONDENCE = "NO_CORRESPONDENCE"


class MappingConfidence(str, Enum):
    """CR-11G — explicit semantic confidence prevents false precision."""
    EXACT = "Exact"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    UNCERTAIN = "Uncertain"


class Lossiness(str, Enum):
    """CR-11AQ — mappings MUST declare whether information is lost."""
    LOSSLESS = "LOSSLESS"
    PARTIAL = "PARTIAL"
    LOSSY = "LOSSY"
    UNKNOWN = "UNKNOWN"


class GovernanceStatus(str, Enum):
    """CR-11AU — lifecycle for governed assets (mappings, adapters…)."""
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"
    SUPERSEDED = "SUPERSEDED"


class ImportMode(str, Enum):
    """CR-11P."""
    FULL = "FULL_IMPORT"
    INCREMENTAL = "INCREMENTAL_IMPORT"
    DELTA = "DELTA_IMPORT"
    EVENT = "EVENT_IMPORT"
    ON_DEMAND = "ON_DEMAND_QUERY"


class SyncDirection(str, Enum):
    """CR-11Q — never assume synchronization is bidirectional."""
    ONE_WAY_IN = "ONE_WAY_IN"
    ONE_WAY_OUT = "ONE_WAY_OUT"
    BIDIRECTIONAL = "BIDIRECTIONAL"
    EVENT_DRIVEN = "EVENT_DRIVEN"
    PULL = "PULL"
    PUSH = "PUSH"


class EntityLocality(str, Enum):
    """CR-11AI — where the authoritative representation lives."""
    LOCAL = "LOCAL"
    FEDERATED = "FEDERATED"
    IMPORTED = "IMPORTED"
    DERIVED = "DERIVED"
    VIRTUAL = "VIRTUAL"


class IntegrationErrorCode(str, Enum):
    """CR-11AW — integration failures are explicit; failed records are never
    silently discarded."""
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    MAPPING_FAILED = "MAPPING_FAILED"
    IDENTITY_CONFLICT = "IDENTITY_CONFLICT"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    CONFLICT_DETECTED = "CONFLICT_DETECTED"
    PARTIAL_IMPORT = "PARTIAL_IMPORT"


# ------------------------------------------------------------------- concepts
@dataclass
class ExternalSystem:
    """CR-11B — an external system or artifact (a *Source*).

    ``authentication`` is a reference to a credential store entry — never a
    credential. Credentials MUST NOT exist in the metamodel (CR-11AY).
    """
    id: str
    name: str
    type: str  # ITSM, CMDB, EA_REPOSITORY, GRC, HR, DATA_CATALOG, …
    provider: str = ""
    version: str = ""
    endpoint: str = ""
    authentication: str = ""  # credential-store reference, NOT a secret
    classification: str = "INTERNAL"  # CR-11AZ
    owner: str = ""
    capabilities: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not is_canonical_id(self.id):
            raise InteropError(f"external system id {self.id!r} is not canonical")
        if self.authentication and any(
                tok in self.authentication.lower()
                for tok in ("pass", "secret", "key=", "bearer", "token")):
            raise InteropError(
                "authentication must be a credential-store reference, never a "
                "credential (CR-11AY)")

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in vars(self).items() if v not in (None, "", [])}


@dataclass
class IntegrationAdapter:
    """CR-11C/D — semantic integration mechanism bound to a Source.

    The adapter is semantic (ServiceNow → OpenDEA); the *connector* is the
    transport (protocol). Keeping these distinct prevents integration
    architecture from being confused with semantic interoperability.
    """
    id: str
    name: str
    source: str  # ExternalSystem id
    protocol: str  # connector: REST | GraphQL | SQL | SFTP | Kafka | Webhook | File
    format: str = "json"
    capabilities: List[AdapterCapability] = field(default_factory=list)
    version: str = "1.0.0"
    status: GovernanceStatus = GovernanceStatus.ACTIVE

    def __post_init__(self):
        if not is_canonical_id(self.id):
            raise InteropError(f"adapter id {self.id!r} is not canonical")
        self.capabilities = [AdapterCapability(c) for c in self.capabilities]
        self.status = GovernanceStatus(self.status)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "source": self.source,
            "protocol": self.protocol, "format": self.format,
            "capabilities": [c.value for c in self.capabilities],
            "version": self.version, "status": self.status.value,
        }


@dataclass
class SemanticMapping:
    """CR-11E — first-class semantic correspondence.

    Mappings are governed assets (CR-11AT): they carry owner, version, status,
    approval and dates because a mapping change materially alters enterprise
    meaning. Lossiness (CR-11AQ) is declared, never discovered by surprise.
    """
    source_concept: str  # namespaced, e.g. "external:ApplicationComponent"
    target_concept: str  # namespaced, e.g. "opendea:ApplicationComponent"
    relationship: MappingRelation = MappingRelation.MAPS_TO
    transformation: str = ""  # explicit, testable rule (CR-11H)
    confidence: MappingConfidence = MappingConfidence.UNCERTAIN
    lossiness: Lossiness = Lossiness.UNKNOWN
    owner: str = ""
    version: str = "1.0.0"
    status: GovernanceStatus = GovernanceStatus.ACTIVE
    approved_by: str = ""
    effective_date: str = ""
    deprecation_date: str = ""
    superseded_by: str = ""  # CR-11AU replacement reference

    def __post_init__(self):
        self.relationship = MappingRelation(self.relationship)
        self.confidence = MappingConfidence(self.confidence)
        self.lossiness = Lossiness(self.lossiness)
        self.status = GovernanceStatus(self.status)
        for ref in (self.source_concept, self.target_concept):
            split_concept_ref(ref)
        if self.status == GovernanceStatus.SUPERSEDED and not self.superseded_by:
            raise InteropError(
                "SUPERSEDED mappings require a replacement reference (CR-11AU)")

    def as_dict(self) -> Dict[str, Any]:
        d = {
            "sourceConcept": self.source_concept,
            "targetConcept": self.target_concept,
            "relationship": self.relationship.value,
            "confidence": self.confidence.value,
            "lossiness": self.lossiness.value,
            "owner": self.owner, "version": self.version,
            "status": self.status.value,
        }
        for k, v in {"transformation": self.transformation,
                     "approvedBy": self.approved_by,
                     "effectiveDate": self.effective_date,
                     "deprecationDate": self.deprecation_date,
                     "supersededBy": self.superseded_by}.items():
            if v:
                d[k] = v
        return d


@dataclass
class ExternalIdentifier:
    """CR-11I — the bridge between an external record and an OpenDEA entity.

    An external system's identifier is NEVER the OpenDEA canonical identity by
    default; this object preserves the correlation across time.
    """
    system: str          # ExternalSystem id
    identifier: str      # the external record's id
    entity: str          # OpenDEA canonical entity id
    identifier_type: str = "primary"  # primary | alternate | legacy
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in {
            "system": self.system, "identifier": self.identifier,
            "identifierType": self.identifier_type, "entity": self.entity,
            "validFrom": self.valid_from, "validTo": self.valid_to,
        }.items() if v is not None}


@dataclass
class Extension:
    """CR-11AR — external concepts with no OpenDEA correspondence are
    preserved as extensions in their own namespace, never discarded and never
    absorbed into the Core."""
    namespace: str  # MUST NOT be "opendea" — extensions stay external
    name: str
    version: str = "1.0.0"
    definition: str = ""
    source: str = ""  # ExternalSystem id

    def __post_init__(self):
        if self.namespace == Namespace.OPENDEA.value:
            raise InteropError(
                "extensions must not use the opendea: namespace — the Core is "
                "not extended from outside (CR-11AR/AS, CR-11 §66)")
        if not self.namespace:
            raise InteropError("extensions require a namespace (CR-11AS)")

    @property
    def ref(self) -> str:
        return f"{self.namespace}:{self.name}"

    def as_dict(self) -> Dict[str, Any]:
        return {"namespace": self.namespace, "name": self.name,
                "version": self.version, "definition": self.definition,
                "source": self.source}


@dataclass
class Exchange:
    """CR-11S/V — the standard exchange envelope.

    Every exchange declares its schema/profile/mapping versions (CR-11V) so a
    receiver can always interpret the payload. The payload is a *canonical
    serialization* of OpenDEA semantics (entities, relationships, assertions,
    evidence, state, scenarios, decisions) — never a dump of an internal
    storage schema (CR-11U).
    """
    id: str
    source: str  # ExternalSystem id or "opendea"
    target: str  # ExternalSystem id or "opendea"
    operation: ImportMode  # import/export mode (CR-11P)
    payload: Dict[str, Any]
    schema_version: str = "1.0.0"
    profile_versions: Dict[str, str] = field(default_factory=dict)
    mapping_version: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        self.operation = ImportMode(self.operation)
        if not self.schema_version:
            raise InteropError("exchanges must declare schemaVersion (CR-11V)")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "exchange": {
                "id": self.id, "source": self.source, "target": self.target,
                "timestamp": self.timestamp,
                "schemaVersion": self.schema_version,
                "profileVersions": self.profile_versions,
                "mappingVersion": self.mapping_version,
                "operation": self.operation.value,
                "payload": self.payload,
                "provenance": self.provenance,
            }
        }
